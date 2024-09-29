# micLucy 
LUCY Voice Assistant
Language Understanding Companion for You

Table of Contents
Introduction
Project Overview
Prerequisites
Installation
1. Setting Up the Raspberry Pi
2. Installing System Dependencies
3. Setting Up the Python Virtual Environment
4. Cloning the Repository
5. Installing Python Dependencies
6. Downloading Models
Configuration
1. Picovoice Access Key and Hotword Model
2. Vosk Speech-to-Text Model
3. Setting Audio Device Indices
4. Configuring the Server URI
Running the Application
1. Testing the Application Manually
2. Running as a Service
Testing
1. Verifying Hotword Detection
2. Testing Speech-to-Text Conversion
3. Checking Server Communication
4. Playing Back Responses
Troubleshooting
Additional Notes
Acknowledgments
Introduction
LUCY (Language Understanding Companion for You) is a voice assistant designed to run on edge devices like the Raspberry Pi. It uses efficient, low-RAM consumption libraries to perform hotword detection, speech recognition, and text-to-speech synthesis. LUCY communicates with a backend server via WebSockets to process user commands and provide responses.

Project Overview
The LUCY Voice Assistant project includes:

Hotword Detection: Using Picovoice's Porcupine engine with a custom hotword "LUCY".
Speech Recognition: Utilizing Vosk for offline speech-to-text conversion.
Communication: Sending commands to a server via WebSockets and receiving responses.
Text-to-Speech: Using Pico TTS for audio playback of responses.
Optimization: Designed for low RAM usage and lag-free performance.
Headless Operation: Runs without a GUI and starts automatically on boot.
Prerequisites
Hardware:
Raspberry Pi 4
USB Microphone
Speakers or Headphones
MicroSD Card with Raspberry Pi OS (preferably Raspberry Pi OS Lite)
Software:
Raspberry Pi OS (with network connectivity)
Git installed on the Raspberry Pi
Accounts:
Picovoice Console account to generate custom hotword model and access key
Installation
1. Setting Up the Raspberry Pi
Update and Upgrade the System:

bash
Copy code
sudo apt update && sudo apt full-upgrade -y
Reboot the Raspberry Pi:

bash
Copy code
sudo reboot
2. Installing System Dependencies
Install the necessary system packages:

bash
Copy code
sudo apt install -y python3-pip python3-venv git \
portaudio19-dev libasound-dev libttspico-utils \
ffmpeg swig libpulse-dev
3. Setting Up the Python Virtual Environment
Create a Project Directory:

bash
Copy code
mkdir ~/lucy
cd ~/lucy
Set Up the Virtual Environment:

bash
Copy code
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
4. Cloning the Repository
Clone the Project Repository:

bash
Copy code
git clone https://github.com/yourusername/miLucy.git
Replace yourusername with your GitHub username.

Navigate to the Project Directory:

bash
Copy code
cd miLucy
5. Installing Python Dependencies
Install the required Python packages:

bash
Copy code
pip install -r requirements.txt
If requirements.txt is not available, install the packages individually:

bash
Copy code
pip install pvporcupine pyaudio websockets asyncio \
vosk numpy resampy
6. Downloading Models
A. Vosk Speech-to-Text Model
Create a Models Directory:

bash
Copy code
mkdir models
cd models
Download and Extract the Vosk Model:

bash
Copy code
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 vosk_model
Return to the Project Directory:

bash
Copy code
cd ..
Configuration
1. Picovoice Access Key and Hotword Model
A. Sign Up for Picovoice Console
Visit the Picovoice Console and create an account.
B. Create a Custom Hotword "LUCY"
Generate the Hotword Model:

Navigate to Porcupine in the console.
Click on "Create New Keyword".
Enter "lucy" as the keyword.
Select Raspberry Pi as the platform and English as the language.
Generate and download the .ppn model file.
Place the Model in the Project Directory:

bash
Copy code
mv /path/to/downloaded/lucy.ppn ~/lucy/miLucy
C. Obtain the Picovoice Access Key
Navigate to Access Keys in the Picovoice Console.
Create a new access key and copy it.
2. Vosk Speech-to-Text Model
Ensure the Vosk model is correctly placed in the models/vosk_model directory.

3. Setting Audio Device Indices
A. List Available Audio Devices
Create and run a script to list audio devices:

bash
Copy code
nano list_audio_devices.py
Script Content:

python
Copy code
import pyaudio

pa = pyaudio.PyAudio()

print("Available audio devices:")
for i in range(pa.get_device_count()):
    dev = pa.get_device_info_by_index(i)
    print(f"Index {i}: {dev['name']} - Input Channels: {dev['maxInputChannels']}, Output Channels: {dev['maxOutputChannels']}")
Run the Script:

bash
Copy code
python3 list_audio_devices.py
Note the indices of your USB microphone and speakers.

4. Configuring the Server URI
Update the SERVER_URI in your milucy.py script:

python
Copy code
SERVER_URI = 'ws://your_server_address:port'  # Replace with your server's address
Running the Application
1. Testing the Application Manually
Activate the Virtual Environment:

bash
Copy code
source ~/lucy/venv/bin/activate
cd ~/lucy/miLucy
Run the Application:

bash
Copy code
python3 milucy.py
Speak "LUCY" to trigger the hotword detection.

2. Running as a Service
A. Create a systemd Service File
bash
Copy code
sudo nano /etc/systemd/system/lucy.service
Service File Content:

ini
Copy code
[Unit]
Description=LUCY Voice Assistant Service
After=network.target

[Service]
Type=simple
User=pi  # Replace with your username if different
WorkingDirectory=/home/pi/lucy/miLucy
ExecStart=/home/pi/lucy/venv/bin/python /home/pi/lucy/miLucy/milucy.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
B. Enable and Start the Service
bash
Copy code
sudo systemctl daemon-reload
sudo systemctl enable lucy.service
sudo systemctl start lucy.service
C. Check the Service Status
bash
Copy code
sudo systemctl status lucy.service
Testing
1. Verifying Hotword Detection
Speak "LUCY" near the microphone.

Observe the logs to confirm hotword detection:

bash
Copy code
journalctl -u lucy.service -f
2. Testing Speech-to-Text Conversion
After the hotword is detected, speak a command clearly.
Check if the command is correctly transcribed by Vosk.
Logs should display the captured command text.
3. Checking Server Communication
Ensure the server specified in SERVER_URI is running and accessible.
Verify that the command is sent to the server and a response is received.
Logs should show successful communication with the server.
4. Playing Back Responses
Listen for the assistant's response via the speakers.
Ensure the text-to-speech output is clear and audible.
Troubleshooting
Hotword Not Detected:

Ensure the microphone is correctly connected.
Verify the INPUT_DEVICE_INDEX is set to your microphone's index.
Check microphone volume levels using alsamixer.
No Audio Output:

Confirm the speakers are connected and working.
Verify the OUTPUT_DEVICE_INDEX is set correctly.
Test audio playback with aplay command.
Invalid Sample Rate Error:

Use the check_sample_rates.py script to find supported sample rates.
Update the sample rate in your code to a supported value.
Ensure that Porcupine's required sample rate (16000 Hz) is supported or consider resampling.
Server Connection Issues:

Verify network connectivity.
Check if the server is running and accessible at the specified URI.
Ensure proper firewall settings.
High CPU or RAM Usage:

Monitor resource usage with htop.
Optimize code or use lighter models if necessary.
Additional Notes
Optimizations:

The application is designed for low RAM usage.
Uses efficient libraries suitable for embedded devices.
Security:

Consider implementing SSL/TLS encryption for WebSocket communication.
Use authentication tokens for secure server interaction.
Customization:

You can modify the hotword by generating a new model with Picovoice.
Adjust the sensitivity of hotword detection as needed.
Extensibility:

Integrate additional functionalities by enhancing the server-side processing.
Expand speech recognition capabilities with more advanced models if hardware permits.
Acknowledgments
Picovoice Porcupine: For hotword detection engine.
Vosk: For offline speech recognition.
Pico TTS: For text-to-speech synthesis.
Raspberry Pi Foundation: For providing an accessible platform for development.
Project LUCY is an ongoing effort to bring efficient voice assistant capabilities to edge devices. Contributions and suggestions are welcome!

This README was generated to provide comprehensive installation and testing steps for setting up the LUCY Voice Assistant on a Raspberry Pi. It includes all steps performed up to this point in the project.
