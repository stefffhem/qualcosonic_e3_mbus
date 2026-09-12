#!/usr/bin/env python3
import argparse
import serial
import time
import json
import logging
import sys
import paho.mqtt.client as mqtt

# pymbus imports (API je nach Version)
from pymbus import MBusFrame, MBusParser, MBusMaster  # names illustrative; prüfen je nach pymbus-Version

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qualcosonic_mbus")

def publish_discovery(client, prefix, sensor_id, name, unit, state_topic, discovery_prefix="homeassistant"):
    cfg_topic = f"{discovery_prefix}/sensor/{sensor_id}/config"
    payload = {
        "name": name,
        "state_topic": state_topic,
        "unit_of_measurement": unit,
        "value_template": "{{ value_json.value }}",
        "unique_id": sensor_id
    }
    client.publish(cfg_topic, json.dumps(payload), qos=1, retain=True)
    logger.info("Published discovery %s -> %s", cfg_topic, payload)

def publish_values(client, topic_prefix, values):
    ts = int(time.time())
    for k, v in values.items():
        topic = f"{topic_prefix}/{k}"
        payload = {"value": v, "timestamp": ts}
        client.publish(topic, json.dumps(payload), qos=1, retain=False)
        logger.info("Published %s -> %s", topic, payload)

def decode_mbus_data(record_bytes):
    """
    Nutze pymbus Parser / helpers, um DIF/DTF Datensätze zu dekodieren.
    Diese Funktion ist ein Wrapper; genaue API hängt von pymbus-Version ab.
    """
    # Beispiel: MBusParser.decode_data(record_bytes) -> dict
    try:
        parsed = MBusParser.parse_data(record_bytes)  # pseudocode: anpassen
        return parsed
    except Exception as e:
        logger.exception("Fehler beim Dekodieren der M-Bus Daten: %s", e)
        return {}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=2400)
    parser.add_argument("--mqtt", default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--topic-prefix", default="homeassistant/sensor/qualcosonic_e3")
    parser.add_argument("--poll-interval", type=int, default=60)
    parser.add_argument("--mqtt-discovery", default="true")
    parser.add_argument("--discovery-prefix", default="homeassistant")
    args = parser.parse_args()

    # MQTT
    client = mqtt.Client()
    if args.user:
        client.username_pw_set(args.user, args.password)
    client.connect(args.mqtt, args.port, 60)
    client.loop_start()

    # Serial
    try:
        ser = serial.Serial(args.device, args.baud, timeout=1)
    except Exception as e:
        logger.error("Cannot open serial device %s: %s", args.device, e)
        sys.exit(1)

    logger.info("Listening on %s @ %d", args.device, args.baud)

    buffer = bytearray()
    parser = MBusParser()  # pseudocode: tatsächliche Initialisierung prüfen

    # Optional: publish static discovery for expected sensors
    if args.mqtt_discovery.lower() in ("true", "1", "yes"):
        publish_discovery(client, args.topic_prefix, "qualcosonic_energy", "Qualcosonic Energy", "kWh", f"{args.topic_prefix}/energy", args.discovery_prefix)
        publish_discovery(client, args.topic_prefix, "qualcosonic_power", "Qualcosonic Power", "W", f"{args.topic_prefix}/power", args.discovery_prefix)
        publish_discovery(client, args.topic_prefix, "qualcosonic_temp", "Qualcosonic Temperature", "°C", f"{args.topic_prefix}/temp", args.discovery_prefix)

    while True:
        try:
            data = ser.read(256)
            if data:
                buffer.extend(data)
                # feed buffer to pymbus parser which yields frames when complete
                frames, consumed = parser.feed(buffer)  # pseudocode: parser.feed returns (frames, bytes_consumed)
                # remove consumed bytes
                if consumed:
                    del buffer[:consumed]
                for frame in frames:
                    # frame is an MBusFrame object (pymbus)
                    # extract APDU / data records
                    try:
                        # Depending on pymbus API:
                        # records = frame.get_records()
                        records = frame.records  # pseudocode
                        values = {}
                        for rec in records:
                            # rec might have fields: function, unit, value, id
                            # map known DIFs to friendly keys
                            key = rec.get("id", rec.get("name", "unknown"))
                            values[key] = rec.get("value")
                        if values:
                            publish_values(client, args.topic_prefix, values)
                    except Exception as e:
                        logger.exception("Error processing frame: %s", e)
            else:
                # kein Daten, evtl. Polling senden falls nötig
                time.sleep(0.1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.exception("Fehler in Lese‑Loop: %s", e)
            time.sleep(5)

    client.loop_stop()
    client.disconnect()
    ser.close()

if __name__ == "__main__":
    main()

