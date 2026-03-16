# ⚡ 快速开始指南

## 🎯 一句话说明
**视频转文字总结工具** = 输入视频URL → 自动下载 → 提取音频 → 转成文字 → 智能总结

## 📦 一分钟安装

### Linux/macOS
```bash
# 1. 下载工具
git clone https://github.com/yourusername/video-to-summary-skill.git
cd video-to-summary-skill

# 2. 一键安装
chmod +x install.sh
./install.sh

# 3. 按提示操作（建议安装Whisper）
```

### Windows
```bash
# 1. 安装Python 3.8+ 和 FFmpeg
# 2. 下载项目代码
# 3. 安装依赖
pip install yt-dlp ffmpeg-python whisper speechrecognition pydub
```

## 🚀 三分钟上手

### 示例1：处理YouTube视频
```bash
# 下载视频并生成总结
python scripts/video_to_summary.py \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --language zh
```

### 示例2：仅处理音频（更快）
```bash
# 仅下载音频并转文字
python scripts/video_to_summary.py \
  --url "视频URL" \
  --audio-only \
  --model small
```

### 示例3：批量处理多个视频
```bash
# 1. 创建URL列表文件
cat > my_videos.txt << EOF
https://www.youtube.com/watch?v=video1
https://www.bilibili.com/video/BVxxxx1
https://www.xiaohongshu.com/discovery/item/xxx1
EOF

# 2. 批量处理（3个并行）
bash scripts/batch_process.sh -i my_videos.txt -p 3 -l zh
```

## 📊 查看结果

处理完成后，在 `output/` 目录中查看：
```bash
# 查看最新处理结果
ls -la output/$(ls -t output/ | head -1)

# 查看总结内容
cat output/最新目录/summary.md

# 查看转录文本
head -20 output/最新目录/transcript.txt
```

## 🎨 定制化使用

### 针对不同平台优化
```bash
# YouTube：使用cookies避免限制
python scripts/video_to_summary.py --url "youtube链接" --cookies-browser chrome

# Bilibili：设置referer
python scripts/video_to_summary.py --url "bilibili链接" --referer "https://www.bilibili.com"

# 小红书：可能需要自定义user-agent
python scripts/video_to_summary.py --url "小红书链接" --user-agent "Mozilla/5.0"
```

### 质量与速度平衡
```bash
# 最快（低质量）
python scripts/video_to_summary.py --url "URL" --model tiny --audio-only

# 平衡（推荐）
python scripts/video_to_summary.py --url "URL" --model base --audio-only

# 最好质量（较慢）
python scripts/video_to_summary.py --url "URL" --model large
```

### 输出定制
```bash
# 指定输出目录
python scripts/video_to_summary.py --url "URL" --output-dir "~/我的视频分析"

# 生成详细报告
python scripts/video_to_summary.py --url "URL" --summary-style detailed

# 生成学术格式
python scripts/video_to_summary.py --url "URL" --summary-style academic
```

## 🔧 常见问题速查

### Q1: YouTube下载失败（403错误）
**解决：** 使用浏览器cookies
```bash
python scripts/video_to_summary.py --url "youtube链接" --cookies-browser chrome
```

### Q2: 语音识别不准
**解决：** 指定语言和使用更好的模型
```bash
python scripts/video_to_summary.py --url "URL" --language zh --model medium
```

### Q3: 处理速度太慢
**解决：**
```bash
# 方法1：仅处理音频
python scripts/video_to_summary.py --url "URL" --audio-only

# 方法2：使用小模型
python scripts/video_to_summary.py --url "URL" --model tiny

# 方法3：分段处理长视频（自动）
```

### Q4: 内存不足
**解决：**
```bash
# 1. 使用audio-only模式
# 2. 使用更小的模型（tiny/base）
# 3. 增加swap空间
```

## 📈 性能基准

| 场景 | 预计时间 | 内存使用 | 建议配置 |
|------|----------|----------|----------|
| 5分钟短视频 | 2-3分钟 | 1-2GB | model=base, audio-only |
| 30分钟讲座 | 10-15分钟 | 2-4GB | model=small, 分段处理 |
| 2小时电影 | 30-45分钟 | 4-8GB | model=tiny, 仅音频, 批量分段 |

## 🔄 工作流程图示

```
输入URL
    ↓
平台检测 → 自动选择最优策略
    ↓
视频下载 → 失败？→ 仅下载音频
    ↓
音频提取 → 自动降噪增强
    ↓
语音转文字 → 多引擎备用
    ↓
智能总结 → 多种风格可选
    ↓
输出报告 → 结构化整理
```

## 🎯 适用场景

### ✅ 适合
- 讲座视频笔记整理
- 会议记录转录
- 学习内容总结
- 竞品视频分析
- 个人知识管理

### ⚠️ 注意
- 版权保护内容需获得授权
- 超长视频需要分段处理
- 实时直播需要额外配置

## 📞 获取帮助

```bash
# 查看完整帮助
python scripts/video_to_summary.py --help

# 查看批量处理帮助
bash scripts/batch_process.sh --help

# 启用调试模式
python scripts/video_to_summary.py --url "URL" --debug
```

## 🚨 紧急恢复

如果处理中断：
```bash
# 1. 检查日志
cat output/任务目录/logs/*.log

# 2. 重新开始（会自动跳过已完成部分）
bash scripts/batch_process.sh -i urls.txt --resume

# 3. 手动清理（如需）
rm -rf output/失败的任务目录
```

---

**立即开始：**
```bash
# 复制这行，替换URL即可
python scripts/video_to_summary.py --url "你的视频链接" --language zh
```

享受高效的视频内容分析！🎬🚀