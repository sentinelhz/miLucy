import pyaudio


pa = pyaudio.PyAudio()


print("Available audio devices")
for i in range(pa.get_device_count()):
    dev = pa.get_device_info_by_index(i)
    print(f"Index {i}: {dev['name']} - Input Channels: {dev['maxInputChannels']}, Output Channels: {dev['maxOutputChannels']}")

