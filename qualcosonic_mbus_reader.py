import mbus
import serial
import json
import time
import paho.mqtt.client as mqtt

def read_mbus_frame(device):
    handle = mbus.mbus_context_serial(device)
    mbus.mbus_connect(handle)

    frame = mbus.mbus_recv_frame(handle)
    mbus.mbus_disconnect(handle)

    return frame

def decode_mbus(frame):
    data = mbus.mbus_frame_data_parse(frame)
    records = mbus.mbus_data_record_decode(data)

    result = {}
    for r in records:
        if r.value is not None:
            key = r.id or r.unit or "unknown"
            result[key] = r.value

    return result
