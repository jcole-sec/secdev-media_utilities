# Media Utilities

Python utilities for media processing workflows: audio recording, speech-to-text transcription, and video-to-audio conversion.

## Quick Start

### Video Transcription with Whisper
```bash
# Interactive launcher
python transcribe.py

# Command line usage
cd whisper_text_extraction  
python transcription_manager.py transcribe --video "video.mp4" --model base
```

### Audio Extraction with FFmpeg
```bash
# Install FFmpeg (Windows)
winget install --id=Gyan.FFmpeg -e

# Convert video to audio (high quality)
ffmpeg -i input_video.mp4 -q:a 0 -map a output_audio.wav

# Convert for Whisper (optimized)
ffmpeg -i input_video.mp4 -vn -ac 1 -ar 16000 -acodec pcm_s16le output_audio.wav
```

## Project Structure

- **`whisper_text_extraction/`** - Production Whisper transcription with progress tracking
- **`audio_recorder/`** - Real-time audio capture using PvRecorder
- **`speech_to_text/`** - Alternative Whisper implementations  
- **`video_text_extract/`** - Legacy Google Speech Recognition pipeline
- **`utils/`** - Cross-platform utilities and FFmpeg wrappers

## Whisper Model Selection

|  Model  | VRAM | Speed | Use Case |
|:-------:|:----:|:-----:|:---------|
|  tiny   | ~1GB | ~32x  | Quick tests, low resources |
|  base   | ~1GB | ~16x  | **Recommended balance** |
|  small  | ~2GB | ~6x   | Better accuracy |
|  medium | ~5GB | ~2x   | High accuracy |
|  large  | ~10GB| 1x    | Best quality |

## Installation

```bash
# Clone repository
git clone https://github.com/jcole-sec/secdev-media_utilities.git
cd secdev-media_utilities

# Install FFmpeg (Windows)
winget install --id=Gyan.FFmpeg -e

# Cross-platform setup
python setup_cross_platform.py

# Or install manually
pip install -r requirements_cross_platform.txt
```

### Component-Specific Setup
```bash
# Whisper transcription
cd whisper_text_extraction
pip install -r requirements.txt

# Audio recording  
cd audio_recorder
pip install -r requirements.txt

# Legacy video processing
cd video_text_extract
pip install -r requirements.txt
```

## Usage Examples

### Whisper Text Extraction
```bash
cd whisper_text_extraction
python transcription_manager.py transcribe --video "video.mp4" --model base --segment-minutes 30
```

### Audio Recording
```bash
cd audio_recorder
python audio_recorder.py
```

### Alternative Transcription Methods
```bash
cd speech_to_text
python openai_whisper.py          # Full chunking with language detection
python demo-openai_whisper.py     # Simple 30-second chunks
python whisper_cross_platform.py  # Cross-platform function-based
```

## Output Structure

Whisper transcription creates:
```
transcripts/
├── videoname_transcript.txt          # Plain text
├── videoname_subtitles.srt           # Subtitles with timestamps  
├── videoname_data.json               # Full metadata
├── transcription_progress.json       # Resume tracking
├── transcription.log                 # Processing logs
└── segments/                         # Individual results
```

## Requirements

- Python 3.8+
- FFmpeg (system-wide installation)
- Git
