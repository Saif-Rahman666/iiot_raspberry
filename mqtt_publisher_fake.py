import json
import time
import paho.mqtt.client as mqtt

#BROKER = "172.20.10.5"
#BROKER = "192.168.0.202"
BROKER = "localhost"
PORT = 1883
TOPIC = "engine/1/sensors"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)
client.loop_start()

print("📤 Degrading MQTT publisher started")

cycle = 0

while True:
    cycle += 1
    
    payload = {
    "unit": 1,
    "s2": 642.0 - (0.001 * cycle), # Slowly degrading
    "s3": 1585.0 - (0.1 * cycle),
    "s4": 1405.0 + (0.1 * cycle),
    "s7": 553.0 - (0.05 * cycle),
    "s11": 47.0 + (0.01 * cycle),
    "s12": 521.0 - (0.05 * cycle),
    "s15": 8.4 + (0.001 * cycle)
}
    client.publish(TOPIC, json.dumps(payload))
    print("➡️ Sent:", payload)

    time.sleep(2)
