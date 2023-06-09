import struct
from pvrecorder import PvRecorder
import wave

# ref: https://picovoice.ai/blog/how-to-record-audio-using-python/

def show_audio_devices():
    for index, device in enumerate(PvRecorder.get_audio_devices()):
        print(f"[{index}] {device}")


def record_audio(dev_index):
    recorder = PvRecorder(device_index=dev_index, frame_length=512)

    try:
        recorder.start()
    
        while True:
            frame = recorder.read()
            # Do something ...
    except KeyboardInterrupt:
        recorder.stop()
    finally:
        recorder.delete()

    return audio



def record_audio_file(dev_index, path):

    recorder = PvRecorder(device_index=dev_index, frame_length=512)
    audio = []
    
    try:
        recorder.start()
    
        while True:
            frame = recorder.read()
            audio.extend(frame)
    except KeyboardInterrupt:
        recorder.stop()
        with wave.open(path, 'w') as f:
            f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            f.writeframes(struct.pack("h" * len(audio), *audio))
    finally:
        recorder.delete()

print('\n[*] Available audio devices:\n')
show_audio_devices()

print('\n[*] Recording audio (press CTRL+C to stop):\n')

record_audio_file(1, 'audio.wav')