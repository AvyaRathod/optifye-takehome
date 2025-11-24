import base64
import io
import json
import os
import logging
from typing import List

import boto3
import requests
from kafka import KafkaConsumer
from kafka.structs import TopicPartition

from postprocess import annotate

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("consumer")

BATCH_SIZE = 25


def _init_consumer(bootstrap_servers: str, topic: str) -> KafkaConsumer:
    servers = [s.strip() for s in bootstrap_servers.split(",") if s.strip()]
    logger.info(f"Connecting to Kafka brokers: {servers}")
    group_id = os.getenv("KAFKA_GROUP_ID", "video-consumer-group")

    consumer = KafkaConsumer(
        topic,
        group_id=group_id,
        bootstrap_servers=servers,
        security_protocol="SSL",
        ssl_cafile="/etc/ssl/certs/ca-certificates.crt",
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )
    logger.info("KafkaConsumer created, starting to poll messages")
    return consumer


def _invoke_inference(inference_url: str, payload: dict) -> dict:
    response = requests.post(inference_url, json=payload)
    response.raise_for_status()
    return response.json()


def _upload_to_s3(bucket: str, key: str, body: bytes):
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType="image/jpeg")


def run():
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.environ.get("KAFKA_TOPIC", "video-stream-1")
    bucket = os.environ.get("S3_BUCKET_NAME")
    inference_url = os.environ.get("INFERENCE_URL", "http://localhost:8000/infer")

    if not bucket:
        raise RuntimeError("S3_BUCKET_NAME must be set")

    consumer = _init_consumer(bootstrap_servers, topic)
    batch = []

    logger.info("Starting consumer loop for topic %s", topic)

    for message in consumer:
        frame_id = message.key.decode("utf-8")
        frame_bytes = message.value
        batch.append({
            "id": frame_id,
            "image_b64": base64.b64encode(frame_bytes).decode("utf-8"),
            "raw": frame_bytes,
        })

        if len(batch) < BATCH_SIZE:
            continue

        payload = {
            "frames": [{"id": item["id"], "image_b64": item["image_b64"]} for item in batch]
        }

        try:
            response = _invoke_inference(inference_url, payload)
            results = response.get("results", {})

            target_frame = batch[len(batch) // 2]
            detections = results.get(target_frame["id"], {})
            annotated = annotate(target_frame["raw"], detections)

            key = f"stream1/frame_{target_frame['id']}.jpg"
            _upload_to_s3(bucket, key, annotated)
            logger.info("Uploaded annotated frame %s for batch", target_frame["id"])
        except Exception as err:
            logger.exception("Batch processing failed: %s", err)
        finally:
            batch.clear()


if __name__ == "__main__":
    run()
