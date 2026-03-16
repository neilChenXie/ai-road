#!/bin/bash
# 视频转文字总结工具 - 安装脚本

set -e

echo "🎥 安装视频转文字总结工具..."

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION 3.8" | awk '{print ($1 < $2)}') -eq 1 ]]; then
    echo "❌ 需要Python 3.8或更高版本"
    exit 1
fi

# 安装系统依赖
echo "🔧 安装系统依赖..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y ffmpeg python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y ffmpeg python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y ffmpeg python3-pip
    else
        echo "⚠️  请手动安装: ffmpeg, python3-pip"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "⚠️  请先安装Homebrew: https://brew.sh/"
        echo "然后运行: brew install ffmpeg"
    fi
else
    echo "⚠️  请手动安装: ffmpeg"
fi

# 创建虚拟环境（可选）
read -p "创建Python虚拟环境？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🐍 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "虚拟环境已激活"
fi

# 安装Python包
echo "📦 安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 安装Whisper（可选）
read -p "安装OpenAI Whisper语音识别？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔊 安装Whisper..."
    pip install git+https://github.com/openai/whisper.git
    echo "Whisper安装完成"
    echo "注意: Whisper需要下载模型文件，第一次使用时会自动下载"
fi

# 安装yt-dlp（确保最新版本）
echo "📥 更新yt-dlp..."
pip install -U yt-dlp

# 创建配置目录
echo "⚙️ 创建配置..."
mkdir -p config
mkdir -p output

# 检查工具是否安装成功
echo "🔍 检查安装结果..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg: $(ffmpeg -version | head -n1)"
else
    echo "❌ ffmpeg未安装"
fi

if python3 -c "import yt_dlp; print('✅ yt-dlp:', yt_dlp.version.__version__)" &> /dev/null; then
    python3 -c "import yt_dlp; print('✅ yt-dlp:', yt_dlp.version.__version__)"
else
    echo "❌ yt-dlp未正确安装"
fi

if python3 -c "import whisper" &> /dev/null; then
    echo "✅ Whisper已安装"
else
    echo "⚠️  Whisper未安装（可选）"
fi

# 设置权限
chmod +x scripts/*.py
chmod +x scripts/*.sh

echo ""
echo "🎉 安装完成！"
echo ""
echo "快速开始:"
echo "1. 基本使用: python scripts/video_to_summary.py --url '视频URL'"
echo "2. 仅音频: python scripts/video_to_summary.py --url '视频URL' --audio-only"
echo "3. 批量处理: bash scripts/batch_process.sh urls.txt"
echo ""
echo "配置说明:"
echo "- 编辑 config/settings.yaml 配置API密钥等"
echo "- 输出文件保存在 output/ 目录"
echo ""
echo "如需帮助，请查看 README.md 或运行: python scripts/video_to_summary.py --help"