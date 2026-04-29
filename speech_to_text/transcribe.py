#!/usr/bin/env python3
"""
ElevenLabs Audio Transcription Client
Transcribes all MP3 files in the current directory using ElevenLabs Speech-to-Text API (Scribe v2).
API key should be stored in api.ini or set as ELEVENLABS_API_KEY environment variable.
"""

import os
import sys
import json
import configparser
from pathlib import Path
from typing import Optional

try:
    from elevenlabs.client import ElevenLabs
except ImportError:
    print("Error: elevenlabs package not installed. Install with: pip install elevenlabs")
    sys.exit(1)


class ElevenLabsTranscriber:
    """Transcribe audio files using ElevenLabs Speech-to-Text API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize transcriber with API key.
        
        Args:
            api_key: ElevenLabs API key. If None, will look for it in environment or config.
        """
        if not api_key:
            api_key = self._get_api_key()
        
        if not api_key:
            raise ValueError(
                "No API key found. Set ELEVENLABS_API_KEY environment variable "
                "or add api_key to [elevenlabs] section in api.ini"
            )
        
        self.client = ElevenLabs(api_key=api_key)
        print(f"✓ Connected to ElevenLabs API")

    @staticmethod
    def _get_api_key() -> Optional[str]:
        """Get API key from environment or api.ini"""
        # Try environment variable first
        if "ELEVENLABS_API_KEY" in os.environ:
            return os.environ["ELEVENLABS_API_KEY"]
        
        # Try api.ini file
        config_path = Path(__file__).parent / "api.ini"
        if config_path.exists():
            config = configparser.ConfigParser()
            config.read(config_path)
            
            if "elevenlabs" in config and "api_key" in config["elevenlabs"]:
                return config["elevenlabs"]["api_key"]
        
        return None

    def _format_diarization_output(self, transcription) -> str:
        """
        Extract and format transcription with speaker diarization.
        
        Args:
            transcription: Response from ElevenLabs API
            
        Returns:
            Formatted text with speaker labels
        """
        output = []
        
        # Check if response has chapters/segments with speaker info
        if hasattr(transcription, 'chapters') and transcription.chapters:
            for chapter in transcription.chapters:
                if hasattr(chapter, 'summary'):
                    output.append(chapter.summary)
        
        # Check for segments with diarization
        elif hasattr(transcription, 'segments') and transcription.segments:
            for segment in transcription.segments:
                speaker_label = ""
                if hasattr(segment, 'speaker') and segment.speaker is not None:
                    speaker_label = f"[Speaker {segment.speaker}] "
                
                text = segment.text if hasattr(segment, 'text') else str(segment)
                output.append(f"{speaker_label}{text}")
        
        # Check for direct text field (basic transcription)
        elif hasattr(transcription, 'text') and transcription.text:
            return transcription.text
        
        # Return formatted output or full response as string
        if output:
            return "\n".join(output)
        else:
            return str(transcription)

    def transcribe_file(
        self,
        file_path: Path,
        language_code: str = "eng",
        diarize: bool = True,
        tag_audio_events: bool = True
    ) -> Optional[str]:
        """
        Transcribe MP3 file using ElevenLabs Scribe v2 API.
        
        Args:
            file_path: Path to MP3 file
            language_code: Language code (e.g., "eng" for English, None for auto-detect)
            diarize: Whether to identify speakers
            tag_audio_events: Whether to tag audio events (laughter, applause, etc.)
            
        Returns:
            Transcription text or None if error
        """
        print(f"\nTranscribing: {file_path.name}")

        try:
            print(f"  Sending to ElevenLabs Scribe v2 API...")
            
            with open(file_path, "rb") as audio_file:
                transcription = self.client.speech_to_text.convert(
                    file=audio_file,
                    model_id="scribe_v2",
                    language_code=language_code,
                    diarize=diarize,
                    tag_audio_events=tag_audio_events,
                )
            
            print(f"  ✓ Transcription complete")
            
            # Extract and format transcription with diarization
            transcription_text = self._format_diarization_output(transcription)
            return transcription_text
                
        except Exception as e:
            print(f"  ✗ Transcription failed: {e}")
            return None

    def save_transcription(self, transcription_text: str, output_path: Path) -> bool:
        """Save transcription to text file"""
        try:
            output_path.write_text(transcription_text, encoding="utf-8")
            print(f"  ✓ Saved to: {output_path.name}")
            return True
        except Exception as e:
            print(f"  ✗ Failed to save transcription: {e}")
            return False

    def process_directory(
        self,
        directory: Path = None,
        language_code: str = "eng",
        diarize: bool = True,
        tag_audio_events: bool = True
    ) -> None:
        """
        Process all MP3 files in directory.
        
        Args:
            directory: Directory to process (default: current directory)
            language_code: Language code for transcription
            diarize: Whether to identify speakers
            tag_audio_events: Whether to tag audio events
        """
        if directory is None:
            directory = Path.cwd()

        audio_files = sorted(directory.glob("*.mp3"))

        if not audio_files:
            print("No MP3 files found in directory")
            return

        print(f"\nFound {len(audio_files)} MP3 files to transcribe")
        print("=" * 60)

        successful = 0
        failed = 0
        skipped = 0

        for file_path in audio_files:
            try:
                # Skip if transcription already exists
                txt_path = file_path.with_suffix(".txt")
                if txt_path.exists():
                    print(f"\n{file_path.name}")
                    print(f"  ⊘ Already transcribed: {txt_path.name}")
                    skipped += 1
                    continue

                # Transcribe
                transcription_text = self.transcribe_file(
                    file_path,
                    language_code=language_code,
                    diarize=diarize,
                    tag_audio_events=tag_audio_events
                )
                
                if transcription_text:
                    # Save transcription
                    if self.save_transcription(transcription_text, txt_path):
                        successful += 1
                    else:
                        failed += 1
                else:
                    failed += 1
                    
            except KeyboardInterrupt:
                print("\n\nTranscription interrupted by user")
                break
            except Exception as e:
                print(f"\nUnexpected error processing {file_path.name}: {e}")
                failed += 1

        print("\n" + "=" * 60)
        print(f"Transcription complete!")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Skipped: {skipped}")


def main():
    """Main entry point"""
    try:
        print("ElevenLabs Audio Transcription Client")
        print("=" * 60)
        transcriber = ElevenLabsTranscriber()
        transcriber.process_directory()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Audio Transcription Client
Transcribes all MP3 and MP4 files in the current directory using OpenAI's Whisper API.
API key should be set in environment variable OPENAI_API_KEY or stored in api.ini
"""

import os
import sys
import json
import configparser
from pathlib import Path
from typing import Optional
import subprocess

try:
    import openai
except ImportError:
    print("Error: openai package not installed. Install with: pip install openai")
    sys.exit(1)

try:
    from pydub import AudioSegment
except ImportError:
    print("Error: pydub package not installed. Install with: pip install pydub")
    print("You also need ffmpeg installed on your system")
    sys.exit(1)


class AudioTranscriber:
    """Transcribe audio files using OpenAI Whisper API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize transcriber with API key.
        
        Args:
            api_key: OpenAI API key. If None, will look for it in environment or config.
        """
        if not api_key:
            api_key = self._get_api_key()
        
        if not api_key:
            raise ValueError(
                "No API key found. Set OPENAI_API_KEY environment variable "
                "or ensure elevenlabs section exists in api.ini"
            )
        
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)

    @staticmethod
    def _get_api_key() -> Optional[str]:
        """Get API key from environment or api.ini"""
        # Try environment variable first
        if "OPENAI_API_KEY" in os.environ:
            return os.environ["OPENAI_API_KEY"]
        
        # Try api.ini file
        config_path = Path(__file__).parent / "api.ini"
        if config_path.exists():
            config = configparser.ConfigParser()
            config.read(config_path)
            
            # Check for elevenlabs section (user may have added OpenAI key there)
            if "openai" in config and "api_key" in config["openai"]:
                return config["openai"]["api_key"]
            
            # Also check elevenlabs section in case user wants to clarify
            if "elevenlabs" in config and "api_key" in config["elevenlabs"]:
                print("Warning: Found elevenlabs API key but need OpenAI key for transcription.")
                print("Please add OpenAI API key to api.ini under [openai] section or set OPENAI_API_KEY")
        
        return None

    def extract_audio_to_wav(self, file_path: Path) -> Path:
        """
        Convert MP4 or MP3 to WAV format.
        
        Args:
            file_path: Path to audio/video file
            
        Returns:
            Path to generated WAV file
        """
        wav_path = file_path.with_suffix(".wav")
        
        if wav_path.exists():
            print(f"  WAV already exists: {wav_path.name}")
            return wav_path
        
        try:
            print(f"  Converting to WAV...")
            audio = AudioSegment.from_file(str(file_path))
            audio.export(str(wav_path), format="wav")
            print(f"  ✓ Converted to: {wav_path.name}")
            return wav_path
        except Exception as e:
            print(f"  ✗ Error converting file: {e}")
            return None

    def transcribe_file(self, file_path: Path, keep_wav: bool = False) -> Optional[dict]:
        """
        Transcribe audio file using OpenAI Whisper API.
        
        Args:
            file_path: Path to audio file (MP3 or MP4)
            keep_wav: If True, keep temporary WAV files after transcription
            
        Returns:
            Transcription result or None if error
        """
        print(f"\nTranscribing: {file_path.name}")
        
        # Convert to WAV if needed
        if file_path.suffix.lower() == ".mp4":
            wav_path = self.extract_audio_to_wav(file_path)
            if not wav_path:
                return None
        else:
            wav_path = file_path

        try:
            print(f"  Sending to Whisper API...")
            with open(wav_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"  # Specify English; remove or modify as needed
                )
            
            print(f"  ✓ Transcription complete")
            return transcript
        except Exception as e:
            print(f"  ✗ Transcription failed: {e}")
            return None
        finally:
            # Clean up WAV file if it was temporary
            if file_path.suffix.lower() == ".mp4" and wav_path.exists() and not keep_wav:
                try:
                    wav_path.unlink()
                except:
                    pass

    def save_transcription(self, transcription_text: str, output_path: Path) -> bool:
        """Save transcription to text file"""
        try:
            output_path.write_text(transcription_text, encoding="utf-8")
            print(f"  ✓ Saved to: {output_path.name}")
            return True
        except Exception as e:
            print(f"  ✗ Failed to save transcription: {e}")
            return False

    def process_directory(self, directory: Path = None, keep_wav: bool = False) -> None:
        """
        Process all MP3 and MP4 files in directory.
        
        Args:
            directory: Directory to process (default: current directory)
            keep_wav: If True, keep temporary WAV files
        """
        if directory is None:
            directory = Path.cwd()

        audio_files = sorted(
            list(directory.glob("*.mp3")) + list(directory.glob("*.mp4"))
        )

        if not audio_files:
            print("No MP3 or MP4 files found in directory")
            return

        print(f"\nFound {len(audio_files)} audio files to transcribe")
        print("=" * 60)

        successful = 0
        failed = 0

        for file_path in audio_files:
            try:
                # Skip if transcription already exists
                txt_path = file_path.with_suffix(".txt")
                if txt_path.exists():
                    print(f"\n{file_path.name}")
                    print(f"  ⊘ Already transcribed: {txt_path.name}")
                    continue

                # Transcribe
                transcript = self.transcribe_file(file_path, keep_wav)
                if transcript:
                    # Save transcription
                    if self.save_transcription(transcript.text, txt_path):
                        successful += 1
                    else:
                        failed += 1
                else:
                    failed += 1
            except KeyboardInterrupt:
                print("\n\nTranscription interrupted by user")
                break
            except Exception as e:
                print(f"\nUnexpected error processing {file_path.name}: {e}")
                failed += 1

        print("\n" + "=" * 60)
        print(f"Transcription complete!")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Skipped: {len(audio_files) - successful - failed}")


def main():
    """Main entry point"""
    try:
        transcriber = AudioTranscriber()
        transcriber.process_directory()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
