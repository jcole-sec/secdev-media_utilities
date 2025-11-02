#!/bin/bash

# Batch transcribe videos recursively using OpenAI Whisper
# Processes all .mp4 videos in the specified directory and subdirectories
# Outputs transcription files (.txt, .srt, .json) to the same directory as each video
# Usage: ./batch_transcribe_video.sh <video_directory>

set +e  # Continue processing even if individual videos fail

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

echo "Starting recursive batch transcription..."
echo "Video directory: $VIDEO_DIR"

total_videos=$(find "$VIDEO_DIR" -type f -name "*.mp4" | wc -l)
echo "Found $total_videos video(s) to process"
echo ""

current=0
succeeded=0
failed=0

# Process each video file recursively
find "$VIDEO_DIR" -type f -name "*.mp4" | while IFS= read -r video; do
    ((current++))
    video_dir=$(dirname "$video")
    
    echo "=========================================="
    echo "[$current/$total_videos] Processing: $(basename "$video")"
    echo "Directory: $video_dir"
    echo "=========================================="
    
    # Transcribe with output to same directory as video
    # Redirect stdin from /dev/null to prevent consuming the pipe
    (
        source venv/bin/activate
        python3 transcription_manager.py transcribe \
            --video "$video" \
            --model base \
            --output "$video_dir" < /dev/null
    )
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✓ Success"
        ((succeeded++))
    else
        echo "✗ Failed with exit code $exit_code"
        ((failed++))
    fi
    
    echo ""
done

echo "=========================================="
echo "Batch transcription complete!"
echo "Processed: $current videos"
echo "Succeeded: $succeeded"
echo "Failed: $failed"
echo "=========================================="
