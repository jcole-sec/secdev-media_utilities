import argparse

import numpy as np
import whisper


def iter_chunk_starts(total_samples, chunk_samples, step_samples):
    start = 0
    while start < total_samples:
        yield start
        start += step_samples


def transcribe_audio(
    audio_path,
    model_name="base",
    chunk_duration=30,
    overlap_seconds=5,
    language=None,
    silence_threshold=0.003,
):
    model = whisper.load_model(model_name)
    audio = whisper.load_audio(audio_path)

    sample_rate = whisper.audio.SAMPLE_RATE
    chunk_samples = int(chunk_duration * sample_rate)
    overlap_samples = int(overlap_seconds * sample_rate)
    step_samples = max(1, chunk_samples - overlap_samples)

    total_samples = audio.shape[0]
    starts = list(iter_chunk_starts(total_samples, chunk_samples, step_samples))
    transcription = []
    previous_text = ""
    detected_language = language

    for i, start in enumerate(starts):
        chunk = audio[start:start + chunk_samples]
        chunk_rms = float(np.sqrt(np.mean(np.square(chunk)))) if chunk.size else 0.0

        if chunk_rms < silence_threshold:
            print(f"Skipping silent chunk {i + 1}/{len(starts)} (RMS={chunk_rms:.6f})")
            continue

        chunk = whisper.pad_or_trim(chunk)
        mel = whisper.log_mel_spectrogram(chunk).to(model.device)

        if i == 0 and not detected_language:
            _, probs = model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            print(f"Detected language: {detected_language}")

        options = whisper.DecodingOptions(
            language=detected_language,
            task="transcribe",
            temperature=0.0,
            beam_size=5,
            fp16=(str(model.device).lower() != "cpu"),
            prompt=previous_text[-200:] if previous_text else None,
        )
        result = whisper.decode(model, mel, options)

        text = result.text.strip()
        if text:
            transcription.append(text)
            previous_text = f"{previous_text} {text}".strip()

        print(f"Processed chunk {i + 1}/{len(starts)}")

    full_transcription = " ".join(transcription)
    return full_transcription, detected_language


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Whisper transcription with free local quality/speed enhancements")
    parser.add_argument("--audio", default="output_audio.wav", help="Path to audio file")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny/base/small/medium/large)")
    parser.add_argument("--chunk-seconds", type=int, default=30, help="Chunk duration in seconds")
    parser.add_argument("--overlap-seconds", type=int, default=5, help="Overlap between chunks in seconds")
    parser.add_argument("--language", default=None, help="Language code (auto-detect if omitted)")
    parser.add_argument("--silence-threshold", type=float, default=0.003, help="RMS threshold to skip silent chunks")
    parser.add_argument("--output", default="transcription.txt", help="Output text file")
    args = parser.parse_args()

    text, detected_lang = transcribe_audio(
        audio_path=args.audio,
        model_name=args.model,
        chunk_duration=args.chunk_seconds,
        overlap_seconds=args.overlap_seconds,
        language=args.language,
        silence_threshold=args.silence_threshold,
    )

    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write(text)

    print(f"Detected language: {detected_lang}")
    print("Full Transcription:")
    print(text)
    print(f"Saved to: {args.output}")


