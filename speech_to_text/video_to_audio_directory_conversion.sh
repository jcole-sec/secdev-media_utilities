#!/bin/bash

# Directory containing .mp4 files
input_directory="/path/to/your/directory"  # Replace this with the path to your directory

# Loop through all .mp4 files in the directory
for video_file in "$input_directory"/*.mp4; do
    # Extract the base name (without extension)
    base_name=$(basename "$video_file" .mp4)

    # Construct the output file name
    output_audio="$input_directory/$base_name.wav"

    # Run the ffmpeg command
    ffmpeg -i "$video_file" -q:a 0 -map a "$output_audio"

    echo "Processed $video_file -> $output_audio"
done
