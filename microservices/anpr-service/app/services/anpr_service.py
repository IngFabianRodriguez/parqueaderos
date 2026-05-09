"""ANPR Service — business logic and integrations."""
import json
from datetime import datetime

from sqlalchemy import select

from app.config import get_settings
from app.db.models import ANPRCamera, PlateDetection
from app.db.session import get_session_factory

settings = get_settings()


# ── Kafka Consumer (placeholder) ─────────────────────────────────────────────
# TODO: RF-016 — Consume from "anpr.plate-detected" topic (produced by infer endpoint)
#
# from aiokafka import AIOKafkaConsumer
#
# class KafkaANPRConsumer:
#     def __init__(self):
#         self.consumer: AIOKafkaConsumer | None = None
#
#     async def start(self):
#         self.consumer = AIOKafkaConsumer(
#             "anpr.plate-detected",
#             bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
#             group_id=settings.KAFKA_CONSUMER_GROUP,
#             auto_offset_reset="earliest",
#         )
#         await self.consumer.start()
#
#     async def consume(self):
#         async for msg in self.consumer:
#             event = json.loads(msg.value)
#             await self._process_detection_event(event)
#
#     async def _process_detection_event(self, event: dict):
#         # Write to plate_detections table, trigger notification matching
#         pass
#
#     async def stop(self):
#         if self.consumer:
#             await self.consumer.stop()
#
#
# kafka_consumer = KafkaANPRConsumer()


# ── OCR Engine (placeholder) ─────────────────────────────────────────────────
# TODO: RF-017 — Replace with LPRNet / ONNX inference
#
# import numpy as np
# from PIL import Image
# import onnxruntime as ort
#
# class LPREngine:
#     """License Plate Recognition ONNX engine."""
#
#     def __init__(self, model_path: str):
#         self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
#         self.input_name = self.session.get_inputs()[0].name
#         self.output_name = self.session.get_outputs()[0].name
#
#     def predict(self, image_bytes: bytes) -> tuple[str, float]:
#         """
#         Run inference on raw image bytes.
#         Returns (plate_number, confidence).
#         """
#         import numpy as np
#         from PIL import Image
#         import io
#
#         img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#         img = img.resize((settings.LPR_IMAGE_WIDTH, settings.LPR_IMAGE_HEIGHT))
#         img_array = np.array(img, dtype=np.float32) / 255.0
#         img_array = img_array.transpose(2, 0, 1)[np.newaxis, ...]
#
#         output = self.session.run([self.output_name], {self.input_name: img_array})[0]
#         # Post-process output → plate string
#         plate = self._decode_output(output)
#         confidence = float(output.max())
#         return plate, confidence
#
#     def _decode_output(self, output):
#         # CTC decode / argmax over output sequence
#         return "ABC123"


async def match_reservation(plate_number: str, tenant_id, sede_id: str) -> str | None:
    """
    Match a detected plate against active reservations.

    TODO: RF-017 — query reservations table for matching plate + sede
    Returns reservation_id if match found, else None.
    """
    return None


async def get_detection_stats(camera_id: str, tenant_id, hours: int = 24):
    """Get detection statistics for a camera."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        from datetime import timedelta

        since = datetime.utcnow() - timedelta(hours=hours)
        result = await session.execute(
            select(PlateDetection).where(
                PlateDetection.camera_id == camera_id,
                PlateDetection.tenant_id == tenant_id,
                PlateDetection.timestamp >= since,
            )
        )
        detections = result.scalars().all()

        total = len(detections)
        avg_confidence = sum(d.confidence for d in detections) / total if total else 0.0
        entry_count = sum(1 for d in detections if d.detection_type == "entry")
        exit_count = sum(1 for d in detections if d.detection_type == "exit")

        return {
            "total_detections": total,
            "avg_confidence": round(avg_confidence, 3),
            "entries": entry_count,
            "exits": exit_count,
        }