#!/bin/bash

# Navigate to project folder
cd ~/iiot_project

# Activate the virtual environment
source ~/iiot_project/iiot_env/bin/activate

echo "🚀 [ Starting the Engine Simulation (NASA Data)..."
# Run the publisher in the background (&)
python3 mqtt_publisher_fake.py &
PUB_PID=$!

echo " Starting the ML (Autoencoder + LSTM)..."
# Run the listener (this will stay in the foreground so you can see logs)
python3 mqtt_listener.py

echo " Starting Physical IR Sensor Publisher..."
python3 ir_publisher.py &

# Function to kill all background processes when you exit
cleanup() {
    echo -e "\n🛑 [IIoT Master] Shutting down all processes..."
    pkill -P $$  # Kills all child processes of this script
    exit
}

# Trap Ctrl+C (SIGINT) and run the cleanup function
trap cleanup SIGINT
# Keep the script alive so the trap can work
wait
