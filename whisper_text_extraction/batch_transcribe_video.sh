#!/bin/bash

# Batch transcribe videos
# This script processes all videos in the specified directory

VIDEO_DIR="paths/to/your/video_directory"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

echo "Starting batch transcription of videos..."


echo "Video directory: $VIDEO_DIR"
echo ""

# Process each video file
for video in "$VIDEO_DIR"/*.mp4; do
    if [ -f "$video" ]; then
        echo "=========================================="
        echo "Processing: $(basename "$video")"
        echo "=========================================="
        python3 transcription_manager.py transcribe --video "$video" --model base
        echo ""
    fi
done

echo "Batch transcription complete!"
