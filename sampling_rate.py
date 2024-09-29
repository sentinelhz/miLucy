import pyaudio

def check_sample_rates(device_index):
    pa = pyaudio.PyAudio()
    device_info = pa.get_device_info_by_index(device_index)

    print(f"Checking supported sample rates for device index {device_index}: {device_info['name']}")
    standard_sample_rates = [
        8000,
        11025,
        16000,
        22050,
        32000,
        44100,
        48000,
        88200,
        96000,
        192000,
    ]

    for rate in standard_sample_rates:
        try:
            if pa.is_format_supported(
                rate,
                input_device=device_index,
                input_channels=1,
                input_format=pyaudio.paInt16,
            ):
                print(f"Sample rate {rate} Hz is supported.")
            else:
                print(f"Sample rate {rate} Hz is NOT supported.")
        except ValueError:
            print(f"Sample rate {rate} Hz is NOT supported.")

    pa.terminate()

if __name__ == "__main__":
    INPUT_DEVICE_INDEX = 2  # Replace with your microphone's device index
    check_sample_rates(INPUT_DEVICE_INDEX)

