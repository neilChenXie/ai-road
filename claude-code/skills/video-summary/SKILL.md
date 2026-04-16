---
name: video-summary
description: 下载小红书或B站视频并自动提取转录内容和生成总结。使用此技能当用户提供小红书或B站视频URL并要求下载、转录或总结视频内容。支持通过yt-dlp下载小红书视频、通过B站API下载B站视频、FFmpeg提取音频、Whisper进行语音转文字、以及总结视频观点等。如果用户提到小红书、B站、bilibili、短视频下载、视频转录、语音识别或视频内容分析，都应该使用此技能。用户提供的链接，必须完整保留，需严格按照文档的步骤处理链接。
compatibility: 需要yt-dlp、FFmpeg、OpenAI Whisper、requests；Python 3.9+
---

# 视频下载和总结 Skill

支持平台：**小红书**、**B站(Bilibili)**

整体按四个步骤进行：
1. **下载视频** 
2. **提取音频** 
3. **Whisper转录**
4. **总结输出**

## 🚨 强制规则

1. 用户提供的链接，**必须完整保留**
2. **先识别平台**，再按对应流程处理
3. 所有中间文件存储在 `./temp/` 目录，处理完成后自动清理。
4. 最终总结输出为 Markdown 格式，保存在 `./temp/` 目录下，命名格式为 `summary_YYYYMMDD_HHMMSS.md`。
5. whisper默认使用base模型，除非用户明确要求更高准确度的模型（如medium或large）。

## 平台识别

根据URL判断平台：

| 平台 | URL特征 | 处理方式 |
|------|---------|----------|
| 小红书 | `xiaohongshu.com` 或 `xhslink.com`| yt-dlp下载 |
| B站 | `bilibili.com` 或 `b23.tv` | 优先yt-dlp音频，失败用API脚本 |

---

## Workflow：视频处理流程

### 步骤1：下载视频

#### B站

**方法一（优先）：yt-dlp直接获取音频**

```bash
yt-dlp -f "bestaudio" -o "video.%(ext)s" "https://www.bilibili.com/video/BVxxxxxx"
```

如果成功，直接获得音频文件，**跳过步骤2**，直接进入步骤3。

**方法二（备用）：B站API下载脚本**

如果yt-dlp失败（如触发HTTP 412风控），使用专用下载脚本：

```bash
python scripts/bilibili_download.py "https://www.bilibili.com/video/BVxxxxxx"
```

脚本参数：
- `--output-dir, -o` - 指定输出目录
- `--keep-files, -k` - 保留临时文件

#### 小红书

```bash
yt-dlp --referer "https://www.xiaohongshu.com" \
  --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "视频URL"
```

**关键参数：**
- `--referer` - 设置HTTP referer防止被阻止
- `--user-agent` - 模拟浏览器请求

---

### 步骤2：提取音频

**跳过条件：** 如果步骤1用yt-dlp直接获取了音频文件，跳过此步骤。

```bash
ffmpeg -i input_video.mp4 -q:a 0 -map a audio.mp3
```

---

### 步骤3：Whisper转录

```bash
whisper audio.mp3 --model base --language zh
```

---

### 步骤4：总结并输出

基于转录文本生成总结，输出为 Markdown 文件。

**输出文件：** `./temp/summary_YYYYMMDD_HHMMSS.md`

**文件格式：**
```markdown
# 视频内容总结

**平台:** [小红书/B站]
**URL:** [原始视频URL]
**处理时间:** [时间戳]

## 核心要点

[总结内容：提取主要观点和核心信息]

## 完整转录

[转录的完整文本]
```

**清理临时文件：** 处理完成后自动删除视频文件、音频文件、转录文本文件，仅保留最终的 Markdown 总结文件。

---

## 输出目录

所有输出文件默认保存到 `./temp/` 目录：

- **最终输出** - `./temp/summary_YYYYMMDD_HHMMSS.md`（Markdown格式）
- **B站视频** - 如需保留视频，使用 `--keep-files` 参数

可通过 `--output-dir` 参数指定其他目录。

---

## 输出格式

处理完成后，向用户显示：

```
===== 视频内容总结 =====
平台: [小红书/B站]
URL: [原始视频URL]
处理时间: [时间戳]

【核心要点】
[总结内容]

【处理完成】
已删除临时文件：视频文件、音频文件、转录文本
保留文件：./temp/summary_YYYYMMDD_HHMMSS.md
```

## 错误处理

| 错误类型 | 可能原因 | 解决方法 |
|---------|--------|--------|
| B站yt-dlp失败 | 触发HTTP 412风控 | 自动切换到 `scripts/bilibili_download.py` |
| B站API返回错误 | 视频不存在/会员专属 | 提示用户视频可能需要会员 |
| 小红书下载失败 | URL无效或被封禁 | 检查URL格式，稍后重试 |
| 音频提取失败 | FFmpeg未安装 | `brew install ffmpeg` |
| Whisper转录失败 | Whisper未安装 | `pip install openai-whisper` |

当遇到任何错误，应该：
1. 报告具体的错误信息
2. 说明停在哪个处理步骤
3. 建议用户的解决方案
4. 停止处理不继续后续步骤

## 环境准备

```bash
# 安装yt-dlp (视频下载)
pip install yt-dlp

# 安装Whisper (语音转文字)
pip install openai-whisper

# 安装requests (B站API)
pip install requests

# 检查FFmpeg
ffmpeg -version
# 如果未安装，macOS上：
brew install ffmpeg
```

## 常见问题

**Q: B站视频处理流程是什么？**
A: B站视频优先使用yt-dlp直接获取音频（更快更简单）。如果yt-dlp触发HTTP 412风控，则自动切换到API下载脚本作为备用方案。

**Q: B站会员专属视频能下载吗？**
A: 不能。API方式无法获取会员专属视频的播放地址，需要提示用户该视频需要会员权限。

**Q: 支持B站短链接吗？**
A: 支持。`bilibili_download.py` 会自动解析 b23.tv 短链接。

**Q: 能处理其他平台吗？**
A: 目前支持小红书和B站。其他平台需要不同的处理方式。

**Q: 转录准确度如何？**
A: Whisper base模型的中文准确度约为80-90%。可使用medium或large模型提高准确度，但更耗时。

## 依赖和版本

- Python 3.9+
- yt-dlp >= 2024.01.01
- FFmpeg >= 4.0
- openai-whisper >= 20231117
- requests >= 2.28.0
