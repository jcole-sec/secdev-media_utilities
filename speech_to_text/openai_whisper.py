import whisper
import numpy as np

# Load Whisper model
model = whisper.load_model("base")

# Load the full audio
audio = whisper.load_audio("output_audio.wav")

# Parameters
chunk_duration = 30  # Duration of each audio chunk in seconds
sample_rate = whisper.audio.SAMPLE_RATE  # Whisper model's sample rate (16000 Hz)
chunk_samples = chunk_duration * sample_rate  # Number of samples per chunk

# Split audio into chunks
total_samples = audio.shape[0]
chunks = [audio[i:i+chunk_samples] for i in range(0, total_samples, chunk_samples)]

# Process each chunk
transcription = []

for i, chunk in enumerate(chunks):
    # Pad or trim the chunk to fit 30 seconds
    chunk = whisper.pad_or_trim(chunk)
    
    # Make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(chunk).to(model.device)
    
    # Detect the spoken language (for the first chunk)
    if i == 0:
        _, probs = model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")
    
    # Decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    
    # Append recognized text to the transcription
    transcription.append(result.text)
    print(f"Processed chunk {i + 1}/{len(chunks)}")

# Combine transcriptions from all chunks
full_transcription = ' '.join(transcription)

# Print the full transcription
print("Full Transcription:")
print(full_transcription)
