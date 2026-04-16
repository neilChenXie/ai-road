# Skill 快速参考

## 什么是这个Skill

🎥 **小红书视频下载和总结 (xiaohongshu-video-summarizer)**

- 自动下载小红书视频
- 提取音频并转录为文字
- 生成内容总结

---

## 何时使用

用户说：
- "下载小红书视频"
- "转录这个视频链接"
- "总结视频内容"
- "帮我提取这个短视频的文字"

---

## 工作流程 (4步)

```
URL → [yt-dlp下载] → [FFmpeg提取音频] → [Whisper转录] → [总结] → 输出
```

---

## 快速使用命令

```bash
# 安装依赖（首次）
bash scripts/install_deps.sh

# 基础使用
python scripts/xiaohongshu_download_and_summarize.py "URL"

# 高精度模式
python scripts/xiaohongshu_download_and_summarize.py "URL" --model medium

# 保留所有文件
python scripts/xiaohongshu_download_and_summarize.py "URL" --keep-files
```

---

## 输出内容

```
【显示在命令行】
- 完整的转录文本
- 核心要点总结
- 处理时间和文件位置

【保存到文件】
- transcript_YYYYMMDD_HHMMSS.txt
- summary_YYYYMMDD_HHMMSS.txt
```

---

## 依赖

| 工具 | 版本 | 说明 |
|------|------|------|
| Python | 3.9+ | 脚本运行环境 |
| yt-dlp | 2024.01+ | 视频下载 |
| FFmpeg | 4.0+ | 音频提取 |
| Whisper | 20231117+ | 语音转文字 |

---

## 参数对比

| 参数 | 用途 |
|------|------|
| --model tiny/base/small/medium/large | 选择Whisper精度（base平衡推荐） |
| --language zh/en/... | 指定语言代码（默认中文） |
| --keep-files | 保留下载的视频和音频 |
| --output-dir /path | 指定输出目录 |

---

## 文件清单

```
xiaohongshu-video-summarizer/
├── SKILL.md                     # Skill文档（核心）
├── README.md                    # 快速入门
├── PROJECT_SUMMARY.md           # 项目总结
├── scripts/
│   ├── xiaohongshu_download_and_summarize.py   # 主脚本 ⭐
│   └── install_deps.sh             # 依赖安装
├── references/
│   └── USAGE_GUIDE.md           # 详细使用指南
└── evals/
    └── evals.json              # 测试用例
```

---

## 常见问题速查

| 问题 | 答案 |
|------|------|
| 支持哪些平台？ | 目前仅小红书（其他平台需要定制） |
| 准确度如何？ | base模型约80-90%（可升级到medium/large） |
| 处理时间？ | 1min视频约2-3min，5min视频约8-12min |
| 文件会被保存吗？ | 默认删除，用--keep-files保留 |
| 支持批量吗？ | 支持，逐个处理多个URL |

---

## 故障排除

```bash
# ❌ yt-dlp: command not found
pip install yt-dlp

# ❌ ffmpeg: command not found  
brew install ffmpeg

# ❌ whisper: command not found
pip install openai-whisper

# ❌ 下载被拒
# → 检查URL、稍后重试、检查网络
```

---

## 下一步

1. ✅ 阅读 README.md 快速开始
2. ✅ 运行 `bash scripts/install_deps.sh` 安装依赖
3. ✅ 运行脚本处理视频
4. ✅ 查看 USAGE_GUIDE.md 了解更多高级用法

---
