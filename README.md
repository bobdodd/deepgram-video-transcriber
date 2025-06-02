# Deepgram Video Transcriber

A Python script that uses Deepgram's API to transcribe MP4 video files and generate captions in multiple formats.

## Features

- **Efficient Audio Extraction**: Automatically extracts audio from video files using FFmpeg with M4A compression
- **Multiple Input Formats**: Supports MP4, MOV, AVI, MKV, and direct audio files (WAV, MP3, M4A, etc.)
- **Highly Optimized**: Converts to compressed M4A format (typically 95%+ size reduction) for faster uploads
- **Multiple Output Formats**: VTT, SRT, TXT, JSON
- **Speaker Diarization**: Identifies different speakers
- **Smart Formatting**: Automatic punctuation and formatting
- **Configurable Options**: Different models and languages
- **Error Handling**: Comprehensive error handling and progress feedback

## Installation

### 1. Install FFmpeg (Required)

FFmpeg is required for extracting audio from video files. Choose your platform:

#### macOS

**Option A: Using Homebrew (Recommended)**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg

# Verify installation
ffmpeg -version
```

**Option B: Using MacPorts**
```bash
sudo port install ffmpeg
```

**Option C: Download Binary**
- Download from [https://ffmpeg.org/download.html#build-mac](https://ffmpeg.org/download.html#build-mac)
- Extract and add to your PATH

#### Linux

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

**CentOS/RHEL/Fedora:**
```bash
# Enable RPM Fusion repository first
sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm

# Install FFmpeg
sudo dnf install ffmpeg

# For older systems using yum
sudo yum install ffmpeg
```

**Arch Linux:**
```bash
sudo pacman -S ffmpeg
```

#### Windows

**Option A: Using Chocolatey (Recommended)**
```powershell
# Install Chocolatey if you don't have it
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg

# Verify installation
ffmpeg -version
```

**Option B: Using Scoop**
```powershell
# Install Scoop if you don't have it
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Install FFmpeg
scoop install ffmpeg
```

**Option C: Manual Installation**
1. Download FFmpeg from [https://ffmpeg.org/download.html#build-windows](https://ffmpeg.org/download.html#build-windows)
2. Extract the zip file to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Click "Environment Variables"
   - Under "System Variables", find and select "Path", click "Edit"
   - Click "New" and add `C:\ffmpeg\bin`
   - Click "OK" to save

#### Docker Alternative

If you prefer using Docker:
```bash
# Build with FFmpeg included
docker run --rm -v $(pwd):/workspace python:3.11-slim bash -c "
  apt-get update && apt-get install -y ffmpeg && 
  cd /workspace && 
  pip install -r requirements.txt && 
  python transcribe_video.py --help
"
```

### 2. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Installation

Test that everything is working:
```bash
# Check FFmpeg
ffmpeg -version

# Check Python script
python transcribe_video.py --help
```

3. Get a Deepgram API key:
   - Sign up at [Deepgram](https://console.deepgram.com/)
   - Create an API key from your dashboard

4. Set your API key (choose one method):
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

### FFmpeg Installation Issues

**"ffmpeg: command not found" or "ffmpeg is required but not found"**

1. **Verify PATH**: Make sure FFmpeg is in your system PATH
   ```bash
   # Check if FFmpeg is accessible
   which ffmpeg
   ffmpeg -version
   ```

2. **macOS specific**:
   - If Homebrew installation failed: `brew doctor` then `brew install ffmpeg`
   - If using Apple Silicon: Make sure you have ARM64 version of Homebrew
   - Permission issues: `sudo chown -R $(whoami) $(brew --prefix)/*`

3. **Windows specific**:
   - Restart command prompt/PowerShell after adding to PATH
   - Use full path if PATH not working: `C:\ffmpeg\bin\ffmpeg.exe`
   - Verify PATH: `echo $env:PATH` (PowerShell) or `echo %PATH%` (CMD)

4. **Linux specific**:
   - Update package manager: `sudo apt update` or `sudo yum update`
   - Try alternative repositories if FFmpeg not found
   - Build from source if package unavailable

### Python/Dependencies Issues

**"deepgram-sdk not installed"**
```bash
pip install deepgram-sdk
```

**"No module named 'deepgram'"**
- Activate virtual environment: `source venv/bin/activate`
- Install in correct environment: `pip install -r requirements.txt`

**"externally-managed-environment" error**
```bash
# Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or use --break-system-packages (not recommended)
pip install -r requirements.txt --break-system-packages
```

### API and Authentication Issues

**"API key required"**
- Set environment variable: `export DEEPGRAM_API_KEY=your_key_here`
- Create .env file: `echo "DEEPGRAM_API_KEY=your_key_here" > .env`
- Pass as argument: `--api-key your_key_here`

**"Invalid API key" or "Authentication failed"**
- Verify key is correct (no extra spaces/characters)
- Check account status at [Deepgram Console](https://console.deepgram.com/)
- Ensure key has proper permissions

**"Rate limit exceeded" or "Quota exceeded"**
- Check account balance and usage limits
- Wait before retrying or upgrade plan
- Consider splitting large files

### File Processing Issues

**"File not found"**
- Use absolute paths: `/full/path/to/video.mp4`
- Check file permissions: `ls -la your_file.mp4`
- Verify file exists and is accessible

**"Audio extraction failed"**
- Check FFmpeg can read the file: `ffmpeg -i your_file.mp4`
- Try different file format or convert first
- Check available disk space for temporary files

**"The write operation timed out"**
- Large files may take time - be patient
- Check internet connection
- Try smaller files first to test setup

### Performance Issues

**Very slow processing**
- Ensure using M4A extraction (this script does automatically)
- Check internet connection speed
- Monitor disk space for temporary files

**Out of memory errors**
- Close other applications
- Try smaller video files
- Increase system virtual memory

### Getting Help

If you continue having issues:

1. **Check the error message carefully** - it often contains the solution
2. **Verify all prerequisites** are installed correctly
3. **Test with a small file first** (under 50MB)
4. **Check your internet connection** and Deepgram account status
5. **Update to latest versions** of Python, FFmpeg, and dependencies

**Common working setup:**
- Python 3.8+ with virtual environment
- FFmpeg 4.0+ properly installed in PATH
- Valid Deepgram API key with sufficient balance
- Stable internet connection