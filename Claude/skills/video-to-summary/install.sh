#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. Not recommended."
fi

# Check Python version
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    print_info "Found Python $PYTHON_VERSION"

    # Check if version is >= 3.8
    if [ "$(echo "$PYTHON_VERSION" | cut -d. -f1)" -lt 3 ] || [ "$(echo "$PYTHON_VERSION" | cut -d. -f2)" -lt 8 ]; then
        print_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 is not installed. Please install it first."
    exit 1
fi

# Check FFmpeg
print_info "Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1)
    print_info "Found FFmpeg"
else
    print_error "FFmpeg is not installed."
    echo ""
    echo "Please install FFmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    exit 1
fi

# Check/install yt-dlp
print_info "Checking yt-dlp..."
if command -v yt-dlp &> /dev/null; then
    YTDLP_VERSION=$(yt-dlp --version)
    print_info "Found yt-dlp $YTDLP_VERSION"
else
    print_info "Installing yt-dlp..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install yt-dlp
    else
        pip3 install --break-system-packages yt-dlp
    fi
fi

# Check/install pipx
print_info "Checking pipx..."
if command -v pipx &> /dev/null; then
    print_info "Found pipx"
else
    print_info "Installing pipx..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install pipx
    else
        python3 -m pip install --user pipx
        pipx ensurepath
    fi
fi

# Install Whisper via pipx
print_info "Checking Whisper..."
if command -v whisper &> /dev/null; then
    print_info "Found Whisper"
else
    print_info "Installing Whisper (this may take a while)..."
    pipx install openai-whisper
fi

# Install Python dependencies
print_info "Installing Python dependencies..."
pip3 install --break-system-packages -r requirements.txt 2>/dev/null || {
    print_warning "Could not install system-wide packages. You may need to use a virtual environment."
    print_info "Creating virtual environment at ./venv..."
    python3 -m venv ./venv
    source ./venv/bin/activate
    pip install -r requirements.txt
}

# Create output directory
print_info "Creating output directory..."
mkdir -p output

# Make script executable
chmod +x scripts/video_to_summary.py 2>/dev/null || true

echo ""
print_info "Installation complete!"
echo ""
echo "Quick start:"
echo "  python3 scripts/video_to_summary.py --url \"https://youtube.com/watch?v=xxx\""
echo ""
echo "For more information, see SKILL.md"
