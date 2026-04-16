#!/bin/bash
# 小红书视频下载工具依赖安装脚本

set -e

echo "=========================================="
echo "小红书视频下载和总结 - 依赖安装脚本"
echo "=========================================="

# 检查Python版本
echo ""
echo "[检查] Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python版本: $python_version"

# 安装yt-dlp
echo ""
echo "[安装] yt-dlp..."
if pip3 install yt-dlp; then
    echo "✓ yt-dlp安装成功"
else
    echo "✗ yt-dlp安装失败"
    exit 1
fi

# 安装Whisper
echo ""
echo "[安装] OpenAI Whisper..."
if pip3 install openai-whisper; then
    echo "✓ Whisper安装成功"
else
    echo "✗ Whisper安装失败"
    exit 1
fi

# 检查FFmpeg
echo ""
echo "[检查] FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    ffmpeg_version=$(ffmpeg -version 2>&1 | head -n1)
    echo "✓ FFmpeg已安装: $ffmpeg_version"
else
    echo "⚠ FFmpeg未安装"
    echo ""
    echo "请手动安装FFmpeg:"
    echo "  macOS:   brew install ffmpeg"
    echo "  Windows: 访问 https://ffmpeg.org/download.html"
    echo "  Linux:   sudo apt install ffmpeg  (Ubuntu/Debian)"
    echo "           sudo yum install ffmpeg  (CentOS/RHEL)"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ 所有依赖安装完成！"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  python3 xiaohongshu_download_and_summarize.py \"小红书视频URL\""
echo ""
