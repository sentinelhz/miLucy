import asyncio
import websockets
import pvporcupine
import pyaudio
import struct
import os
import logging
import time
import wave
import audioop
from vosk import Model, KaldiRecognizer
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Configuration parameters
HOTWORD_MODEL_PATH = 'lucy.ppn'  # Path to your custom wake word model
ACCESS_KEY = 'hsXTpPSp/b7nytvbN7/NqUct+oqTM82jLvcMt3P1JtK1kyduC8qzcA=='  # Replace with your Picovoice Access Key
SERVER_URI = 'ws://your_server_address:port'  # Replace with your server's address
AUDIO_OUTPUT_DEVICE_INDEX = 2  # Set to None or the index of your audio output device

# Load the Vosk model once at the beginning
vosk_model = Model("/home/pi/milucy/models/vosk-model")  # Ensure the model path is correct

# Function to play TTS response
def play_response(text):
    logging.info("Playing response...")
    os.system(f'pico2wave -w response.wav "{text}" && aplay response.wav')
    os.remove('response.wav')

# Function to capture speech input after hotword detection
async def capture_speech(pa, sample_rate):
    logging.info("Capturing speech input...")

    # Configure audio stream for recording speech
    stream = pa.open(
        rate=sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=2048
    )

    frames = []
    silence_threshold = 500  # Adjust this value as needed
    silence_duration = 1.0  # Seconds of silence to consider the end of speech
    silence_start = None

    try:
        while True:
            data = stream.read(2048, exception_on_overflow=False)
            frames.append(data)
            rms = audioop.rms(data, 2)  # Measure volume

            if rms < silence_threshold:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > silence_duration:
                    # Silence detected for long enough, stop recording
                    break
            else:
                silence_start = None
    except Exception as e:
        logging.error(f"Error during speech capture: {e}")
    finally:
        stream.stop_stream()
        stream.close()

    # Save the captured audio to a WAV file
    audio_filename = 'command.wav'
    wf = wave.open(audio_filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Perform speech recognition using Vosk
    wf = wave.open(audio_filename, "rb")
    rec = KaldiRecognizer(vosk_model, wf.getframerate())

    command_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = rec.Result()
            result_json = json.loads(result)
            command_text += result_json.get('text', '') + " "
    result = rec.FinalResult()
    result_json = json.loads(result)
    command_text += result_json.get('text', '')

    wf.close()

    # Remove the temporary audio file
    os.remove(audio_filename)

    command_text = command_text.strip()
    logging.info(f"Captured command: {command_text}")
    return command_text

# Function to send the command to the server and receive the response
async def send_command_to_server(command):
    try:
        async with websockets.connect(SERVER_URI) as websocket:
            logging.info("Connected to the server.")
            await websocket.send(command)
            logging.info(f"Sent command: {command}")

            response = await websocket.recv()
            logging.info(f"Received response: {response}")
            return response
    except Exception as e:
        logging.error(f"Failed to communicate with the server: {e}")
        return None

async def main():
    # Initialize Porcupine for hotword detection
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[HOTWORD_MODEL_PATH]
    )
    pa = pyaudio.PyAudio()

    # Open audio input stream
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    logging.info("Voice assistant started. Listening for hotword...")

    try:
        while True:
            # Read audio data from the microphone
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

            # Check for hotword detection
            keyword_index = porcupine.process(pcm_unpacked)
            if keyword_index >= 0:
                logging.info(f"Hotword 'LUCY' detected!")

                # Capture additional audio input after hotword detection
                command = await capture_speech(pa, porcupine.sample_rate)

                if command:
                    # Send the command to the server and get the response
                    response = await send_command_to_server(command)

                    if response:
                        # Play the response using TTS
                        play_response(response)
                else:
                    logging.warning("No command captured.")
    except KeyboardInterrupt:
        logging.info("Voice assistant stopped by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Clean up resources
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

if __name__ == '__main__':
    asyncio.run(main())
