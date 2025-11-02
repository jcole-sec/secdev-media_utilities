@echo off
REM Windows batch script for video to audio conversion
REM Directory containing .mp4 files

set "input_directory=C:\path\to\your\directory"

REM Loop through all .mp4 files in the directory
for %%f in ("%input_directory%\*.mp4") do (
    REM Extract the base name without extension
    set "video_file=%%f"
    set "base_name=%%~nf"
    
    REM Construct the output file name
    set "output_audio=%input_directory%\!base_name!.wav"
    
    REM Run the ffmpeg command
    ffmpeg -i "!video_file!" -q:a 0 -map a "!output_audio!"
    
    echo Processed !video_file! -^> !output_audio!
)

pause