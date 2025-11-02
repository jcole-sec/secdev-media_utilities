#!/usr/bin/env python3
"""
Whisper Text Extraction System
Complete video-to-text transcription with progress tracking and resume capability.
"""

import whisper
import os
import time
import json
import glob
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import logging
import shutil

class WhisperTranscriptionManager:
    """Manages complete video transcription with progress tracking"""
    
    def __init__(self, source_video, output_dir="transcripts", model_name="base"):
        self.source_video = source_video
        self.output_dir = Path(output_dir)
        self.model_name = model_name
        
        # Generate base filename from source video
        video_name = Path(source_video).stem
        
        self.output_dir.mkdir(exist_ok=True)
        self.setup_logging()
        
        self.total_duration = None
        self.processed_duration = 0
        self.start_time = None
        self.model = None
        self.segment_minutes = 30
        self.max_retries = 3
        
        self.progress_file = self.output_dir / "transcription_progress.json"
        self.final_transcript = self.output_dir / f"{video_name}_transcript.txt"
        self.final_srt = self.output_dir / f"{video_name}_subtitles.srt"
        self.final_json = self.output_dir / f"{video_name}_data.json"
        self.segments_dir = self.output_dir / "segments"
        self.segments_dir.mkdir(exist_ok=True)
    
    def setup_logging(self):
        log_file = self.output_dir / "transcription.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_whisper_model(self):
        if self.model is None:
            self.logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            self.logger.info("Whisper model loaded successfully")
    
    def get_video_duration(self):
        if self.total_duration is not None:
            return self.total_duration
            
        try:
            cmd = ["ffmpeg", "-i", str(self.source_video), "-f", "null", "-"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            for line in result.stdout.split("\n"):
                if "Duration:" in line:
                    duration_str = line.split("Duration:")[1].split(",")[0].strip()
                    parts = duration_str.split(":")
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = float(parts[2])
                    
                    self.total_duration = hours * 3600 + minutes * 60 + seconds
                    self.logger.info(f"Video duration: {duration_str} ({self.total_duration:.1f} seconds)")
                    return self.total_duration
            
            raise ValueError("Could not parse video duration from FFmpeg output")
            
        except Exception as e:
            self.logger.error(f"Error getting video duration: {e}")
            raise
    
    def extract_audio_segment(self, start_seconds, duration_seconds, output_file):
        try:
            cmd = [
                "ffmpeg", "-i", str(self.source_video),
                "-ss", str(start_seconds),
                "-t", str(duration_seconds),
                "-vn", "-ac", "1", "-ar", "16000",
                "-acodec", "pcm_s16le",
                "-y", str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
            return os.path.exists(output_file)
            
        except Exception as e:
            self.logger.error(f"Error extracting audio segment: {e}")
            return False
    
    def seconds_to_srt_timestamp(self, seconds):
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{seconds:06.3f}".replace(".", ",")
    
    def transcribe_segment(self, audio_file, segment_start_time):
        self.load_whisper_model()
        
        try:
            self.logger.info(f"Transcribing segment: {audio_file}")
            
            result = self.model.transcribe(
                str(audio_file),
                verbose=False,
                word_timestamps=True,
                language="en"
            )
            
            for segment in result["segments"]:
                segment["start"] += segment_start_time
                segment["end"] += segment_start_time
                if "words" in segment:
                    for word in segment["words"]:
                        word["start"] += segment_start_time
                        word["end"] += segment_start_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error transcribing segment {audio_file}: {e}")
            return None
    
    def save_progress(self, processed_segments, current_segment=None):
        progress_data = {
            "timestamp": datetime.now().isoformat(),
            "processed_segments": processed_segments,
            "current_segment": current_segment,
            "total_duration": self.total_duration,
            "segment_minutes": self.segment_minutes
        }
        
        try:
            with open(self.progress_file, "w") as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving progress: {e}")
    
    def load_progress(self):
        if not self.progress_file.exists():
            return [], 0
        
        try:
            with open(self.progress_file, "r") as f:
                progress_data = json.load(f)
            
            processed_segments = progress_data.get("processed_segments", [])
            current_segment = progress_data.get("current_segment", 0)
            
            self.logger.info(f"Resuming from segment {current_segment}, {len(processed_segments)} segments completed")
            return processed_segments, current_segment
            
        except Exception as e:
            self.logger.error(f"Error loading progress: {e}")
            return [], 0
    
    def update_progress_display(self, current_segment, total_segments, segment_duration):
        if self.start_time is None:
            self.start_time = time.time()
        
        elapsed_time = time.time() - self.start_time
        progress_percent = (current_segment / total_segments) * 100
        
        if current_segment > 0:
            time_per_segment = elapsed_time / current_segment
            remaining_segments = total_segments - current_segment
            eta_seconds = remaining_segments * time_per_segment
            eta_str = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta_str = "Calculating..."
        
        self.logger.info(f"Progress: {current_segment}/{total_segments} ({progress_percent:.1f}%) | "
                        f"Elapsed: {timedelta(seconds=int(elapsed_time))} | ETA: {eta_str}")
    
    def combine_results(self, all_results):
        self.logger.info("Combining transcription results...")
        
        full_text = ""
        full_srt = ""
        full_json_data = {
            "text": "",
            "segments": [],
            "language": "en"
        }
        
        srt_counter = 1
        
        for result in all_results:
            if result:
                full_text += result["text"] + "\n"
                full_json_data["segments"].extend(result["segments"])
                
                for segment in result["segments"]:
                    start_time = self.seconds_to_srt_timestamp(segment["start"])
                    end_time = self.seconds_to_srt_timestamp(segment["end"])
                    
                    full_srt += f"{srt_counter}\n"
                    full_srt += f"{start_time} --> {end_time}\n"
                    full_srt += f'{segment["text"].strip()}\n\n'
                    srt_counter += 1
        
        full_json_data["text"] = full_text.strip()
        
        try:
            with open(self.final_transcript, "w", encoding="utf-8") as f:
                f.write(full_text.strip())
            
            with open(self.final_srt, "w", encoding="utf-8") as f:
                f.write(full_srt)
            
            with open(self.final_json, "w", encoding="utf-8") as f:
                json.dump(full_json_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Transcription saved:")
            self.logger.info(f"   Text: {self.final_transcript}")
            self.logger.info(f"   SRT:  {self.final_srt}")
            self.logger.info(f"   JSON: {self.final_json}")
            
        except Exception as e:
            self.logger.error(f"Error saving combined results: {e}")
    
    def transcribe_complete_video(self, resume=True):
        self.logger.info("Starting complete video transcription...")
        
        total_duration = self.get_video_duration()
        segment_duration = self.segment_minutes * 60
        total_segments = int((total_duration + segment_duration - 1) // segment_duration)
        
        self.logger.info(f"Video: {self.source_video}")
        self.logger.info(f"Duration: {timedelta(seconds=int(total_duration))}")
        self.logger.info(f"Segments: {total_segments} x {self.segment_minutes}min each")
        
        processed_segments, start_segment = ([], 0) if not resume else self.load_progress()
        all_results = []
        
        if resume and processed_segments:
            for i in range(len(processed_segments)):
                segment_file = self.segments_dir / f"segment_{i+1:03d}_transcript.json"
                if segment_file.exists():
                    try:
                        with open(segment_file, "r") as f:
                            result = json.load(f)
                        all_results.append(result)
                    except Exception as e:
                        self.logger.warning(f"Could not load segment {i+1}: {e}")
                        all_results.append(None)
                else:
                    all_results.append(None)
        
        for segment_num in range(start_segment, total_segments):
            if segment_num < len(processed_segments):
                continue
            
            self.logger.info(f"\nProcessing segment {segment_num + 1}/{total_segments}")
            
            start_time = segment_num * segment_duration
            current_segment_duration = min(segment_duration, total_duration - start_time)
            
            audio_file = Path(f"temp_segment_{segment_num + 1:03d}.wav")
            
            if not self.extract_audio_segment(start_time, current_segment_duration, audio_file):
                self.logger.error(f"Failed to extract segment {segment_num + 1}")
                continue
            
            result = self.transcribe_segment(audio_file, start_time)
            
            if result:
                segment_file = self.segments_dir / f"segment_{segment_num + 1:03d}_transcript.json"
                try:
                    with open(segment_file, "w") as f:
                        json.dump(result, f, indent=2)
                except Exception as e:
                    self.logger.error(f"Error saving segment result: {e}")
                
                all_results.append(result)
                processed_segments.append(segment_num + 1)
            else:
                all_results.append(None)
            
            self.update_progress_display(segment_num + 1, total_segments, current_segment_duration)
            self.save_progress(processed_segments, segment_num + 1)
            
            if audio_file.exists():
                audio_file.unlink()
        
        if all_results:
            self.combine_results(all_results)
            
            total_time = time.time() - self.start_time if self.start_time else 0
            self.logger.info(f"TRANSCRIPTION COMPLETE!")
            self.logger.info(f"Total processing time: {timedelta(seconds=int(total_time))}")
            self.logger.info(f"Processed segments: {len(processed_segments)}/{total_segments}")
        else:
            self.logger.error("No segments were successfully transcribed")

def interactive_transcribe():
    """Interactive launcher for transcription"""
    print("Whisper Transcription System")
    print("=" * 40)
    
    video_path = input("Enter path to video file: ").strip('"')
    if not os.path.exists(video_path):
        print("Error: Video file not found. Exiting.")
        return
    
    models = ["tiny", "base", "small", "medium", "large"]
    print("\nAvailable Whisper models:")
    for i, model in enumerate(models, 1):
        descriptions = {
            "tiny": "Fastest, lowest accuracy (~1GB VRAM)",
            "base": "Good balance (~1GB VRAM) [RECOMMENDED]", 
            "small": "Better accuracy (~2GB VRAM)",
            "medium": "High accuracy (~5GB VRAM)",
            "large": "Best accuracy (~10GB VRAM)"
        }
        print(f"  {i}. {model} - {descriptions.get(model, '')}")
    
    try:
        choice = input(f"\nSelect model (1-{len(models)}, default=2): ").strip() or "2"
        model = models[int(choice)-1]
    except:
        model = "base"
        print("Using default model: base")
    
    try:
        segment_minutes = int(input("Segment duration in minutes (default=30): ") or 30)
    except:
        segment_minutes = 30
    
    resume = input("Resume from existing progress? (Y/n): ").strip().lower() != 'n'
    
    print(f"\nStarting transcription:")
    print(f"   Video: {os.path.basename(video_path)}")
    print(f"   Model: {model}")
    print(f"   Segments: {segment_minutes} minutes")
    print(f"   Resume: {'Yes' if resume else 'No'}")
    
    manager = WhisperTranscriptionManager(video_path, model_name=model)
    manager.segment_minutes = segment_minutes
    
    try:
        manager.transcribe_complete_video(resume=resume)
    except KeyboardInterrupt:
        print("\nTranscription interrupted. Progress saved.")
    except Exception as e:
        print(f"\nError during transcription: {e}")

def cleanup_transcription_files():
    """Clean up temporary transcription files"""
    print("Transcription Cleanup Utility")
    print("=" * 40)
    
    cleanup_items = [
        "*_segment_*.wav", "transcript_*.txt", "whisper_transcript_*.txt", "whisper_transcript_*.srt",
        "temp_minute_*.wav", "temp_segment_*.wav", "*.tmp"
    ]
    
    cleaned_count = 0
    
    for pattern in cleanup_items:
        for match in glob.glob(pattern):
            try:
                os.remove(match)
                print(f"  Removed: {match}")
                cleaned_count += 1
            except Exception as e:
                print(f"  Error removing {match}: {e}")
    
    for dir_name in ["segments"]:
        if os.path.isdir(dir_name):
            if input(f"\nRemove directory '{dir_name}' and all contents? (y/N): ").strip().lower() == 'y':
                try:
                    shutil.rmtree(dir_name)
                    print(f"  Removed directory: {dir_name}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"  Error removing {dir_name}: {e}")
    
    print(f"\nCleanup complete. Items removed: {cleaned_count}")

def show_disk_usage():
    """Show disk usage analysis"""
    print("Disk Usage Analysis")
    print("=" * 30)
    
    total_size = 0
    
    # Check for audio files
    for audio_file in glob.glob("*.wav"):
        if os.path.exists(audio_file):
            size = os.path.getsize(audio_file)
            print(f"  {audio_file}: {size/1024/1024:.1f} MB")
            total_size += size
    
    # Check transcripts directory
    if os.path.isdir("transcripts"):
        transcripts_size = sum(
            f.stat().st_size for f in Path("transcripts").rglob("*") if f.is_file()
        )
        print(f"  transcripts/: {transcripts_size/1024/1024:.1f} MB")
        total_size += transcripts_size
    
    print(f"  Total: {total_size/1024/1024:.1f} MB")

def main():
    parser = argparse.ArgumentParser(
        description='Whisper Text Extraction System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                                    # Interactive mode
  %(prog)s transcribe                         # Interactive transcription
  %(prog)s transcribe --video video.mp4      # Direct transcription
  %(prog)s cleanup                           # Clean temporary files
  %(prog)s disk-usage                        # Show disk usage
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    p_transcribe = subparsers.add_parser('transcribe', help='Run video transcription')
    p_transcribe.add_argument('--video', help='Path to source video file')
    p_transcribe.add_argument('--output', default='transcripts', help='Output directory (default: transcripts)')
    p_transcribe.add_argument('--model', default='base', 
                             choices=['tiny', 'base', 'small', 'medium', 'large'], 
                             help='Whisper model to use (default: base)')
    p_transcribe.add_argument('--segment-minutes', type=int, default=30, 
                             help='Segment duration in minutes (default: 30)')
    p_transcribe.add_argument('--no-resume', action='store_true', 
                             help='Start from beginning, ignore existing progress')
    
    subparsers.add_parser('cleanup', help='Clean up temporary transcription files')
    subparsers.add_parser('disk-usage', help='Show disk usage analysis')
    
    args = parser.parse_args()
    
    if args.command == 'transcribe':
        if args.video:
            print(f"Whisper Transcription System")
            print("=" * 50)
            print(f"Video: {args.video}")
            print(f"Model: {args.model}")
            print(f"Output: {args.output}")
            print(f"Segments: {args.segment_minutes} minutes")
            print(f"Resume: {'No' if args.no_resume else 'Yes'}")
            print("=" * 50)
            
            manager = WhisperTranscriptionManager(
                source_video=args.video,
                output_dir=args.output,
                model_name=args.model
            )
            manager.segment_minutes = args.segment_minutes
            
            try:
                manager.transcribe_complete_video(resume=not args.no_resume)
            except KeyboardInterrupt:
                print("\nTranscription interrupted. Progress saved.")
            except Exception as e:
                print(f"\nError during transcription: {e}")
        else:
            interactive_transcribe()
    
    elif args.command == 'cleanup':
        cleanup_transcription_files()
    
    elif args.command == 'disk-usage':
        show_disk_usage()
    
    else:
        interactive_transcribe()

if __name__ == "__main__":
    main()
