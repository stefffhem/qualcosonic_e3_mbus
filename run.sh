#!/usr/bin/env bash
SERIAL_DEVICE="${SERIAL_DEVICE:-/dev/ttyUSB0}"
BAUDRATE="${BAUDRATE:-2400}"
MQTT_BROKER="${MQTT_BROKER:-core-mosquitto}"
MQTT_PORT="${MQTT_PORT:-1883}"
MQTT_USER="${MQTT_USER:-}"
MQTT_PASSWORD="${MQTT_PASSWORD:-}"
MQTT_TOPIC_PREFIX="${MQTT_TOPIC_PREFIX:-homeassistant/sensor/qualcosonic_e3}"
POLL_INTERVAL="${POLL_INTERVAL:-60}"
MQTT_DISCOVERY="${MQTT_DISCOVERY:-true}"
DISCOVERY_PREFIX="${DISCOVERY_PREFIX:-homeassistant}"

echo "Starting Qualcosonic E3 M-Bus reader..."
exec python3 /app/qualcosonic_mbus_reader.py \
  --device "$SERIAL_DEVICE" \
  --baud "$BAUDRATE" \
  --mqtt "$MQTT_BROKER" \
  --port "$MQTT_PORT" \
  --user "$MQTT_USER" \
  --password "$MQTT_PASSWORD" \
  --topic-prefix "$MQTT_TOPIC_PREFIX" \
  --poll-interval "$POLL_INTERVAL" \
  --mqtt-discovery "$MQTT_DISCOVERY" \
  --discovery-prefix "$DISCOVERY_PREFIX"

