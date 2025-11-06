#!/bin/bash

# Clean up transcription artifacts recursively
# Removes all files created by batch_transcribe_video.sh
# Usage: ./cleanup_transcriptions.sh <directory>

set +e  # Continue even if some files don't exist

if [ -z "$1" ]; then
    echo "Error: No directory specified"
    echo "Usage: $0 <directory>"
    echo "Example: $0 ~/nas/data_share/Training/videos"
    exit 1
fi

TARGET_DIR="$1"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory does not exist: $TARGET_DIR"
    exit 1
fi

echo "Cleaning up transcription artifacts in: $TARGET_DIR"
echo ""
echo "This will remove:"
echo "  - *_transcript.txt"
echo "  - *_subtitles.srt"
echo "  - *_data.json"
echo "  - .*_progress.json (hidden progress files)"
echo "  - .*_segments/ (hidden segment directories)"
echo "  - transcription_progress.json (legacy progress files)"
echo "  - segments/ (legacy segment directories)"
echo "  - transcription.log"
echo ""

read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

echo ""
echo "Removing transcription artifacts..."

# Count files before deletion
transcript_count=$(find "$TARGET_DIR" -type f -name "*_transcript.txt" 2>/dev/null | wc -l)
srt_count=$(find "$TARGET_DIR" -type f -name "*_subtitles.srt" 2>/dev/null | wc -l)
json_count=$(find "$TARGET_DIR" -type f -name "*_data.json" 2>/dev/null | wc -l)
progress_count=$(find "$TARGET_DIR" -type f -name ".*_progress.json" 2>/dev/null | wc -l)
segment_count=$(find "$TARGET_DIR" -type d -name ".*_segments" 2>/dev/null | wc -l)
legacy_progress_count=$(find "$TARGET_DIR" -type f -name "transcription_progress.json" 2>/dev/null | wc -l)
legacy_segment_count=$(find "$TARGET_DIR" -type d -name "segments" 2>/dev/null | wc -l)
log_count=$(find "$TARGET_DIR" -type f -name "transcription.log" 2>/dev/null | wc -l)

total_files=$((transcript_count + srt_count + json_count + progress_count + legacy_progress_count + log_count))
total_items=$((total_files + segment_count + legacy_segment_count))

if [ $total_items -eq 0 ]; then
    echo "No transcription artifacts found"
    exit 0
fi

echo "Found:"
echo "  Transcript files:     $transcript_count"
echo "  Subtitle files:       $srt_count"
echo "  JSON data files:      $json_count"
echo "  Progress files:       $progress_count"
echo "  Segment directories:  $segment_count"
echo "  Legacy progress:      $legacy_progress_count"
echo "  Legacy segments:      $legacy_segment_count"
echo "  Log files:            $log_count"
echo "  Total items:          $total_items"
echo ""

# Remove transcript files
if [ $transcript_count -gt 0 ]; then
    echo "Removing transcript files..."
    find "$TARGET_DIR" -type f -name "*_transcript.txt" -delete
fi

# Remove subtitle files
if [ $srt_count -gt 0 ]; then
    echo "Removing subtitle files..."
    find "$TARGET_DIR" -type f -name "*_subtitles.srt" -delete
fi

# Remove JSON data files
if [ $json_count -gt 0 ]; then
    echo "Removing JSON data files..."
    find "$TARGET_DIR" -type f -name "*_data.json" -delete
fi

# Remove progress files (hidden)
if [ $progress_count -gt 0 ]; then
    echo "Removing progress files..."
    find "$TARGET_DIR" -type f -name ".*_progress.json" -delete
fi

# Remove segment directories (hidden)
if [ $segment_count -gt 0 ]; then
    echo "Removing segment directories..."
    find "$TARGET_DIR" -type d -name ".*_segments" -exec rm -rf {} + 2>/dev/null
fi

# Remove legacy progress files
if [ $legacy_progress_count -gt 0 ]; then
    echo "Removing legacy progress files..."
    find "$TARGET_DIR" -type f -name "transcription_progress.json" -delete
fi

# Remove legacy segment directories
if [ $legacy_segment_count -gt 0 ]; then
    echo "Removing legacy segment directories..."
    find "$TARGET_DIR" -type d -name "segments" -exec rm -rf {} + 2>/dev/null
fi

# Remove log files
if [ $log_count -gt 0 ]; then
    echo "Removing log files..."
    find "$TARGET_DIR" -type f -name "transcription.log" -delete
fi

echo ""
echo "=========================================="
echo "Cleanup complete!"
echo "Removed $total_items items"
echo "=========================================="
