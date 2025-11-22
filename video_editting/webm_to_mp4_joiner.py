import os
import subprocess
import argparse
from pathlib import Path

def join_webm_to_mp4(input_dir, output_file):
    """
    Join multiple WebM files into a single MP4 file.
    
    Args:
        input_dir (str): Directory containing WebM files
        output_file (str): Path to the output MP4 file
    """
    # Ensure input directory exists
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        print(f"Error: Directory '{input_dir}' does not exist or is not a directory.")
        return False
    
    # Get all .webm files in the directory
    webm_files = sorted([str(f) for f in input_path.glob('*.webm')])
    
    if not webm_files:
        print("No WebM files found in the specified directory.")
        return False
    
    print(f"Found {len(webm_files)} WebM files to process.")
    
    # Create a temporary file list for ffmpeg
    list_file = input_path / "file_list.txt"
    try:
        with open(list_file, 'w', encoding='utf-8') as f:
            for webm_file in webm_files:
                f.write(f"file '{os.path.abspath(webm_file)}'\n")
        
        # Build the ffmpeg command
        # Since WebM uses VP8/VP9 and Vorbis codecs which aren't compatible with MP4,
        # we need to re-encode to H.264 (video) and AAC (audio)
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(list_file),
            '-c:v', 'libx264',  # Re-encode video to H.264
            '-preset', 'medium',  # Encoding speed/quality balance
            '-crf', '23',  # Quality level (lower = better quality, 18-28 is good range)
            '-c:a', 'aac',  # Re-encode audio to AAC
            '-b:a', '128k',  # Audio bitrate
            '-y',  # Overwrite output file if it exists
            str(output_file)
        ]
        
        print(f"Joining files into {output_file}...")
        subprocess.run(cmd, check=True)
        print("Joining completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during processing: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        # Clean up the temporary file list
        if list_file.exists():
            try:
                list_file.unlink()
            except Exception as e:
                print(f"Warning: Could not delete temporary file {list_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Join multiple WebM files into a single MP4 file')
    parser.add_argument('input_dir', help='Directory containing WebM files to join')
    parser.add_argument('output_file', help='Output MP4 file path')
    
    args = parser.parse_args()
    
    # Ensure output file has .mp4 extension
    if not args.output_file.lower().endswith('.mp4'):
        args.output_file += '.mp4'
    
    join_webm_to_mp4(args.input_dir, args.output_file)

if __name__ == "__main__":
    main()
