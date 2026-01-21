import RPi.GPIO as GPIO
import time

IR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_PIN, GPIO.IN)

print("🔍 IR Sensor Test (Ctrl+C to stop)...")
try:
    while True:
        
        if GPIO.input(IR_PIN) == GPIO.LOW:
            print(" DETECTED!")
        else:
            print("... Clear")
        time.sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()
