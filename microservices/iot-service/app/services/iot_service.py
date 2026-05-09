"""IoT Service — business logic and integrations."""
from app.config import get_settings
from app.db.session import get_session_factory
from app.db.models import IoTEvent

settings = get_settings()


# ── MQTT Integration (placeholder) ────────────────────────────────────────────
# TODO: RF-008 — Connect to MQTT broker and subscribe to device topics
#
# import paho.mqtt.client as mqtt
#
# class MQTTClient:
#     def __init__(self):
#         self.client = mqtt.Client(client_id="iot-service")
#         self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
#         self.client.on_connect = self._on_connect
#         self.client.on_message = self._on_message
#
#     def connect(self):
#         self.client.connect(
#             settings.MQTT_BROKER_URL.replace("mqtt://", "").rstrip("/"),
#             port=1883,
#         )
#         self.client.loop_start()
#
#     def _on_connect(self, client, userdata, flags, rc):
#         if rc == 0:
#             client.subscribe(f"{settings.MQTT_TOPIC_PREFIX}/+/events")
#         else:
#             print(f"MQTT connection failed with code {rc}")
#
#     def _on_message(self, client, userdata, msg):
#         # Parse message, write IoTEvent to DB, publish to Kafka
#         pass


# ── Kafka Integration (placeholder) ─────────────────────────────────────────
# TODO: RF-009 — Publish IoT events to Kafka topic "iot.events"
#
# from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
#
# class KafkaEventPublisher:
#     def __init__(self):
#         self.producer: AIOKafkaProducer | None = None
#
#     async def start(self):
#         self.producer = AIOKafkaProducer(
#             bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
#             client_id="iot-service-producer",
#         )
#         await self.producer.start()
#
#     async def stop(self):
#         if self.producer:
#             await self.producer.stop()
#
#     async def publish_event(self, event: IoTEvent):
#         import json
#         from datetime import datetime
#
#         await self.producer.send(
#             "iot.events",
#             key=str(event.id).encode(),
#             value=json.dumps({
#                 "id": str(event.id),
#                 "tenant_id": str(event.tenant_id),
#                 "device_id": str(event.device_id),
#                 "event_type": event.event_type,
#                 "payload": event.payload,
#                 "confidence": event.confidence,
#                 "timestamp": event.timestamp.isoformat(),
#             }).encode(),
#         )
#
#
# kafka_publisher = KafkaEventPublisher()


async def process_mqtt_event(device_serial: str, payload: dict) -> None:
    """
    Process an event received via MQTT.

    TODO: RF-008 — integrate with MQTT subscriber
    1. Lookup device by serial_number
    2. Write IoTEvent to DB
    3. Publish to Kafka via kafka_publisher
    """
    pass


async def get_recent_events(device_id: str, limit: int = 50):
    """Get recent events for a device."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        from sqlalchemy import select

        result = await session.execute(
            select(IoTEvent)
            .where(IoTEvent.device_id == device_id)
            .order_by(IoTEvent.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()