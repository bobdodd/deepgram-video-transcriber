#!/usr/bin/env python3
"""
MP4 Video Transcription Script using Deepgram API

This script transcribes MP4 video files using Deepgram's speech-to-text API
and outputs the results in various formats (VTT, SRT, TXT, JSON).

Requirements:
    - deepgram-sdk
    - python-dotenv (optional, for environment variables)

Usage:
    python transcribe_video.py input_video.mp4 [--output-format vtt]
"""

import os
import sys
import json
import argparse
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

try:
    from deepgram import DeepgramClient, PrerecordedOptions, FileSource
except ImportError:
    print("Error: deepgram-sdk not installed. Install with: pip install deepgram-sdk")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional


class VideoTranscriber:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the transcriber with Deepgram API key."""
        self.api_key = api_key or os.getenv('DEEPGRAM_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Deepgram API key required. Set DEEPGRAM_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        self.client = DeepgramClient(self.api_key)
    
    def extract_audio(self, video_path: str, output_path: str = None) -> str:
        """Extract audio from video file using ffmpeg."""
        video_path = Path(video_path)
        
        if output_path is None:
            # Create temporary file for audio (M4A format is much more efficient)
            temp_fd, output_path = tempfile.mkstemp(suffix='.m4a', prefix='audio_')
            os.close(temp_fd)  # Close the file descriptor, we just need the path
        
        try:
            # Check if ffmpeg is available
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "ffmpeg is required but not found. Install with: brew install ffmpeg (macOS) "
                "or apt-get install ffmpeg (Linux) or download from https://ffmpeg.org"
            )
        
        print(f"Extracting audio from: {video_path.name}")
        
        # Extract audio using ffmpeg with AAC compression (M4A)
        cmd = [
            'ffmpeg', '-i', str(video_path),
            '-vn',  # No video
            '-acodec', 'aac',  # AAC codec (much more efficient than PCM)
            '-b:a', '64k',  # 64kbps bitrate (good quality for speech)
            '-ar', '16000',  # 16kHz sample rate (optimal for speech recognition)
            '-ac', '1',  # Mono channel
            '-y',  # Overwrite output file
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Show file size comparison
            original_size = video_path.stat().st_size
            audio_size = Path(output_path).stat().st_size
            compression_ratio = (1 - audio_size / original_size) * 100
            
            print(f"Audio extracted to: {output_path}")
            print(f"Size reduction: {original_size / 1024 / 1024:.1f}MB → {audio_size / 1024 / 1024:.1f}MB ({compression_ratio:.1f}% smaller)")
            
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Audio extraction failed: {e.stderr}")
    
    def transcribe_file(self, file_path: str, **options) -> dict:
        """Transcribe a video file using Deepgram API."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"Transcribing: {file_path.name}")
        
        # Check if this is a video file that needs audio extraction
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.webm', '.flv'}
        audio_extensions = {'.wav', '.mp3', '.m4a', '.aac', '.ogg', '.flac'}
        
        file_extension = file_path.suffix.lower()
        audio_file_path = None
        temp_audio_file = None
        
        try:
            if file_extension in video_extensions:
                # Extract audio from video
                temp_audio_file = self.extract_audio(str(file_path))
                audio_file_path = temp_audio_file
            elif file_extension in audio_extensions:
                # Use audio file directly
                audio_file_path = str(file_path)
            else:
                # Try to process as-is (might be audio in unsupported container)
                audio_file_path = str(file_path)
                print(f"Warning: Unknown file type {file_extension}, attempting to process as audio...")
            
            print("Sending audio to Deepgram API...")
            print("Please wait, this may take a few minutes...")
            
            # Default options for transcription
            default_options = {
                "model": "nova-2",
                "smart_format": True,
                "utterances": True,
                "punctuate": True,
                "diarize": True,
                "language": "en-US"
            }
            
            # Override defaults with user options
            default_options.update(options)
            
            transcription_options = PrerecordedOptions(**default_options)
            
            # Read the audio file
            with open(audio_file_path, "rb") as file:
                buffer_data = file.read()
            
            payload: FileSource = {
                "buffer": buffer_data,
            }
            
            # Make the API call
            response = self.client.listen.rest.v("1").transcribe_file(
                payload, transcription_options
            )
            
            # Convert response to dictionary if it's not already
            if hasattr(response, 'to_dict'):
                return response.to_dict()
            elif hasattr(response, '__dict__'):
                return response.__dict__
            else:
                return response
            
        finally:
            # Clean up temporary audio file
            if temp_audio_file and os.path.exists(temp_audio_file):
                try:
                    os.unlink(temp_audio_file)
                    print(f"Cleaned up temporary audio file: {temp_audio_file}")
                except OSError:
                    pass  # Ignore cleanup errors
    
    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to VTT/SRT timestamp format."""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = td.total_seconds() % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    
    def to_vtt(self, response: dict, output_path: str):
        """Convert Deepgram response to VTT format."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            f.write("NOTE\n")
            f.write("Transcription provided by Deepgram\n")
            f.write(f"Created: {datetime.now().isoformat()}\n\n")
            
            if 'results' in response and 'channels' in response['results']:
                channel = response['results']['channels'][0]
                
                if 'alternatives' in channel and channel['alternatives']:
                    words = channel['alternatives'][0].get('words', [])
                    
                    # Group words into utterances based on speaker or time gaps
                    current_utterance = []
                    current_speaker = None
                    last_end_time = 0
                    
                    for word in words:
                        speaker = word.get('speaker', 0)
                        start_time = word.get('start', 0)
                        
                        # Start new utterance if speaker changes or there's a significant gap
                        if (speaker != current_speaker or 
                            (start_time - last_end_time > 2.0) or
                            len(current_utterance) > 20):  # Max words per caption
                            
                            if current_utterance:
                                self._write_vtt_utterance(f, current_utterance, current_speaker)
                            
                            current_utterance = [word]
                            current_speaker = speaker
                        else:
                            current_utterance.append(word)
                        
                        last_end_time = word.get('end', 0)
                    
                    # Write the last utterance
                    if current_utterance:
                        self._write_vtt_utterance(f, current_utterance, current_speaker)
    
    def _write_vtt_utterance(self, file, words: list, speaker: int):
        """Write a single VTT utterance."""
        if not words:
            return
        
        start_time = self.format_timestamp(words[0].get('start', 0))
        end_time = self.format_timestamp(words[-1].get('end', 0))
        text = ' '.join(word.get('word', '') for word in words)
        
        file.write(f"{start_time} --> {end_time}\n")
        file.write(f"<v Speaker {speaker}>{text}\n\n")
    
    def to_srt(self, response: dict, output_path: str):
        """Convert Deepgram response to SRT format."""
        with open(output_path, 'w', encoding='utf-8') as f:
            if 'results' in response and 'channels' in response['results']:
                channel = response['results']['channels'][0]
                
                if 'alternatives' in channel and channel['alternatives']:
                    words = channel['alternatives'][0].get('words', [])
                    
                    # Group words into utterances
                    utterances = []
                    current_utterance = []
                    current_speaker = None
                    last_end_time = 0
                    
                    for word in words:
                        speaker = word.get('speaker', 0)
                        start_time = word.get('start', 0)
                        
                        if (speaker != current_speaker or 
                            (start_time - last_end_time > 2.0) or
                            len(current_utterance) > 20):
                            
                            if current_utterance:
                                utterances.append((current_utterance, current_speaker))
                            
                            current_utterance = [word]
                            current_speaker = speaker
                        else:
                            current_utterance.append(word)
                        
                        last_end_time = word.get('end', 0)
                    
                    if current_utterance:
                        utterances.append((current_utterance, current_speaker))
                    
                    # Write SRT format
                    for i, (words, speaker) in enumerate(utterances, 1):
                        if not words:
                            continue
                        
                        start_time = self.format_timestamp(words[0].get('start', 0)).replace('.', ',')
                        end_time = self.format_timestamp(words[-1].get('end', 0)).replace('.', ',')
                        text = ' '.join(word.get('word', '') for word in words)
                        
                        f.write(f"{i}\n")
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"Speaker {speaker}: {text}\n\n")
    
    def to_txt(self, response: dict, output_path: str):
        """Convert Deepgram response to plain text format."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Transcription created: {datetime.now().isoformat()}\n")
            f.write("=" * 50 + "\n\n")
            
            if 'results' in response and 'channels' in response['results']:
                channel = response['results']['channels'][0]
                
                if 'alternatives' in channel and channel['alternatives']:
                    # Use utterances if available
                    if 'utterances' in channel:
                        for utterance in channel['utterances']:
                            speaker = utterance.get('speaker', 0)
                            text = utterance.get('transcript', '')
                            start = utterance.get('start', 0)
                            
                            timestamp = self.format_timestamp(start)
                            f.write(f"[{timestamp}] Speaker {speaker}: {text}\n\n")
                    else:
                        # Fallback to transcript
                        transcript = channel['alternatives'][0].get('transcript', '')
                        f.write(transcript)
    
    def to_json(self, response: dict, output_path: str):
        """Save the full Deepgram response as JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Transcribe MP4 videos using Deepgram')
    parser.add_argument('input_file', help='Path to MP4 file to transcribe')
    parser.add_argument('--output-format', '-f', choices=['vtt', 'srt', 'txt', 'json', 'all'],
                       default='vtt', help='Output format (default: vtt)')
    parser.add_argument('--output-dir', '-o', help='Output directory (default: same as input)')
    parser.add_argument('--api-key', help='Deepgram API key (or set DEEPGRAM_API_KEY env var)')
    parser.add_argument('--model', default='nova-2', help='Deepgram model to use (default: nova-2)')
    parser.add_argument('--language', default='en-US', help='Language code (default: en-US)')
    
    args = parser.parse_args()
    
    try:
        # Initialize transcriber
        transcriber = VideoTranscriber(api_key=args.api_key)
        
        # Set up output paths
        input_path = Path(args.input_file)
        output_dir = Path(args.output_dir) if args.output_dir else input_path.parent
        output_dir.mkdir(exist_ok=True)
        
        base_name = input_path.stem
        
        # Transcribe the file
        response = transcriber.transcribe_file(
            args.input_file,
            model=args.model,
            language=args.language
        )
        
        # Generate output files
        formats = [args.output_format] if args.output_format != 'all' else ['vtt', 'srt', 'txt', 'json']
        
        for fmt in formats:
            output_path = output_dir / f"{base_name}.{fmt}"
            
            if fmt == 'vtt':
                transcriber.to_vtt(response, output_path)
            elif fmt == 'srt':
                transcriber.to_srt(response, output_path)
            elif fmt == 'txt':
                transcriber.to_txt(response, output_path)
            elif fmt == 'json':
                transcriber.to_json(response, output_path)
            
            print(f"Created: {output_path}")
        
        print("\nTranscription completed successfully!")
        
        # Display basic info
        if 'results' in response and 'channels' in response['results']:
            channel = response['results']['channels'][0]
            if 'alternatives' in channel and channel['alternatives']:
                transcript = channel['alternatives'][0].get('transcript', '')
                word_count = len(transcript.split())
                print(f"Word count: {word_count}")
                
                if 'utterances' in channel:
                    speaker_count = len(set(u.get('speaker', 0) for u in channel['utterances']))
                    print(f"Speakers detected: {speaker_count}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()