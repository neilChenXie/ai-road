---
name: video-to-summary
description: 基于URL下载网络视频，提取音频转为文字，智能总结视频内容的完整工具。支持小红书、Bilibili、YouTube、抖音等主流平台。提供一站式视频内容分析服务，满足内容创作者、研究者、学习者需求。
---

# 🎥 视频转文字总结工具

基于URL的完整视频内容分析工具链，支持：视频下载 → 音频提取 → 语音转文字 → 智能总结

## 🎯 核心功能

### 1. 多平台视频下载
- ✅ YouTube, YouTube Shorts, YouTube Music
- ✅ Bilibili (B站) 
- ✅ 小红书 (RedNote)
- ✅ 抖音, TikTok
- ✅ Twitter/X, Instagram, Facebook
- ✅ Vimeo, Twitch 等数千个网站

### 2. 音频提取与转换
- 自动提取音频为MP3/WAV格式
- 支持批量处理
- 保留音频质量

### 3. 语音转文字
- 支持多语言识别（中文、英文等）
- 高准确率语音识别
- 时间戳标记

### 4. 智能内容总结
- 关键信息提取
- 章节分段总结
- 要点列表生成
- 情感倾向分析

## 📋 前置要求

### 1. 系统依赖
```bash
# 检查并安装必要依赖
pip install yt-dlp ffmpeg-python whisper openai speechrecognition pydub
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg          # macOS
```

### 2. 可选依赖（高级功能）
```bash
# 使用OpenAI Whisper获得更高精度
pip install git+https://github.com/openai/whisper.git

# 使用Azure语音服务
pip install azure-cognitiveservices-speech
```

## 🚀 快速开始

### 基本使用：一站式视频分析
```bash
# 下载视频并提取关键信息
python scripts/video_to_summary.py --url "https://www.youtube.com/watch?v=xxx"

# 指定输出目录
python scripts/video_to_summary.py --url "URL" --output-dir "~/videos/analysis"

# 仅下载音频和转文字（不下载视频）
python scripts/video_to_summary.py --url "URL" --audio-only

# 指定语言识别
python scripts/video_to_summary.py --url "URL" --language "zh"
```

### 参数说明
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--url` | 视频URL（必需） | - |
| `--output-dir` | 输出目录 | `./output` |
| `--audio-only` | 仅处理音频（不下载视频） | `false` |
| `--language` | 语音识别语言 | `auto` |
| `--model` | Whisper模型大小 | `base` |
| `--summary-model` | 总结模型 | `gpt-3.5-turbo` |

## 📊 工作流程

### 完整流程示例
```python
# 1. 下载视频
yt-dlp --cookies-from-browser chrome -o "video.%(ext)s" "URL"

# 2. 提取音频
ffmpeg -i video.mp4 -vn -acodec mp3 audio.mp3

# 3. 语音转文字
whisper audio.mp3 --language Chinese --output_format txt

# 4. 智能总结
python scripts/summarize_text.py -i transcript.txt -o summary.md
```

### 自动化脚本使用
```bash
# 完整流程自动化
bash scripts/process_video.sh "URL"

# 批量处理URL列表
bash scripts/batch_process.sh urls.txt

# 监控目录自动处理
bash scripts/watch_folder.sh ~/Downloads/videos/
```

## 🔧 详细功能说明

### 1. 视频下载与平台适配
```python
# YouTube (需要cookies避免403错误)
yt-dlp --cookies-from-browser chrome "youtube_url"

# Bilibili (B站)
yt-dlp --referer "https://www.bilibili.com" "bilibili_url"

# 小红书
yt-dlp --user-agent "Mozilla/5.0" "xiaohongshu_url"

# 通用配置
yt-dlp -o "%(title)s.%(ext)s" --merge-output-format mp4 "url"
```

### 2. 音频提取与优化
```python
# 提取高质量音频
ffmpeg -i input.mp4 -vn -acodec mp3 -ab 192k audio.mp3

# 降噪处理
ffmpeg -i audio.mp3 -af "afftdn=nf=-20" audio_cleaned.mp3

# 音频分段（长视频优化）
ffmpeg -i audio.mp3 -f segment -segment_time 600 -c copy audio_%03d.mp3
```

### 3. 语音识别配置
```python
# 使用Whisper (推荐)
whisper audio.mp3 --model base --language zh --output_dir transcripts/

# 使用本地部署的Whisper模型
whisper audio.mp3 --model_dir ~/models/whisper-large-v3

# 使用Azure语音服务
import azure.cognitiveservices.speech as speechsdk
# 配置Azure密钥和区域
```

### 4. 智能总结策略
```python
# 基础总结（提取关键要点）
summary = extract_key_points(transcript, max_points=10)

# 结构化总结（分章节）
structured = create_structured_summary(transcript, sections=5)

# 深度分析（情感、话题、建议）
analysis = deep_analysis(transcript, include_emotion=True)

# 多语言支持
summary_zh = summarize(transcript, language="zh", style="brief")
summary_en = summarize(transcript, language="en", style="detailed")
```

## 📁 输出文件结构

处理完成后，将在输出目录生成：
```
output/
├── video.mp4                    # 原始视频（如选择下载）
├── audio.mp3                    # 提取的音频
├── transcript.txt               # 完整文字转录
├── transcript_with_timestamps.txt # 带时间戳的转录
├── summary.md                   # 智能总结
├── key_points.json              # 关键要点JSON
└── metadata.json                # 视频元数据
```

## 🎨 高级功能

### 1. 批量处理
```bash
# 处理URL列表文件
python scripts/batch_processor.py --input-file urls.txt --parallel 3

# 监控RSS源自动处理
python scripts/rss_monitor.py --feed "https://youtube.com/feed/rss"
```

### 2. 自定义总结模板
```yaml
# config/summary_templates.yaml
brief:
  sections: ["概述", "关键点", "结论"]
detailed:
  sections: ["简介", "主要内容", "案例分析", "关键结论", "行动建议"]
academic:
  sections: ["研究背景", "方法", "结果", "讨论", "启示"]
```

### 3. 多模型支持
```python
# 切换不同总结模型
models = {
    "fast": "gpt-3.5-turbo",
    "quality": "gpt-4",
    "local": "llama-3.1-8b",
    "chinese": "qwen-2.5-7b"
}
```

### 4. 质量控制
```python
# 音频质量检查
if audio_quality(audio_path) < 0.7:
    enhance_audio(audio_path)

# 转录准确率评估
accuracy = evaluate_transcription(transcript, reference_text)

# 总结相关性评分
relevance = calculate_relevance(transcript, summary)
```

## 🔍 应用场景

### 1. 内容创作者
- 视频内容快速摘要
- 生成视频字幕
- 提取金句和亮点
- 内容灵感获取

### 2. 学习研究
- 讲座视频笔记
- 在线课程总结
- 学术演讲转录
- 文献视频分析

### 3. 商业分析
- 竞品视频分析
- 市场趋势识别
- 产品评测总结
- 行业报告生成

### 4. 个人使用
- 保存重要视频内容
- 创建个人知识库
- 语言学习辅助
- 记忆强化工具

## ⚠️ 注意事项

### 1. 版权与法律
- 仅下载公开内容
- 遵守平台服务条款
- 个人使用为主
- 尊重内容创作者

### 2. 技术要求
- 网络稳定（视频下载需要带宽）
- 足够的存储空间
- GPU加速（可选，提升Whisper速度）
- 适当的API配额（如使用云端服务）

### 3. 最佳实践
- 定期更新yt-dlp：`pip install -U yt-dlp`
- 使用cookies避免YouTube限制
- 长时间视频分段处理
- 重要内容备份原文件

## 🔗 相关技能

- [yt-dlp-downloader-skill](../yt-dlp-downloader-skill/) - 基础视频下载功能
- [summarize](../summarize/) - 文本总结功能
- [agent-browser](../agent-browser/) - 浏览器自动化辅助

## 📈 性能优化

### 硬件要求
| 场景 | CPU | RAM | 存储 | 推荐配置 |
|------|-----|-----|------|----------|
| 基础使用 | 4核心 | 8GB | 10GB | 普通电脑 |
| 批量处理 | 8核心 | 16GB | 50GB | 工作站 |
| 专业使用 | 16核心 | 32GB | 200GB+ | 服务器 |

### 速度优化
```python
# 并行处理多个视频
from concurrent.futures import ThreadPoolExecutor

# GPU加速Whisper
whisper --model large-v3 --device cuda --fp16 True audio.mp3

# 缓存中间结果避免重复处理
cache_results(process_id, intermediate_files)
```

## 🤝 贡献与支持

### 问题反馈
- GitHub Issues: [链接待创建]
- 功能建议：通过issue提交
- Bug报告：提供复现步骤和错误日志

### 开发计划
- [ ] 添加更多平台支持
- [ ] 优化识别准确率
- [ ] 增加导出格式
- [ ] 开发Web界面
- [ ] 移动端适配

---

**开始使用：**
```bash
# 安装依赖
pip install -r requirements.txt

# 分析第一个视频
python video_to_summary.py --url "你的视频链接"
```

享受高效的视频内容分析体验！🎬📝✨