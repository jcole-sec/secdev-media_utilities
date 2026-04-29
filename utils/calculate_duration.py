#!/usr/bin/env python3
"""
Calculate total duration of audio files in directory
"""

import os
from pathlib import Path

try:
    from pydub import AudioSegment
except ImportError:
    print("Error: pydub package not installed. Install with: pip install pydub")
    exit(1)


def get_file_duration(file_path: Path) -> float:
    """Get duration in minutes"""
    try:
        audio = AudioSegment.from_file(str(file_path))
        duration_ms = len(audio)
        duration_minutes = duration_ms / (1000 * 60)
        return duration_minutes
    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")
        return 0


def main():
    directory = Path.cwd()
    audio_files = sorted(
        list(directory.glob("*.mp3")) + list(directory.glob("*.mp4"))
    )

    if not audio_files:
        print("No audio files found")
        return

    print(f"Calculating duration of {len(audio_files)} audio files...\n")
    print(f"{'File Name':<50} {'Duration (min)':<15}")
    print("=" * 65)

    total_minutes = 0
    for file_path in audio_files:
        duration = get_file_duration(file_path)
        total_minutes += duration
        print(f"{file_path.name:<50} {duration:>10.2f} min")

    print("=" * 65)
    print(f"{'TOTAL':<50} {total_minutes:>10.2f} min")
    print(f"\nTotal Hours: {total_minutes / 60:.2f} hours")
    print(f"\n" + "=" * 65)
    print("COST ESTIMATION (Scribe v2 Speech-to-Text)")
    print("=" * 65)

    # ElevenLabs Scribe v2 pricing: ~$0.006 per minute
    # (This is typical for pay-as-you-go, varies by plan)
    price_per_minute = 0.006
    estimated_cost = total_minutes * price_per_minute

    print(f"Rate: ${price_per_minute:.4f} per minute (typical)")
    print(f"Total Cost: ${estimated_cost:.2f}")
    print(f"\nNote: Check https://elevenlabs.io/pricing for current rates")
    print("Prices may vary by subscription plan")


if __name__ == "__main__":
    main()
