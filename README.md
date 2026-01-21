IIoT-ML: Industrial IoT Edge Computing on Raspberry Pi
This repository contains the Raspberry Pi implementation of the IIoT-ML system. It is designed for Edge Computing, allowing for real-time sensor data collection, local machine learning inference, and industrial communication via MQTT.

🚀 Overview
By moving the ML inference to the "Edge" (the Raspberry Pi), this project reduces latency and bandwidth usage, which is essential for predictive maintenance in factory settings.

Key Features

Edge Intelligence: Local execution of ML models for immediate fault detection.

Hardware Integration: Direct interfacing with industrial sensors via Raspberry Pi GPIO.

MQTT Bridge: Acts as a gateway between local sensor clusters and the central cloud/broker.

Persistent Monitoring: Systemd service integration for 24/7 industrial uptime.

🛠 Hardware Requirements
Device: Raspberry Pi 3B+ / 4B / 5

Operating System: Raspberry Pi OS (64-bit recommended for TensorFlow Lite)

Sensors: Compatible with I2C, SPI, or Analog (via ADC)

Storage: 16GB+ MicroSD card (Class 10 recommended)

⚙️ Installation
Clone the repository:

Bash
git clone https://github.com/Saif-Rahman666/iiot_raspberry.git
cd iiot_raspberry
Run the Setup Script: This will install system-level dependencies for ML (like libatlas-base-dev):

Bash
sudo apt-get update
sudo apt-get install -y libatlas-base-dev
Install Python Dependencies:

Bash
pip install -r requirements.txt
🚦 Usage
1. Configure your Pins

Edit config.yaml to map your GPIO pins to the corresponding sensor inputs (Temperature, Vibration, etc.).

2. Start the Edge Service

Run the main collector and inference engine:

Bash
python3 main.py
3. Deploy as a Background Service

To ensure the project runs automatically on boot:

Bash
sudo cp iiot_service.service /etc/systemd/system/
sudo systemctl enable iiot_service
sudo systemctl start iiot_service
📂 Project Structure
Plaintext
├── iiot_raspberry/
│   ├── main.py              # Main execution loop (Edge Inference)
│   ├── sensors/             # Hardware interface drivers
│   ├── models/              # Compressed TFLite models for Pi
│   ├── config.yaml          # Device and MQTT settings
│   └── requirements.txt     # Pi-specific dependencies
└── README.md
📝 License
Distributed under the MIT License.