import struct
import platform
import os
from pvrecorder import PvRecorder
import wave

def show_audio_devices():
    """Display available audio devices"""
    print(f"\n[*] Available audio devices on {platform.system()}:\n")
    
    devices = PvRecorder.get_audio_devices()
    if not devices:
        print("No audio devices found!")
        return
    
    for index, device in enumerate(devices):
        print(f"[{index}] {device}")

def get_default_device():
    """Get default audio device index"""
    devices = PvRecorder.get_audio_devices()
    if not devices:
        return -1
    
    # Look for microphone or use first device
    for i, device in enumerate(devices):
        if any(word in device.lower() for word in ["microphone", "mic", "default", "built-in"]):
            return i
    return 0

def record_audio_file(dev_index=None, path="audio.wav"):
    """Record audio to file with cross-platform support"""
    system = platform.system()
    
    if dev_index is None:
        dev_index = get_default_device()
        if dev_index == -1:
            print("Error: No audio devices available")
            return False
    
    # Platform frame length
    frame_length = 1024 if system == "Linux" else 512
    
    print(f"Recording on {system} using device {dev_index}")
    print("Press CTRL+C to stop recording...")
    
    recorder = PvRecorder(device_index=dev_index, frame_length=frame_length)
    audio = []
    
    try:
        recorder.start()
        while True:
            frame = recorder.read()
            audio.extend(frame)
            
    except KeyboardInterrupt:
        print("\nStopping recording...")
        recorder.stop()
        
        # Save audio
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            
            with wave.open(path, 'w') as f:
                f.setparams((1, 2, 16000, len(audio), "NONE", "NONE"))
                f.writeframes(struct.pack("h" * len(audio), *audio))
            
            print(f"Audio saved to: {os.path.abspath(path)}")
            return True
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
        
    finally:
        recorder.delete()
    
    return False

if __name__ == "__main__":
    
    show_audio_devices()
    
    print('\n[*] Starting audio recording...\n')
    
    recording = record_audio_file()

    if recording:
        print("Recording completed successfully!")
    else:
        print("Recording failed!")