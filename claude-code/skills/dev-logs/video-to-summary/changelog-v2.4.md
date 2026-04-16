# Video Summary Skill - v2.4 更新日志

**日期:** 2026-03-20

## 概述

本次更新将 `xiaohongshu-video-summarizer` 重构为 `video-summary`，新增B站视频支持，完善单元测试，优化输出格式和文件管理。

---

## 主要变更

### 1. Skill 重命名

| 项目 | 原值 | 新值 |
|------|------|------|
| 目录名 | `xiaohongshu-video-summarizer/` | `video-summary/` |
| Skill名称 | `xiaohongshu-video-summarizer` | `video-summary` |
| 脚本名 | `download_and_summarize.py` | `xiaohongshu_download_and_summarize.py` |

### 2. 新增B站视频支持

**新增文件:** `scripts/bilibili_download.py`

B站有严格的风控策略，直接使用yt-dlp会触发HTTP 412错误。新脚本通过API方式下载：

- 支持标准URL: `bilibili.com/video/BVxxxxxx`
- 支持短链接: `b23.tv/xxxxxx`
- 通过 `api.bilibili.com/x/web-interface/view` 获取视频信息
- 通过 `api.bilibili.com/x/player/playurl` 获取DASH格式音视频
- 使用FFmpeg合并音视频

### 3. 单元测试

新增 `tests/` 目录，包含完整的单元测试：

```
tests/
├── __init__.py                    # 测试包初始化
├── conftest.py                    # 测试配置
├── test_bilibili_download.py      # B站脚本测试 (16个用例)
└── test_xiaohongshu_download.py   # 小红书脚本测试 (18个用例)
```

**测试覆盖范围：**
- 初始化参数验证
- URL解析和BV号提取
- 短链接解析
- API调用模拟
- 内容总结功能
- 文件保存功能
- 清理功能
- 错误处理

**运行测试命令：**
```bash
python -m unittest discover -s tests -v
```

### 4. 输出目录优化

默认输出目录从当前目录改为 `./temp/`：

- 视频文件: `./temp/视频标题.mp4`
- 总结文件: `./temp/summary_YYYYMMDD_HHMMSS.md`

### 5. 输出格式优化

**步骤4改进：**
- 输出格式改为 Markdown (`.md`)
- 内容结构：核心要点在前，完整转录在后

**步骤5新增：**
- 自动清理过程文件（视频、音频、转录文本）
- 仅保留最终的 Markdown 总结文件

**输出文件格式：**
```markdown
# 视频内容总结

**平台:** [小红书/B站]
**URL:** [原始视频URL]
**处理时间:** [时间戳]

## 核心要点

[总结内容]

## 完整转录

[转录的完整文本]
```

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `SKILL.md` | 修改 | 添加B站支持、更新步骤4/5 |
| `README.md` | 修改 | 添加平台支持、测试说明 |
| `scripts/bilibili_download.py` | 新增 | B站视频下载脚本 |
| `scripts/xiaohongshu_download_and_summarize.py` | 重命名 | 原download_and_summarize.py |
| `scripts/install_deps.sh` | 修改 | 更新脚本名称引用 |
| `tests/__init__.py` | 新增 | 测试包初始化 |
| `tests/conftest.py` | 新增 | 测试配置 |
| `tests/test_bilibili_download.py` | 新增 | B站脚本测试 |
| `tests/test_xiaohongshu_download.py` | 新增 | 小红书脚本测试 |
| `references/USAGE_GUIDE.md` | 修改 | 更新脚本名称 |
| `QUICK_REFERENCE.md` | 修改 | 更新脚本名称 |
| `PROJECT_SUMMARY.md` | 修改 | 更新脚本名称 |

---

## 平台支持

| 平台 | URL特征 | 下载方式 |
|------|---------|----------|
| 小红书 | `xiaohongshu.com` / `xhslink.com` | yt-dlp |
| B站 | `bilibili.com` / `b23.tv` | B站API |

---

## 使用示例

```bash
# 小红书视频
python scripts/xiaohongshu_download_and_summarize.py "https://www.xiaohongshu.com/explore/xxx"

# B站视频
python scripts/bilibili_download.py "https://www.bilibili.com/video/BVxxxxxx"

# B站短链接
python scripts/bilibili_download.py "https://b23.tv/xxxxxx"

# 运行测试
python -m unittest discover -s tests -v
```

---

## 版本信息

- **Python:** 3.9+
- **yt-dlp:** >= 2024.01.01
- **FFmpeg:** >= 4.0
- **openai-whisper:** >= 20231117
- **requests:** >= 2.28.0
