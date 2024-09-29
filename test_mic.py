import pyaudio

pa = pyaudio.PyAudio()

stream = pa.open(
    rate=44100,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    input_device_index=2
)

print("Recording...")
data = stream.read(1024)
print("Recorded data length:", len(data))

stream.stop_stream()
stream.close()
pa.terminate()

