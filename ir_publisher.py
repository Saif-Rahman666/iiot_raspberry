import time
import json
import paho.mqtt.client as mqtt
import board
import busio
import adafruit_vcnl4010

# --- CONFIG ---
BROKER_IP = "localhost"
TOPIC = "engine/1/physical"
THRESHOLD = 3000 

# --- I2C SENSOR SETUP ---
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_vcnl4010.VCNL4010(i2c)
    print(" VCNL4010 detected over I2C")
except Exception as e:
    print(f" Failed to find sensor: {e}")
    exit()

# --- MQTT SETUP ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect(BROKER_IP, 1883, 60)

print(" IIOT VCNL4010 Publisher LIVE")

try:
    while True:
        proximity = sensor.proximity
        lux = sensor.ambient_lux

        # RISK CALCULATION
        # 1.0 = High Stress (Anomaly), 0.0 = Normal
        is_blocked = proximity > THRESHOLD
        ai_stress_signal = 1.0 if is_blocked else 0.0
        risk_label = "CRITICAL" if is_blocked else "CLEAR"

        payload = {
            "unit": 1,
            "prox_raw": proximity,
            "lux": round(float(lux), 2),
            "ir_status": risk_label,
        }
        
        client.publish(TOPIC, json.dumps(payload))
        print(f" Prox: {proximity} | Lux: {lux:.1f}| Status: {risk_label}")
        
        time.sleep(0.5) 
except KeyboardInterrupt:
    print("\nStopping...")