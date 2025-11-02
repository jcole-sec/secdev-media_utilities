# PowerShell script for video to audio conversion
# Directory containing .mp4 files

$inputDirectory = "C:\path\to\your\directory"  # Replace this with the path to your directory

# Get all .mp4 files in the directory
Get-ChildItem -Path $inputDirectory -Filter "*.mp4" | ForEach-Object {
    # Extract the base name (without extension)
    $baseName = $_.BaseName
    $videoFile = $_.FullName
    
    # Construct the output file name
    $outputAudio = Join-Path $inputDirectory "$baseName.wav"
    
    # Run the ffmpeg command
    & ffmpeg -i "$videoFile" -q:a 0 -map a "$outputAudio"
    
    Write-Host "Processed $videoFile -> $outputAudio"
}