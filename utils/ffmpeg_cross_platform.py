import subprocess
import platform
import os
import shutil
from pathlib import Path

def find_ffmpeg():
    """Find FFmpeg executable on current platform"""
    system = platform.system()
    
    # Try common paths
    common_paths = {
        "Windows": ["ffmpeg.exe", "C:\\ffmpeg\\bin\\ffmpeg.exe"],
        "Linux": ["ffmpeg", "/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"],
        "Darwin": ["ffmpeg", "/usr/local/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg"]
    }
    
    paths = common_paths.get(system, ["ffmpeg"])
    
    for path in paths:
        if shutil.which(path) or (os.path.isfile(path) and os.access(path, os.X_OK)):
            return path
    
    return "ffmpeg"  # Fallback

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run([find_ffmpeg(), "-version"], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False

def get_install_instructions():
    """Get FFmpeg installation instructions for current platform"""
    system = platform.system()
    
    instructions = {
        "Windows": "choco install ffmpeg  OR  winget install FFmpeg",
        "Linux": "sudo apt install ffmpeg  OR  sudo dnf install ffmpeg", 
        "Darwin": "brew install ffmpeg"
    }
    
    return instructions.get(system, "Visit https://ffmpeg.org/download.html")

def convert_video_to_audio(input_path, output_path, quality="high"):
    """Convert video to audio"""
    if not check_ffmpeg():
        print("Error: FFmpeg not available")
        print(f"Install with: {get_install_instructions()}")
        return False
    
    # Quality settings
    settings = {
        "high": ["-q:a", "0", "-map", "a"],
        "whisper": ["-vn", "-ac", "1", "-ar", "16000", "-acodec", "pcm_s16le"]
    }
    
    cmd = [find_ffmpeg(), "-i", input_path] + settings.get(quality, settings["high"]) + [output_path]
    
    try:
        use_shell = platform.system() == "Windows"
        result = subprocess.run(cmd, shell=use_shell, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Converted: {input_path} -> {output_path}")
            return True
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def batch_convert_directory(input_dir, output_dir=None, quality="high"):
    """Batch convert all MP4 files in directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir or input_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find MP4 files
    mp4_files = list(input_path.glob("*.mp4")) + list(input_path.glob("*.MP4"))
    
    if not mp4_files:
        print(f"No MP4 files found in {input_dir}")
        return []
    
    converted = []
    for video_file in mp4_files:
        audio_file = output_path / f"{video_file.stem}.wav"
        print(f"Converting: {video_file.name}")
        
        if convert_video_to_audio(str(video_file), str(audio_file), quality):
            converted.append(str(audio_file))
    
    print(f"Converted {len(converted)}/{len(mp4_files)} files")
    return converted

# Usage example
if __name__ == "__main__":
    print(f"Platform: {platform.system()}")
    print(f"FFmpeg path: {find_ffmpeg()}")
    print(f"FFmpeg available: {check_ffmpeg()}")
    
    if not check_ffmpeg():
        print(f"Install with: {get_install_instructions()}")