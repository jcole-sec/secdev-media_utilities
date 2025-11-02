import os
import platform
from pathlib import Path

def get_safe_filename(filename):
    """Convert filename to be safe on all platforms"""
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    return safe_name.strip('. ')

def get_output_dir():
    """Get platform-appropriate output directory"""
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        return home / "Documents" / "MediaUtilities"
    else:  # Linux/macOS
        return home / "Documents" / "MediaUtilities"

def get_media_paths(base_name="output"):
    """Get file paths for media processing"""
    output_dir = get_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    safe_name = get_safe_filename(base_name)
    
    return {
        'transcript_txt': output_dir / f"{safe_name}.txt",
        'transcript_srt': output_dir / f"{safe_name}.srt",
        'audio_file': output_dir / f"{safe_name}.wav"
    }

# Usage example
if __name__ == "__main__":
    print(f"Platform: {platform.system()}")
    print(f"Output directory: {get_output_dir()}")
    
    # Example usage
    paths = get_media_paths("test_recording")
    print("\nGenerated file paths:")
    for key, path in paths.items():
        print(f"  {key}: {path}")