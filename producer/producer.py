import os
import time
import logging
from typing import Optional, List

import cv2
from kafka import KafkaProducer
from kafka.errors import KafkaError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rtsp-producer")

FRAME_LOG_INTERVAL = 50
RECONNECT_DELAY_SEC = 5


def _create_producer(bootstrap_servers: str) -> KafkaProducer:
    servers = [s.strip() for s in bootstrap_servers.split(",") if s.strip()]
    logger.info("Connecting to Kafka at %s", servers)
    return KafkaProducer(
        bootstrap_servers=servers,
        value_serializer=lambda v: v,
        key_serializer=lambda k: k.encode("utf-8"),
        linger_ms=5,
        security_protocol="SSL",
        ssl_cafile="/etc/ssl/certs/ca-certificates.crt",
    )



def _open_rtsp(rtsp_url: str) -> Optional[cv2.VideoCapture]:
  cap = cv2.VideoCapture(rtsp_url)
  if not cap.isOpened():
    logger.error("Unable to open RTSP stream: %s", rtsp_url)
    return None
  return cap


def stream_frames():
  bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
  topic = os.environ.get("KAFKA_TOPIC", "video-stream-1")
  rtsp_url = os.environ.get("RTSP_URL")

  if not rtsp_url:
    raise RuntimeError("RTSP_URL environment variable must be set")

  producer = _create_producer(bootstrap_servers)
  frame_id = 0

  while True:
    cap = _open_rtsp(rtsp_url)
    if cap is None:
      logger.info("Retrying RTSP connection in %s seconds", RECONNECT_DELAY_SEC)
      time.sleep(RECONNECT_DELAY_SEC)
      continue

    try:
      while True:
        ret, frame = cap.read()
        if not ret:
          logger.warning("Frame read failed. Reconnecting...")
          break

        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
          logger.warning("JPEG encoding failed for frame %s", frame_id)
          continue

        try:
          producer.send(topic, key=str(frame_id), value=buffer.tobytes())
        except KafkaError as err:
          logger.exception("Kafka send failed: %s", err)
          time.sleep(RECONNECT_DELAY_SEC)
          break

        if frame_id % FRAME_LOG_INTERVAL == 0:
          logger.info("Produced frame %s", frame_id)

        frame_id += 1

      cap.release()
      time.sleep(RECONNECT_DELAY_SEC)

    except KeyboardInterrupt:
      logger.info("Interrupted by user, closing")
      break

  producer.flush()
  producer.close()


if __name__ == "__main__":
  stream_frames()
