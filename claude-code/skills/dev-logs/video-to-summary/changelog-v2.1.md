# Changelog - Video to Summary V2.1

## 发布日期
2026-03-15

## 主要更新

### 小红书下载优化 (核心改进)

小红书视频下载现在使用专用的优化命令，不再依赖 cookies，显著提高下载成功率。

**命令格式：**
```bash
yt-dlp --referer "https://www.xiaohongshu.com" --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" "视频URL"
```

**重要说明：**
- 请使用完整的分享链接（包含所有查询参数，尤其是 `xsec_token`）
- 不再需要浏览器 cookies
- 不添加任何额外的 yt-dlp 参数（如 `--no-playlist`、`-f`、`-o` 等）

---

## 文件修改详情

### 1. `scripts/utils/video_downloader.py`

**新增方法：**
```python
def _download_xiaohongshu(self, url: str, output_path: Path) -> Tuple[bool, str]:
    """
    Download XiaoHongShu video using exact command format:
    yt-dlp --referer "https://www.xiaohongshu.com" --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" "视频URL"
    """
    args = [
        'yt-dlp',
        '--referer', 'https://www.xiaohongshu.com',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        url
    ]
    # ...
```

**修改内容：**
- `download()` 方法：小红书链接调用独立的 `_download_xiaohongshu()` 方法
- 移除小红书的 `--dump-json` 调用（小红书不支持该参数）
- 下载完成后自动移动文件到输出目录

### 2. `scripts/utils/speech_to_text.py`

**修复问题：**
- `--language` 参数：当 language 为空或 'auto' 时不传递该参数（避免空字符串报错）
- 文件名过长：使用固定的 `transcript` 作为文件名，避免 macOS 文件名长度限制错误

**修改前：**
```python
'--language', language if language != 'auto' else '',
base_name = transcript_data.get('text', 'transcript').split()[0]
```

**修改后：**
```python
# Add language if specified (not 'auto')
if language and language != 'auto':
    args.extend(['--language', language])
base_name = "transcript"  # Fixed name to avoid filename too long error
```

### 3. `scripts/utils/platform_detector.py`

**修改内容：**
```python
'xiaohongshu': {
    'name': 'XiaoHongShu (小红书)',
    'supports_api': False,
    'supports_cookies': False,  # Uses custom command instead
    'use_custom_command': True,  # Special handling with referer/user-agent
    'requires_auth': False,
},
```

### 4. `config.yaml`

**修改内容：**
```yaml
xiaohongshu:
  use_custom_command: true   # Uses optimized download command
  # Command: yt-dlp --referer "https://www.xiaohongshu.com" --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" "URL"
```

### 5. `SKILL.md`

**更新内容：**
- 支持平台表：小红书标记为 **Excellent**，排在第一位
- Platform-Specific Notes：详细说明小红书的下载方法和要求

### 6. `README.md`

**更新内容：**
- 支持平台表：小红书标记为 **⭐ 推荐**
- 新增小红书下载说明章节
- 更新常见问题和 V2 优化内容

---

## 支持平台优先级

| 优先级 | 平台 | 支持度 | 说明 |
|--------|------|--------|------|
| 1 | 小红书 | ⭐ Excellent | 使用优化的下载命令 |
| 2 | Bilibili (B站) | Excellent | 官方 API 支持 |
| 3 | YouTube | Good | 可选使用 cookies |
| 4 | TikTok | Good | 标准支持 |
| 5 | Twitter/X | Good | 标准支持 |

---

## Bug 修复

1. **Whisper language 参数错误**
   - 问题：`--language ''` 导致 Whisper 报错
   - 解决：当 language 为空或 'auto' 时不传递该参数

2. **文件名过长错误**
   - 问题：macOS 文件名长度限制 (255 字节)
   - 解决：使用固定的 `transcript` 作为文件名

3. **小红书下载失败**
   - 问题：使用 `--dump-json` 和 cookies 方式不稳定
   - 解决：使用专用的 referer/user-agent 命令格式

---

## 测试验证

测试链接：
```
https://www.xiaohongshu.com/explore/6996509d000000001d013ff0?app_platform=ios&app_version=9.19.4&share_from_user_hidden=true&xsec_source=app_share&type=video&xsec_token=CB4rKDXTQQXWcxU3SLbQQbJuDmU46Buq0GAK5WZ2a4fvY=&author_share=1&xhsshare=CopyLink&shareRedId=Nz0yQUg9NkFHTEk5PkA0PTk1QT1KPThN&apptime=1771489965&share_id=82b9969d453940eb9298ee408d6e0bce&recLinkType=video
```

测试结果：
- ✅ 视频下载成功 (144.47MB, 12分50秒)
- ✅ 音频提取成功
- ✅ 语音识别成功 (507 segments)
- ✅ 总结生成成功

---

## 升级指南

如果您已经安装了旧版本，只需更新以下文件：

```bash
cd /Users/chen/.claude/skills/video-to-summary

# 拉取最新代码（如果是 git 仓库）
git pull

# 或者手动更新以下文件：
# - scripts/utils/video_downloader.py
# - scripts/utils/speech_to_text.py
# - scripts/utils/platform_detector.py
# - config.yaml
# - SKILL.md
# - README.md
```

无需重新安装依赖。

---

## 下一步计划

- [ ] 支持更多视频平台
- [ ] 优化长视频处理性能
- [ ] 添加批量处理功能
- [ ] 支持自定义输出模板
