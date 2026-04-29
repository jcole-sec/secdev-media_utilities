#!/usr/bin/env python3
"""
Duplicate COPY File Remover
Removes files with "COPY" in the name if they have identical content to the source file.
"""

import hashlib
import sys
from pathlib import Path


class CopyFileRemover:
    """Remove duplicate COPY files with identical content to source"""

    @staticmethod
    def _get_file_hash(file_path: Path, chunk_size: int = 65536) -> str:
        """
        Calculate SHA256 hash of file.
        
        Args:
            file_path: Path to file
            chunk_size: Size of chunks to read
            
        Returns:
            SHA256 hash of file
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"  Error reading file: {e}")
            return None

    @staticmethod
    def _get_source_filename(copy_filename: str) -> str:
        """
        Get source filename from copy filename.
        
        Examples:
            "2015-07-22 18-18-40 - Copy.mp4" → "2015-07-22 18-18-40.mp4"
            "file - Copy.mp3" → "file.mp3"
            "file - Copy (2).mp4" → "file.mp4"
        
        Args:
            copy_filename: Filename with COPY in it
            
        Returns:
            Predicted source filename
        """
        # Remove " - Copy" and variants
        source = copy_filename.replace(" - Copy", "").replace(" - copy", "")
        
        # Remove numbered copy patterns like " (2)", " (3)"
        import re
        source = re.sub(r"\s*\(\d+\)\s*", "", source)
        
        return source

    def process_directory(self, directory: Path = None) -> None:
        """
        Find and remove COPY files that are identical to source files.
        
        Args:
            directory: Directory to process (default: current directory)
        """
        if directory is None:
            directory = Path.cwd()

        # Find all files with COPY in name (case-insensitive)
        copy_files = [
            f for f in directory.iterdir()
            if f.is_file() and "copy" in f.name.lower()
        ]

        if not copy_files:
            print("No files with 'COPY' in name found")
            return

        print(f"Found {len(copy_files)} files with 'COPY' in name")
        print("=" * 70)

        deleted = 0
        kept = 0
        errors = 0

        for copy_file in sorted(copy_files):
            # Get predicted source filename
            source_filename = self._get_source_filename(copy_file.name)
            source_file = copy_file.parent / source_filename

            print(f"\n{copy_file.name}")

            # Check if source file exists
            if not source_file.exists():
                print(f"  ⊘ Source not found: {source_filename}")
                kept += 1
                continue

            # Compare file sizes first (quick check)
            if copy_file.stat().st_size != source_file.stat().st_size:
                print(f"  ⊘ Different size - keeping")
                kept += 1
                continue

            # Compare content hashes
            print(f"  Comparing with: {source_filename}")
            copy_hash = self._get_file_hash(copy_file)
            source_hash = self._get_file_hash(source_file)

            if copy_hash is None or source_hash is None:
                print(f"  ✗ Error computing hashes")
                errors += 1
                continue

            if copy_hash == source_hash:
                # Files are identical - delete COPY
                try:
                    copy_file.unlink()
                    print(f"  ✓ Deleted (identical content)")
                    deleted += 1
                except Exception as e:
                    print(f"  ✗ Failed to delete: {e}")
                    errors += 1
            else:
                print(f"  ⊘ Different content - keeping")
                kept += 1

        print("\n" + "=" * 70)
        print(f"Cleanup complete!")
        print(f"  Deleted: {deleted}")
        print(f"  Kept: {kept}")
        print(f"  Errors: {errors}")


def main():
    """Main entry point"""
    try:
        print("Duplicate COPY File Remover")
        print("=" * 70)
        remover = CopyFileRemover()
        remover.process_directory()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
