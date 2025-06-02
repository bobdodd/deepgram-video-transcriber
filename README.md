# Deepgram Video Transcriber

A Python script that uses Deepgram's API to transcribe MP4 video files and generate captions in multiple formats.

## Features

- Transcribe MP4 video files using Deepgram's speech-to-text API
- Output formats: VTT, SRT, TXT, JSON
- Speaker diarization (identifies different speakers)
- Smart formatting with punctuation
- Configurable models and languages
- Error handling and progress feedback

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get a Deepgram API key:
   - Sign up at [Deepgram](https://console.deepgram.com/)
   - Create an API key from your dashboard

3. Set your API key (choose one method):
   - Environment variable: `export DEEPGRAM_API_KEY=your_api_key_here`
   - Create a `.env` file: `DEEPGRAM_API_KEY=your_api_key_here`
   - Pass it as a command line argument: `--api-key your_api_key_here`

## Usage

### Basic usage:
```bash
python transcribe_video.py video.mp4
```

### With options:
```bash
python transcribe_video.py video.mp4 --output-format srt --output-dir ./transcripts
```

### Generate all formats:
```bash
python transcribe_video.py video.mp4 --output-format all
```

## Command Line Options

- `input_file`: Path to MP4 file to transcribe (required)
- `--output-format, -f`: Output format (vtt, srt, txt, json, all) [default: vtt]
- `--output-dir, -o`: Output directory [default: same as input file]
- `--api-key`: Deepgram API key [default: from environment]
- `--model`: Deepgram model to use [default: nova-2]
- `--language`: Language code [default: en-US]

## Output Formats

### VTT (Web Video Text Tracks)
- Standard web caption format
- Includes speaker identification
- Compatible with HTML5 video players

### SRT (SubRip Text)
- Popular subtitle format
- Numbered captions with timestamps
- Compatible with most video players

### TXT (Plain Text)
- Simple text transcript
- Includes timestamps and speaker labels
- Easy to read and edit

### JSON
- Complete Deepgram API response
- Includes word-level timestamps
- Confidence scores and metadata

## Examples

### Environment setup:
```bash
# Create .env file
echo "DEEPGRAM_API_KEY=your_api_key_here" > .env

# Transcribe with VTT output
python transcribe_video.py meeting.mp4

# Generate all formats
python transcribe_video.py interview.mp4 -f all -o ./output

# Use different model and language
python transcribe_video.py spanish_video.mp4 --model nova-2 --language es
```

### Programmatic usage:
```python
from transcribe_video import VideoTranscriber

# Initialize with API key
transcriber = VideoTranscriber(api_key="your_api_key")

# Transcribe file
response = transcriber.transcribe_file("video.mp4")

# Generate VTT captions
transcriber.to_vtt(response, "captions.vtt")

# Generate SRT subtitles
transcriber.to_srt(response, "subtitles.srt")
```

## Supported Models

- `nova-2`: Latest and most accurate (recommended)
- `nova`: Fast and accurate
- `enhanced`: Good balance of speed and accuracy
- `base`: Fastest, lower accuracy

## Supported Languages

Common language codes:
- `en-US`: English (US)
- `en-GB`: English (UK)
- `es`: Spanish
- `fr`: French
- `de`: German
- `it`: Italian
- `pt`: Portuguese
- `ja`: Japanese
- `ko`: Korean
- `zh`: Chinese

## Error Handling

The script includes comprehensive error handling for:
- Missing API key
- Invalid file paths
- Network connectivity issues
- API rate limits
- Unsupported file formats

## Notes

- Processing time depends on video length and selected model
- Longer videos may take several minutes to process
- The script requires an active internet connection
- Deepgram charges per minute of audio processed

## Troubleshooting

### "deepgram-sdk not installed"
```bash
pip install deepgram-sdk
```

### "API key required"
Make sure your API key is set in environment variables or passed as an argument.

### "File not found"
Check that the MP4 file path is correct and the file exists.

### API errors
- Check your Deepgram account balance
- Verify your API key is valid
- Ensure the file format is supported