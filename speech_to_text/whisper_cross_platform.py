import whisper
import platform
import os
import numpy as np

def load_whisper_model(model_size="base"):
    """Load Whisper model with automatic device detection"""
    system = platform.system()
    print(f"Loading Whisper model '{model_size}' on {system}...")
    
    try:
        import torch
        # Simple device detection across platforms
        if torch.cuda.is_available():
            device = "cuda"
            print(f"Using GPU (CUDA)")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps" 
            print(f"Using GPU (Apple MPS)")
        else:
            device = "cpu"
            print(f"Using CPU")
        
        return whisper.load_model(model_size, device=device)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def seconds_to_srt_time(seconds):
    """Convert seconds to SRT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def transcribe_audio_file(audio_path, model_size="base", output_base_name="transcription"):
    """Transcribe audio file with chunking support"""
    model = load_whisper_model(model_size)
    if not model:
        return False
    
    transcript_txt = f"{output_base_name}.txt"
    transcript_srt = f"{output_base_name}.srt"
    
    try:
        print(f"Loading audio file: {audio_path}")
        audio = whisper.load_audio(audio_path)
        
        # Tunable chunking settings (free/local optimization)
        chunk_duration = 30
        overlap_seconds = 5
        silence_threshold = 0.003
        sample_rate = whisper.audio.SAMPLE_RATE
        chunk_samples = chunk_duration * sample_rate
        overlap_samples = overlap_seconds * sample_rate
        step_samples = max(1, chunk_samples - overlap_samples)
        
        # Split audio into chunks
        total_samples = audio.shape[0]
        chunks = [audio[i:i + chunk_samples] for i in range(0, total_samples, step_samples)]
        
        print(f"Processing {len(chunks)} chunks...")
        
        # Process each chunk
        transcription = []
        detected_language = None
        previous_text = ""
        
        for i, chunk in enumerate(chunks):
            try:
                chunk = whisper.pad_or_trim(chunk)
                chunk_rms = float(np.sqrt(np.mean(np.square(chunk)))) if chunk.size else 0.0
                if chunk_rms < silence_threshold:
                    print(f"Skipping silent chunk {i + 1}/{len(chunks)} (RMS={chunk_rms:.6f})")
                    continue
                mel = whisper.log_mel_spectrogram(chunk).to(model.device)
                
                # Detect language for first chunk only
                if i == 0:
                    _, probs = model.detect_language(mel)
                    detected_language = max(probs, key=probs.get)
                    print(f"Detected language: {detected_language}")
                
                options = whisper.DecodingOptions(
                    language=detected_language,
                    task="transcribe",
                    temperature=0.0,
                    beam_size=5,
                    best_of=5,
                    fp16=(str(model.device).lower() != "cpu"),
                    prompt=previous_text[-200:] if previous_text else None,
                )
                result = whisper.decode(model, mel, options)

                text = result.text.strip()
                if text:
                    transcription.append(text)
                    previous_text = f"{previous_text} {text}".strip()
                print(f"Processed chunk {i + 1}/{len(chunks)}")
                
            except Exception as e:
                print(f"Error processing chunk {i + 1}: {e}")
                transcription.append("[ERROR]")
        
        # Combine and save transcription
        full_transcription = ' '.join(transcription)
        
        # Save text file
        with open(transcript_txt, 'w', encoding='utf-8') as f:
            f.write(full_transcription)
        print(f"Text saved: {transcript_txt}")
        
        # Save SRT file
        with open(transcript_srt, 'w', encoding='utf-8') as f:
            for i, text in enumerate(transcription):
                if text.strip() and text != "[ERROR]":
                    start_time = i * chunk_duration
                    end_time = (i + 1) * chunk_duration
                    
                    f.write(f"{i + 1}\n")
                    f.write(f"{seconds_to_srt_time(start_time)} --> {seconds_to_srt_time(end_time)}\n")
                    f.write(f"{text.strip()}\n\n")
        
        print(f"SRT saved: {transcript_srt}")
        print(f"\nTranscription ({detected_language}):")
        print("-" * 50)
        print(full_transcription)
        
        return True
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        return False

# Command line usage
if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Cross-platform Whisper transcription")
    parser.add_argument("--audio", default="output_audio.wav", help="Audio file to transcribe")
    parser.add_argument("--model", default="base", help="Whisper model size")
    parser.add_argument("--output", default="transcription", help="Output base name")
    
    args = parser.parse_args()
    
    # Check if audio file exists
    if not os.path.exists(args.audio):
        print(f"Error: Audio file '{args.audio}' not found")
        sys.exit(1)
    
    # Transcribe
    print(f"Starting transcription on {platform.system()}")
    success = transcribe_audio_file(args.audio, args.model, args.output)
    
    if success:
        print("Transcription completed successfully!")
    else:
        print("Transcription failed!")
        sys.exit(1)