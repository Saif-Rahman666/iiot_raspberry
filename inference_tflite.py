import fix_imp  
import os
import tensorflow as tf
import numpy as np
import pandas as pd
import joblib
from collections import deque
from datetime import datetime



def load_tflite(path):
    
    interpreter = tf.lite.Interpreter(model_path=path)
    interpreter.allocate_tensors()
    return interpreter

# CONFIG
SEQ_LEN = 30
RUL_CAP = 80
AE_SENSORS = ["s2", "s3", "s4", "s7", "s11", "s12", "s15"]
FEATURES = ["health_index"] + AE_SENSORS


print("Loading Autoencoder...")
ae_interp = load_tflite("models/autoencoder.tflite")
print("Loading LSTM (with Flex support)...")
lstm_interp = load_tflite("models/lstm_rul.tflite")

# --- LOAD SCALERS ---
ae_scaler = joblib.load("models/ae_scaler.pkl")
lstm_scaler = joblib.load("models/lstm_scaler.pkl")

engine_buffers = {}

def run_inference(interpreter, input_data):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_tensor(input_details[0]['index'], input_data.astype(np.float32))
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])

def predict_step(unit_id: int, sensor_row: dict):
    if unit_id not in engine_buffers:
        engine_buffers[unit_id] = deque(maxlen=SEQ_LEN)

    # 1. Health Index Calculation
    ae_input = pd.DataFrame([[sensor_row[s] for s in AE_SENSORS]], columns=AE_SENSORS)
    ae_scaled = ae_scaler.transform(ae_input) 
    recon = run_inference(ae_interp, ae_scaled)
    mse = np.mean((ae_scaled - recon) ** 2)
    threshold = 0.05 
    health_index = float(np.clip(1.0 - (mse / threshold), 0.01, 1.0))

    # 2. LSTM Data Prep
    row = {"health_index": health_index}
    for s in AE_SENSORS:
        row[s] = sensor_row[s]
    row_scaled = lstm_scaler.transform(pd.DataFrame([row], columns=FEATURES))
    engine_buffers[unit_id].append(row_scaled[0])

    if len(engine_buffers[unit_id]) < SEQ_LEN:
        return {"unit": unit_id, "health_index": round(health_index, 3), "risk": "WARMING_UP"}

    # 3. Predicted RUL
    X = np.array(engine_buffers[unit_id]).reshape(1, SEQ_LEN, len(FEATURES))
    rul_norm = run_inference(lstm_interp, X)[0][0]
    predicted_rul = int(np.clip(rul_norm * RUL_CAP, 1, RUL_CAP))

    return {
        "unit": unit_id,
        "health_index": round(health_index, 3),
        "predicted_rul": predicted_rul,
        "risk": "CRITICAL" if predicted_rul < 20 else "HIGH" if predicted_rul < 40 else "MEDIUM",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }