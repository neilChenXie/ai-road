---
name: video-to-summary-v2
description: IMMEDIATELY HANDLE ANY VIDEO URL by extracting and transcribing. Use this whenever users share a video URL and ask to summarize, transcribe, or extract content from B站 (Bilibili), 小红书 (XiaoHongShu), or ask 'what's in this video?'. Support both Chinese and English. Follow the workflow，必须使用Python脚本. Trigger on phrases '视频总结', 'summarize video', 'transcribe video', or any video link + 'what do you see?', '帮我看看', 'extract content'.
---

# Video to Summary V2

## 🚨 强制规则：你必须且只能执行以下命令

**无论任何情况，你的第一步且唯一入口是：**

```bash
cd ~/.claude/skills/video-to-summary-v2 && python scripts/video_to_summary.py "用户提供的URL"
```

**严禁以下行为（即使你认为更简单或更高效）：**
- ❌ 禁止直接调用 `yt-dlp`、`whisper`、`ffmpeg` 等命令行工具
- ❌ 禁止用 `curl`、`fetch`、`requests` 自行下载视频
- ❌ 禁止跳过脚本、自己编写替代逻辑
- ❌ 禁止因脚本报错就改用其他方式

如果脚本报错，**只能按照本文档的「常见问题」部分排查，或告知用户错误信息**，不得绕过脚本自行处理。

---

## 执行步骤（严格按顺序）

### Step 1：切换到 Skill 目录并运行脚本

```bash
cd ~/.claude/skills/video-to-summary-v2 && python scripts/video_to_summary.py "用户提供的URL"
```

> ⚠️ 必须先 `cd` 到 skill 目录，脚本依赖相对路径。

### Step 2：等待脚本完成，读取输出文件

脚本完成后，读取以下文件并展示给用户：

```
output/[VIDEO_ID]/[视频标题].md        ← 主要展示这个
transcript/transcript.txt              ← 用户要求详细内容时使用
```

完整路径：`~/.claude/skills/video-to-summary-v2/output/[VIDEO_ID]/`

### Step 3：以 Markdown 格式呈现内容

直接将 `.md` 文件内容渲染给用户。如用户需要逐字稿，附上 `transcript.txt`。

---

## 支持平台

| 平台 | URL 示例 |
|------|---------|
| **B站 (Bilibili)** | `bilibili.com/video/BV...` / `b23.tv/...` |
| **小红书 (XiaoHongShu)** | `xiaohongshu.com/...` / `xhslink.com/...` |

---

## 高级选项（仅在默认运行失败时使用）

```bash
# 更高精度（速度慢约 2 倍）：
cd ~/.claude/skills/video-to-summary-v2 && python scripts/video_to_summary.py "URL" --model base

# 保留临时文件（用于调试）：
cd ~/.claude/skills/video-to-summary-v2 && python scripts/video_to_summary.py "URL" --keep-temp

# 自定义输出目录：
cd ~/.claude/skills/video-to-summary-v2 && python scripts/video_to_summary.py "URL" --output-dir /path/to/output

# 检查依赖是否已安装：
cd ~/.claude/skills/video-to-summary-v2 && python scripts/video_to_summary.py --check-deps
```

---

## 输出文件结构

```
~/.claude/skills/video-to-summary-v2/output/[VIDEO_ID]/
├── [视频标题].md             ← 展示给用户（含标题、概述、要点、详细分段）
├── [视频标题]_summary.json   ← 结构化数据（用户需要解析时使用）
└── transcript/
    ├── transcript.txt        ← 纯文本逐字稿
    └── transcript.json       ← 带时间戳的详细转录
```

---

## 常见问题排查

> ⚠️ 遇到问题时，只能用以下方法排查，不得绕过脚本。

**脚本无法运行 / Python 找不到**
→ 先执行：`cd ~/.claude/skills/video-to-summary-v2 && python scripts/video_to_summary.py --check-deps`

**视频下载失败**
- 小红书：URL 必须包含完整参数（尤其是 `xsec_token`），使用分享链接而非浏览器地址栏复制的链接
- B站：部分视频需要登录，脚本会自动尝试；如仍失败，告知用户

**转录内容乱码或过短**
→ 可能视频文件损坏，使用 `--keep-temp` 重试后检查下载文件：
```bash
cd ~/.claude/skills/video-to-summary-v2 && python scripts/video_to_summary.py "URL" --keep-temp
```

**"Model not found" 错误**
→ Whisper 首次下载模型需要时间（约 500MB），等待完成即可。或改用小模型：`--model tiny` 或 `--model small`

---

## 配置文件说明（config.yaml）

| 配置项 | 说明 |
|--------|------|
| `whisper.model` | Whisper 模型大小：tiny / small / base / medium / large |
| `output.cleanup_temp` | 处理完成后是否删除临时视频文件 |
| `download.timeout` | 视频下载超时时间（秒） |
