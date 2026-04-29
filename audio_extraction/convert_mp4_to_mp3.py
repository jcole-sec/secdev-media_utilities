#!/usr/bin/env python3
"""
MP4 to MP3 Converter
Converts all MP4 files in the current directory to MP3 format using ffmpeg.
"""

import os
import sys
import subprocess
from pathlib import Path


class MP4toMP3Converter:
    """Convert MP4 files to MP3 format using ffmpeg"""

    def __init__(self):
        """Initialize converter and check for ffmpeg"""
        if not self._check_ffmpeg():
            raise RuntimeError("ffmpeg not found. Install with: choco install ffmpeg")

    @staticmethod
    def _check_ffmpeg() -> bool:
        """Check if ffmpeg is available"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def convert_file(self, mp4_path: Path, delete_original: bool = False) -> bool:
        """
        Convert single MP4 file to MP3.
        
        Args:
            mp4_path: Path to MP4 file
            delete_original: If True, delete original MP4 after conversion
            
        Returns:
            True if successful, False otherwise
        """
        mp3_path = mp4_path.with_suffix(".mp3")
        
        # Skip if MP3 already exists
        if mp3_path.exists():
            print(f"  ⊘ MP3 already exists: {mp3_path.name}")
            return True
        
        try:
            print(f"  Converting...")
            
            # ffmpeg command: extract audio from MP4 as MP3
            # -i: input file
            # -q:a 9: quality (1-9, where 9 is highest compression, smaller file)
            # -n: don't overwrite output file
            subprocess.run(
                ["ffmpeg", "-i", str(mp4_path), "-q:a", "9", "-n", str(mp3_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            
            print(f"  ✓ Converted to: {mp3_path.name}")
            
            # Optionally delete original MP4
            if delete_original:
                try:
                    mp4_path.unlink()
                    print(f"  Deleted original: {mp4_path.name}")
                except Exception as e:
                    print(f"  Warning: Could not delete {mp4_path.name}: {e}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Conversion failed: {e}")
            return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False

    def process_directory(self, directory: Path = None, delete_original: bool = False) -> None:
        """
        Convert all MP4 files in directory to MP3.
        
        Args:
            directory: Directory to process (default: current directory)
            delete_original: If True, delete original MP4 files after conversion
        """
        if directory is None:
            directory = Path.cwd()

        mp4_files = sorted(directory.glob("*.mp4"))

        if not mp4_files:
            print("No MP4 files found in directory")
            return

        print(f"Found {len(mp4_files)} MP4 files to convert")
        print("=" * 60)

        successful = 0
        failed = 0
        skipped = 0

        for mp4_path in mp4_files:
            print(f"\n{mp4_path.name}")
            
            try:
                mp3_path = mp4_path.with_suffix(".mp3")
                if mp3_path.exists():
                    print(f"  ⊘ MP3 already exists: {mp3_path.name}")
                    skipped += 1
                elif self.convert_file(mp4_path, delete_original=delete_original):
                    successful += 1
                else:
                    failed += 1
                    
            except KeyboardInterrupt:
                print("\n\nConversion interrupted by user")
                break
            except Exception as e:
                print(f"  ✗ Unexpected error: {e}")
                failed += 1

        print("\n" + "=" * 60)
        print(f"Conversion complete!")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Skipped: {skipped}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert MP4 files to MP3 using ffmpeg"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete original MP4 files after successful conversion"
    )
    
    args = parser.parse_args()
    
    try:
        print("MP4 to MP3 Converter")
        print("=" * 60)
        converter = MP4toMP3Converter()
        print("✓ ffmpeg found")
        print()
        converter.process_directory(delete_original=args.delete)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
