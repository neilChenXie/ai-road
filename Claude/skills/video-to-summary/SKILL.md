---
name: video-to-summary
description: Convert video URLs to text summaries with speech-to-text transcription. Supports Bilibili (B站), YouTube, TikTok, XiaoHongShu (小红书), Twitter, and other platforms. Use when users provide video URLs and want to: (1) Extract and transcribe audio content, (2) Generate text summaries from videos, (3) Download and process video content for analysis. Triggers on phrases like "视频转文字", "视频总结", "transcribe video", "summarize video", "提取视频内容".
---

# Video to Summary V2

An optimized video-to-text tool with automatic speech recognition and intelligent summarization.

## Quick Start

### One-time Setup

```bash
# Run the installation script (recommended)
bash install.sh

# Or manually install dependencies
pipx install openai-whisper  # Whisper (manages its own venv)
pip3 install --break-system-packages yt-dlp requests beautifulsoup4 pyyaml  # System packages
```

### Process a Video

```bash
# Basic usage
python3 scripts/video_to_summary.py --url "https://www.youtube.com/watch?v=xxx"

# With specific output directory
python3 scripts/video_to_summary.py --url "URL" --output-dir ./output

# Audio only mode (faster)
python3 scripts/video_to_summary.py --url "URL" --audio-only
```

## Supported Platforms

| Platform | Support Level | Notes |
|----------|--------------|-------|
| **Bilibili (B站)** | Excellent | Official API support |
| **YouTube** | Good | May require cookies |
| **XiaoHongShu (小红书)** | Good | Auto-detects cookies |
| **TikTok** | Good | Standard support |
| **Twitter/X** | Good | Standard support |
| **Other** | Variable | Any platform supported by yt-dlp |

## Key Improvements (V2)

- 🚀 **Auto dependency management** - One-command setup
- 🎯 **Better platform support** - Smart cookie detection
- 📝 **Auto summarization** - No manual work needed
- 🔧 **Better error handling** - Clear messages and fixes
- 📊 **Structured output** - JSON + Markdown formats
- ⚙️ **Configurable** - YAML-based settings

## Installation

### Prerequisites

```bash
# Install FFmpeg (system dependency)
brew install ffmpeg          # macOS
# or
sudo apt-get install ffmpeg  # Ubuntu/Debian
```

### One-line Install

```bash
bash install.sh
```

This will:
1. Check Python version (requires 3.8+)
2. Install Whisper using pipx (auto-managed venv)
3. Install system dependencies
4. Create necessary directories

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
# Whisper settings
whisper:
  model: base           # tiny/base/small/medium/large
  language: zh          # auto/detect
  temperature: 0.0

# Download settings
download:
  use_cookies: true
  cookies_browser: chrome
  audio_only: false
  timeout: 300

# Output settings
output:
  format: [txt, json, md]
  include_summary: true
  cleanup_temp: true
```

## Usage Examples

### Basic Usage

```bash
# Process YouTube video
python3 scripts/video_to_summary.py --url "https://youtube.com/watch?v=xxx"

# Process Bilibili video
python3 scripts/video_to_summary.py --url "https://b23.tv/xxx"

# Process XiaoHongShu video
python3 scripts/video_to_summary.py --url "https://www.xiaohongshu.com/..."
```

### Advanced Options

```bash
# Specify Whisper model for better accuracy
python3 scripts/video_to_summary.py --url "URL" --model medium

# Audio only mode (faster, smaller)
python3 scripts/video_to_summary.py --url "URL" --audio-only

# Custom output directory
python3 scripts/video_to_summary.py --url "URL" --output-dir ~/videos/analysis

# Disable auto cleanup to keep intermediate files
python3 scripts/video_to_summary.py --url "URL" --keep-temp
```

## Output Structure

```
output/
├── video_id/
│   ├── info.json              # Video metadata
│   ├── transcript.json         # Full transcript with timestamps
│   ├── transcript.txt         # Plain text transcript
│   ├── summary.md             # AI-generated summary
│   └── audio.mp3              # Extracted audio (if not audio-only)
```

## Output Format

### Transcript (JSON)

```json
{
  "video_id": "xxx",
  "platform": "youtube",
  "title": "Video Title",
  "duration": 292.22,
  "transcript": [
    {
      "start": 0.0,
      "end": 3.2,
      "text": "这是第一句话"
    }
  ]
}
```

### Summary (Markdown)

```markdown
# 视频标题

## 概述
视频的简要概述...

## 关键点
- 要点1
- 要点2

## 详细内容
详细总结...
```

## Platform-Specific Notes

### XiaoHongShu (小红书)
- Auto-detects and uses Chrome cookies if available
- Falls back to standard download if cookies fail
- May require user interaction for some private videos

### YouTube
- Age-restricted content requires cookies
- Use `--cookies-from-browser` flag or configure in `config.yaml`

### Bilibili
- Uses official API to bypass 412 errors
- Supports short links (b23.tv)
- No cookies required for public videos

## Troubleshooting

### "python3: command not found"
```bash
# Install Python 3
brew install python3  # macOS
sudo apt install python3  # Ubuntu
```

### "ModuleNotFoundError: No module named 'xxx'"
```bash
# Re-run install script
bash install.sh
```

### "Whisper not found"
```bash
# Whisper is managed by pipx
pipx ensurepath
pipx install openai-whisper
```

### "Video download failed"
- Check URL is valid
- For restricted content, ensure cookies are configured
- Try with `--use-cookies` flag

### Poor transcription quality
```bash
# Use larger model
python3 scripts/video_to_summary.py --url "URL" --model medium

# Or
python3 scripts/video_to_summary.py --url "URL" --model large
```

## Performance Tips

| Scenario | Whisper Model | Speed | Quality |
|----------|--------------|-------|---------|
| Quick test | tiny | Very Fast | Fair |
| General use | base | Fast | Good |
| High quality | medium | Medium | Very Good |
| Best quality | large | Slow | Excellent |

## Development

### Project Structure

```
video-to-summary-v2/
├── SKILL.md                 # This file
├── config.yaml              # Configuration
├── requirements.txt         # Python dependencies
├── install.sh              # Installation script
└── scripts/
    ├── video_to_summary.py # Main script
    └── utils/
        ├── __init__.py
        ├── platform_detector.py  # Platform detection
        ├── video_downloader.py   # Video download
        ├── audio_extractor.py    # Audio extraction
        ├── speech_to_text.py     # Speech recognition
        ├── text_summarizer.py    # Text summarization
        ├── dependency_checker.py # Dependency checking
        └── logger.py            # Logging utilities
```

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a PR.
