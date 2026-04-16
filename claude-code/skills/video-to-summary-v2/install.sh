#!/bin/bash
#
# Video to Summary V2 - Installation Script
# Installs all required dependencies for video processing
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Video to Summary V2 - 安装脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python version
check_python() {
    echo -e "${YELLOW}[1/5] 检查 Python...${NC}"

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION 已安装"
        return 0
    else
        echo -e "  ${RED}✗${NC} Python3 未安装"
        echo -e "  请安装 Python 3.8+ : brew install python3"
        return 1
    fi
}

# Check FFmpeg
check_ffmpeg() {
    echo -e "${YELLOW}[2/5] 检查 FFmpeg...${NC}"

    if command -v ffmpeg &> /dev/null; then
        FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
        echo -e "  ${GREEN}✓${NC} FFmpeg $FFMPEG_VERSION 已安装"
        return 0
    else
        echo -e "  ${RED}✗${NC} FFmpeg 未安装"
        echo -e "  正在尝试安装..."
        if command -v brew &> /dev/null; then
            brew install ffmpeg
            echo -e "  ${GREEN}✓${NC} FFmpeg 安装完成"
            return 0
        else
            echo -e "  ${YELLOW}!${NC} 请手动安装: brew install ffmpeg 或 apt install ffmpeg"
            return 1
        fi
    fi
}

# Check yt-dlp
check_ytdlp() {
    echo -e "${YELLOW}[3/5] 检查 yt-dlp...${NC}"

    if command -v yt-dlp &> /dev/null; then
        YT_VERSION=$(yt-dlp --version 2>&1)
        echo -e "  ${GREEN}✓${NC} yt-dlp $YT_VERSION 已安装"
        return 0
    else
        echo -e "  ${RED}✗${NC} yt-dlp 未安装"
        echo -e "  正在尝试安装..."

        # Try pip first
        if pip3 install yt-dlp 2>/dev/null || pip install yt-dlp 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} yt-dlp 安装完成"
            return 0
        # Try brew
        elif command -v brew &> /dev/null; then
            brew install yt-dlp
            echo -e "  ${GREEN}✓${NC} yt-dlp 安装完成"
            return 0
        else
            echo -e "  ${YELLOW}!${NC} 请手动安装: pip install yt-dlp 或 brew install yt-dlp"
            return 1
        fi
    fi
}

# Check Whisper
check_whisper() {
    echo -e "${YELLOW}[4/5] 检查 Whisper...${NC}"

    if command -v whisper &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Whisper 已安装"
        return 0
    else
        echo -e "  ${RED}✗${NC} Whisper 未安装"
        echo -e "  正在尝试安装..."

        # Try pipx first (recommended for CLI tools)
        if command -v pipx &> /dev/null; then
            pipx install openai-whisper
            echo -e "  ${GREEN}✓${NC} Whisper 安装完成 (via pipx)"
            return 0
        # Fallback to pip
        elif pip3 install openai-whisper 2>/dev/null || pip install openai-whisper 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} Whisper 安装完成 (via pip)"
            return 0
        else
            echo -e "  ${YELLOW}!${NC} 请手动安装: pipx install openai-whisper"
            return 1
        fi
    fi
}

# Install Python dependencies
install_python_deps() {
    echo -e "${YELLOW}[5/5] 安装 Python 依赖...${NC}"

    REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

    if [ -f "$REQUIREMENTS" ]; then
        pip3 install --break-system-packages -r "$REQUIREMENTS" 2>/dev/null || \
        pip install --break-system-packages -r "$REQUIREMENTS" 2>/dev/null || \
        pip3 install -r "$REQUIREMENTS" 2>/dev/null || \
        pip install -r "$REQUIREMENTS"
        echo -e "  ${GREEN}✓${NC} Python 依赖安装完成"
    else
        echo -e "  ${YELLOW}!${NC} requirements.txt 不存在，跳过"
    fi
}

# Create output directory
create_directories() {
    echo -e "${YELLOW}创建输出目录...${NC}"

    mkdir -p "$SCRIPT_DIR/output"
    echo -e "  ${GREEN}✓${NC} 创建 output/ 目录"
}

# Main installation
main() {
    ERRORS=0

    check_python || ERRORS=$((ERRORS + 1))
    check_ffmpeg || ERRORS=$((ERRORS + 1))
    check_ytdlp || ERRORS=$((ERRORS + 1))
    check_whisper || ERRORS=$((ERRORS + 1))
    install_python_deps || ERRORS=$((ERRORS + 1))
    create_directories

    echo ""
    echo -e "${BLUE}========================================${NC}"

    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}✓ 安装完成！所有依赖已就绪${NC}"
        echo ""
        echo -e "使用方法:"
        echo -e "  python scripts/video_to_summary.py \"视频URL\""
        echo ""
    else
        echo -e "${YELLOW}! 安装完成，但有 $ERRORS 个问题需要手动处理${NC}"
        echo -e "  请参考上述提示安装缺失的依赖"
    fi

    echo -e "${BLUE}========================================${NC}"
}

main "$@"
