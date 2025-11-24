## Architecture Overview

RTSP video source (Docker RTSP server on EC2) → Kafka producer (frame extraction) → Amazon MSK topic → Kafka consumer running in EKS → FastAPI inference service in EKS → Annotated frames uploaded to S3 for verification.
