# Whisper Text Extraction

Production-ready Whisper transcription system for long-form video processing.

## Features

- Progress tracking with resume capability
- Multiple output formats (txt, srt, json)
- Memory-efficient segment processing  
- Automated audio extraction via FFmpeg
- Comprehensive logging

## Quick Start

Interactive mode (recommended):
```bash
cd whisper_text_extraction
python transcription_manager.py
```

Command line usage:
```bash
python transcription_manager.py transcribe --video "path/to/video.mp4" --model base
```

## Model Selection

- `tiny` - Fastest (~1GB VRAM)
- `base` - Recommended balance (~1GB VRAM)  
- `small` - Better accuracy (~2GB VRAM)
- `medium` - High accuracy (~5GB VRAM)
- `large` - Best quality (~10GB VRAM)

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies: `openai-whisper`, `ffmpeg-python`

FFmpeg must be installed system-wide.

This interactive mode will:
- Detect your video file automatically
- Let you choose the Whisper model
- Configure segment size
- Handle resume options

### 2. Direct Command Line
```bash
python transcription_manager.py transcribe --video "path/to/video.mp4" --model base --segment-minutes 30
```

### 3. Cleanup and Maintenance
```bash
# Clean up temporary files
python transcription_manager.py cleanup

# Show disk usage analysis  
python transcription_manager.py disk-usage
```

### 4. Command Line Options
```bash
# Full transcription options
python transcription_manager.py transcribe \
  --video "Z:\Training\...\rbp_ai-d1-01.mp4" \
  --output "my_transcripts" \
  --model small \
  --segment-minutes 20 \
  --no-resume

# Help
python transcription_manager.py --help
```

## ⚙️ Configuration Options

### Whisper Models
- **tiny**: Fastest, ~1GB VRAM, lowest accuracy
- **base**: Good balance, ~1GB VRAM **[RECOMMENDED]**
- **small**: Better accuracy, ~2GB VRAM
- **medium**: High accuracy, ~5GB VRAM
- **large**: Best accuracy, ~10GB VRAM

### Segment Sizes
- **10 minutes**: Fine-grained, more resume points, slower overall
- **30 minutes**: Balanced approach **[RECOMMENDED]**
- **60 minutes**: Faster processing, fewer resume points

## 📊 Progress Tracking

The system provides comprehensive progress information:

```
============================================================
TRANSCRIPTION PROGRESS
============================================================
Segment: 8/13
Processed: 4:00:00
Total: 6:22:44
Progress: 62.7%
ETA: 1:15:23
============================================================
```

Progress is automatically saved and can be resumed from interruptions.

## 📄 Output Formats

### 1. Complete Transcript (`rbp_ai_complete_transcript.txt`)
```
RED BLUE PURPLE AI - COMPLETE TRANSCRIPT
============================================================
Source: Z:\Training\...\rbp_ai-d1-01.mp4
Total Duration: 6:22:44
Transcribed: 2025-11-01 15:30:45
Model: base
============================================================

COMPLETE TRANSCRIPT:
----------------------------------------
[Full conversational text here...]

TIMESTAMPED SEGMENTS:
----------------------------------------
[0:00:00 --> 0:00:05]
hello everyone can you hear me OK Google

[0:00:05 --> 0:00:12]
don't forget to order your energy drinks we're ready to go...
```

### 2. SRT Subtitles (`rbp_ai_complete_subtitles.srt`)
```
1
00:00:00,000 --> 00:00:05,000
hello everyone can you hear me OK Google

2
00:00:05,000 --> 00:00:12,000
don't forget to order your energy drinks we're ready to go
```

### 3. JSON Data (`rbp_ai_complete_data.json`)
```json
{
  "metadata": {
    "source": "Z:\\Training\\...\\rbp_ai-d1-01.mp4",
    "total_duration": 22964.8,
    "transcribed": "2025-11-01T15:30:45",
    "model": "base",
    "total_segments": 1247
  },
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "text": "hello everyone can you hear me OK Google"
    }
  ]
}
```

## 🔄 Resume Capability

The system automatically saves progress and can resume from interruptions:

1. **Automatic Resume**: Just run the script again - it detects and resumes automatically
2. **Progress File**: `transcripts/transcription_progress.json` tracks completed segments
3. **Segment Files**: Individual results saved in `transcripts/segments/`
4. **Clean Restart**: Use `--no-resume` to start completely fresh

## 🛠️ Troubleshooting

### Common Issues

**FFmpeg Not Found**
```bash
# Windows: Install via Chocolatey or download from ffmpeg.org
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

**Out of Memory**
- Use smaller Whisper model (`tiny` or `base`)
- Reduce segment size (`--segment-minutes 15`)
- Close other applications

**Video File Not Found**
- Check file path and permissions
- Use absolute paths
- Ensure file is not corrupted

**Slow Processing**
- Use faster model (`tiny` for speed tests)
- Increase segment size (`--segment-minutes 60`)
- Ensure adequate disk space

### Performance Tips

1. **GPU Acceleration**: Whisper automatically uses CUDA if available
2. **Disk Space**: Ensure 2-3GB free space for temporary files
3. **RAM Usage**: 4GB+ recommended for stable processing
4. **Background Apps**: Close unnecessary applications during processing

## 🧹 Cleanup

Remove old files and temporary data:

```bash
python cleanup_transcriptions.py
```

This utility helps you:
- Remove old segment files
- Clean up temporary transcripts
- Analyze disk usage
- Selectively keep important files

## 📈 Expected Performance

### Processing Time Estimates

| Model | Quality | Speed (6h22m video) | Hardware Req |
|-------|---------|-------------------|--------------|
| tiny  | Basic   | ~45-60 minutes    | Any modern PC |
| base  | Good    | ~60-90 minutes    | 4GB+ RAM |
| small | Better  | ~90-120 minutes   | 8GB+ RAM |
| medium| High    | ~120-180 minutes  | 16GB+ RAM |
| large | Best    | ~180-300 minutes  | 32GB+ RAM |

*Times vary based on hardware and content complexity*

### Quality Comparison

Based on our testing with the Red Blue Purple AI video:
- **Whisper vs Google Speech Recognition**: Significantly better accuracy and natural flow
- **Technical Content**: Excellent handling of AI/cybersecurity terminology
- **Multiple Speakers**: Good speaker differentiation
- **Audio Quality**: Robust performance even with varying audio levels

## 🎛️ Advanced Usage

### Custom Configurations

```python
# Custom segment processing
manager = WhisperTranscriptionManager(
    source_video="path/to/video.mp4",
    output_dir="custom_output",
    model_name="small"
)
manager.segment_minutes = 15  # Custom segment size
manager.max_retries = 5       # More retries
manager.transcribe_complete_video()
```

### Integration with Other Tools

The JSON output format makes it easy to integrate with:
- Video editing software (via SRT)
- Content management systems (via JSON)
- Search and analysis tools (via full text)
- Custom applications (via Python imports)

## 🤝 Contributing

This transcription system is part of the `secdev-media_utilities` project. Contributions welcome for:
- Additional output formats
- Performance optimizations  
- Error handling improvements
- Cross-platform compatibility

## 📄 License

Part of the secdev-media_utilities project. See main repository for license information.

---

**Happy Transcribing!** 🎙️➡️📝