# 视频下载和总结 Skill

自动下载**小红书**和**B站**视频并生成转录和总结的AI skill。

## 支持平台

| 平台 | URL特征 | 下载方式 |
|------|---------|----------|
| 小红书 | `xiaohongshu.com` | yt-dlp |
| B站 | `bilibili.com` / `b23.tv` | B站API（绕过风控） |

## 快速开始

### 1. 安装依赖

```bash
bash scripts/install_deps.sh
```

或手动安装：
```bash
pip install yt-dlp openai-whisper requests
brew install ffmpeg  # macOS
```

### 2. 使用脚本

**小红书视频：**
```bash
python scripts/xiaohongshu_download_and_summarize.py "小红书视频URL"
# 输出文件保存在 ./temp/ 目录
```

**B站视频：**
```bash
python scripts/bilibili_download.py "https://www.bilibili.com/video/BVxxxxxx"
# 支持短链接
python scripts/bilibili_download.py "https://b23.tv/xxxxxx"
# 输出文件保存在 ./temp/ 目录
```

### 3. 可选参数

**小红书脚本：**
```bash
# 使用更高精度的Whisper模型
python scripts/xiaohongshu_download_and_summarize.py "URL" --model medium

# 保留所有文件（默认删除临时文件）
python scripts/xiaohongshu_download_and_summarize.py "URL" --keep-files

# 指定输出目录
python scripts/xiaohongshu_download_and_summarize.py "URL" --output-dir ./results
```

**B站脚本：**
```bash
# 指定输出目录
python scripts/bilibili_download.py "URL" --output-dir ./videos

# 保留临时文件
python scripts/bilibili_download.py "URL" --keep-files
```

## 工作流程

### 小红书
1. **下载视频** - 使用yt-dlp + 小红书专用headers
2. **提取音频** - 使用FFmpeg从视频中提取音频
3. **转录文字** - 使用OpenAI Whisper进行语音转文字
4. **生成总结** - 对转录内容进行总结
5. **输出结果** - 显示在命令行并保存文件

### B站
1. **获取视频信息** - 调用B站API获取aid、cid
2. **获取播放地址** - 获取DASH格式音视频URL
3. **下载音视频** - 分别下载视频流和音频流
4. **合并文件** - 使用FFmpeg合并为完整视频

## 运行测试

本项目包含完整的单元测试，用于验证脚本功能。

### 运行所有测试

```bash
cd /path/to/video-summary
python -m unittest discover -s tests -v
```

### 运行单个测试文件

```bash
# B站下载脚本测试
python tests/test_bilibili_download.py

# 小红书下载脚本测试
python tests/test_xiaohongshu_download.py
```

### 运行特定测试类

```bash
# 测试B站BV号提取
python -m unittest tests.test_bilibili_download.TestExtractBvid -v

# 测试小红书内容总结
python -m unittest tests.test_xiaohongshu_download.TestSummarizeContent -v
```

### 测试覆盖范围

| 测试文件 | 测试数量 | 覆盖内容 |
|----------|----------|----------|
| `test_bilibili_download.py` | 16个 | 初始化、BV号提取、短链接解析、API调用、播放地址、清理 |
| `test_xiaohongshu_download.py` | 18个 | 初始化、内容总结、结果保存、下载、音频提取、转录 |

### 预期输出

```
test_init_with_default_params ... ok
test_extract_bvid_standard_url ... ok
...
Ran 34 tests in 0.018s
OK
```

## Whisper模型对比

| 模型 | 相对速度 | 相对准确度 | 适用场景 |
|------|---------|----------|--------|
| tiny | 最快 ⚡ | 最低 | 快速检查内容概况 |
| base | 快 ⚡ | 中等 ✓ | **推荐**（平衡） |
| small | 中等 | 较好 | 高要求的转录 |
| medium | 慢 | 好 | 专业内容 |
| large | 最慢 🐢 | 最好 | 关键内容必须精准 |

## 注意事项

- 首次运行Whisper会自动下载模型文件（约140MB for base）
- 长视频处理时间较长（取决于视频长度和所选模型）
- 建议在网络稳定的环境下运行
- B站视频**不能**直接用yt-dlp下载（会触发HTTP 412风控），必须使用专用脚本
- B站会员专属视频无法下载

## 故障排除

### "yt-dlp command not found"
```bash
pip install yt-dlp
```

### "FFmpeg not found"
```bash
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu/Debian
```

### "Whisper not installed"
```bash
pip install openai-whisper
```

### "requests module not found"
```bash
pip install requests
```

### B站下载HTTP 412错误
确保使用 `bilibili_download.py` 脚本，不要用yt-dlp直接下载。

### 下载失败或被封禁
- 检查URL格式是否正确
- 等待一段时间后重新尝试
- 确保网络连接正常

## 文件结构

```
video-summary/
├── SKILL.md                    # Skill说明文档
├── README.md                   # 本文件
├── scripts/
│   ├── xiaohongshu_download_and_summarize.py  # 小红书下载脚本
│   ├── bilibili_download.py    # B站下载脚本
│   └── install_deps.sh         # 依赖安装脚本
├── tests/
│   ├── __init__.py             # 测试包初始化
│   ├── conftest.py             # 测试配置
│   ├── test_bilibili_download.py    # B站脚本测试
│   └── test_xiaohongshu_download.py # 小红书脚本测试
├── references/                 # 参考文档
└── evals/
    └── evals.json              # 测试用例
```

## 技术栈

- **Python 3.9+** - 脚本语言
- **yt-dlp** - 视频下载工具（小红书）
- **requests** - HTTP请求（B站API）
- **FFmpeg** - 音视频处理
- **OpenAI Whisper** - 语音转文字

## 许可证

MIT
