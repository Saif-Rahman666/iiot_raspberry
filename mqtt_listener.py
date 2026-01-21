import json
import paho.mqtt.client as mqtt
from inference_tflite import predict_step
import RPi.GPIO as GPIO # 1. Import GPIO

# --- IR Sensor Setup ---
IR_PIN = 17 
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_PIN, GPIO.IN)

BROKER = "localhost"
PORT = 1883
TOPIC = "engine/#"
AE_SENSORS = ["s2", "s3", "s4", "s7", "s11", "s12", "s15"]

# Store the latest physical values globally
latest_prox = 0
latest_lux = 0.0

def on_connect(client, userdata, flags, rc):
    print("✅ MQTT connected:", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global latest_prox,latest_lux
    try:    
        data = json.loads(msg.payload.decode())

        # 1. Capture physical data and save it
        if "physical" in msg.topic:
            latest_prox = data.get("prox_raw", 0)
            latest_lux = data.get("lux", 0.0)
            return
        # 2. Process engine data through AI
        if "sensors" in msg.topic:
            unit = int(data["unit"])
            sensors = {s: float(data.get(s, 0.0)) for s in AE_SENSORS}
        
            result = predict_step(unit, sensors)    
    
        # 3. DATA FUSION & OVERRIDE
        # Use AI results as baseline, but override if sensor is touched
            health = float(result.get("health_index", 0.0))
            raw_rul = int(result.get("predicted_rul") or result.get("rul") or 0)
            status = "CLEAR"

            if latest_prox > 3000:  # Your threshold for touching the sensor
                health = 0.01
                raw_rul = 1             # Force low RUL on failure
                status = "CRITICAL"
            #light failure check    
            elif latest_lux < 1.0:
                status = "CRITICAL: LIGHT FAILURE"
        
        # --- THE CRITICAL FIX FOR RUL ---
        # Models often return 'predicted_rul' or 'rul'. We check both.
        #raw_rul = result.get("predicted_rul") or result.get("rul") or 0
        
            final_payload = {
                "unit": unit,
                "health_index": float(result.get("health_index", 0.0)),
                "rul": int(raw_rul), # Flutter expects an int for 'Predicted RUL'
                "prox_raw": latest_prox, 
                "lux": latest_lux,
                "ir_status": status
            }
        
            PRED_TOPIC = f"engine/{unit}/status"
            client.publish(PRED_TOPIC, json.dumps(final_payload))
            print(f" Fused Data Sent: Health={final_payload['health_index']:.2f}, RUL={final_payload['rul']}", f" (Prox={latest_prox}), Lux={latest_lux:.1f}, Status={status}")

    except Exception as e:
        print("Error in AI Fuser:", e)

# Use the API Version fix we discussed earlier
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_forever()