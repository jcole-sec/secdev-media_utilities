#!/bin/bash

# Batch transcribe videos recursively
# This script processes all .mp4 videos in the specified directory and subdirectories
# Outputs transcription files to the same directory as each video source
# Usage: ./batch_transcribe_video.sh [VIDEO_DIRECTORY]

# Check if directory argument is provided
if [ -z "$1" ]; then
    echo "Error: No directory specified"
    echo "Usage: $0 <video_directory>"
    echo "Example: $0 ~/nas/data_share/Training/videos"
    exit 1
fi

VIDEO_DIR="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if directory exists
if [ ! -d "$VIDEO_DIR" ]; then
    echo "Error: Directory does not exist: $VIDEO_DIR"
    exit 1
fi

cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

echo "Starting recursive batch transcription of videos..."
echo "Video directory: $VIDEO_DIR"
echo ""

# Count total videos
total_videos=$(find "$VIDEO_DIR" -type f -name "*.mp4" | wc -l)
echo "Found $total_videos video(s) to process"
echo ""

current=0

# Process each video file recursively
find "$VIDEO_DIR" -type f -name "*.mp4" | while read -r video; do
    ((current++))
    video_dir=$(dirname "$video")
    
    echo "=========================================="
    echo "[$current/$total_videos] Processing: $(basename "$video")"
    echo "Directory: $video_dir"
    echo "=========================================="
    
    # Transcribe with output to the same directory as the video
    python3 transcription_manager.py transcribe \
        --video "$video" \
        --model base \
        --output "$video_dir"
    
    echo ""
done

echo "Batch transcription complete!"
