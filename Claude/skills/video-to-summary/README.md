# Video to Summary V2

优化版视频转文字总结工具 - 一键安装，自动处理，智能总结。

## 快速开始

### 1. 一键安装

```bash
bash install.sh
```

### 2. 处理视频

```bash
# 基础用法
python3 scripts/video_to_summary.py --url "https://www.youtube.com/watch?v=xxx"

# 仅下载音频（更快）
python3 scripts/video_to_summary.py --url "URL" --audio-only

# 使用更准确的模型
python3 scripts/video_to_summary.py --url "URL" --model medium

# 自定义输出目录
python3 scripts/video_to_summary.py --url "URL" --output-dir ~/my-output
```

### 3. 检查依赖

```bash
python3 scripts/video_to_summary.py --check-deps
```

## 支持的平台

| 平台 | 支持度 | 说明 |
|------|--------|------|
| YouTube | ✅ | 可选使用 cookies |
| Bilibili (B站) | ✅ | 官方 API 支持 |
| 小红书 | ✅ | 自动检测 cookies |
| TikTok | ✅ | 标准支持 |
| Twitter/X | ✅ | 标准支持 |

## 输出格式

处理完成后会生成：

```
output/<video_id>/
├── report.json              # 处理报告
├── transcript/
│   ├── audio.json          # 转录数据（含时间戳）
│   ├── audio.txt          # 纯文本转录
│   └── audio.srt          # 字幕文件
└── summary.md             # Markdown 格式总结
```

## 常见问题

### 依赖问题

如果遇到 `ModuleNotFoundError`，运行：
```bash
bash install.sh
```

### 下载失败

对于需要认证的内容（如小红书私有视频），确保已登录浏览器。

### 识别不准

使用更大的模型：
```bash
python3 scripts/video_to_summary.py --url "URL" --model medium
```

## 配置

编辑 `config.yaml` 自定义行为：

```yaml
whisper:
  model: base           # 模型大小
  language: zh         # 语言

download:
  use_cookies: true    # 使用浏览器 cookies
  audio_only: false    # 仅下载音频

output:
  format: [txt, json, md]  # 输出格式
  include_summary: true      # 自动生成总结
```

## 项目结构

```
video-to-summary-v2/
├── SKILL.md                 # Skill 说明文档
├── README.md                # 本文件
├── config.yaml             # 配置文件
├── requirements.txt         # Python 依赖
├── install.sh              # 安装脚本
└── scripts/
    ├── video_to_summary.py  # 主脚本
    └── utils/
        ├── __init__.py
        ├── platform_detector.py
        ├── video_downloader.py
        ├── audio_extractor.py
        ├── speech_to_text.py
        ├── text_summarizer.py
        ├── dependency_checker.py
        └── logger.py
```

## V2 优化内容

相比原版本的主要改进：

- ✅ 自动依赖管理
- ✅ 更好的平台支持（小红书自动 cookies）
- ✅ 自动生成结构化总结
- ✅ 友好的错误提示
- ✅ 结构化输出（JSON + Markdown）
- ✅ 可配置的 YAML 设置
- ✅ 进度追踪
- ✅ 自动清理临时文件
