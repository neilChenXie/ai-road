# 🎥 视频转文字总结工具

基于URL的完整视频内容分析工具链，一站式解决：视频下载 → 音频提取 → 语音转文字 → 智能总结

## ✨ 功能特性

### 🎯 核心功能
- **多平台支持**: YouTube, Bilibili, 小红书, 抖音, Twitter, Instagram等数千个网站
- **完整流程**: 视频下载 → 音频提取 → 语音转文字 → 智能总结
- **智能分析**: 自动提取关键信息，生成结构化总结
- **批量处理**: 支持批量URL处理，自动并行化

### 🛠️ 技术特点
- **模块化设计**: 每个功能独立模块，易于扩展和维护
- **多引擎支持**: Whisper、Google语音、Azure语音等多种语音识别引擎
- **智能适配**: 自动检测平台，使用最优配置
- **质量保证**: 音频增强、降噪处理、分段优化

### 📊 输出格式
- 完整文字转录（带时间戳）
- 智能总结报告（Markdown格式）
- 关键要点提取（JSON格式）
- 处理元数据（JSON格式）
- 详细分析报告

## 🚀 快速开始

### 安装依赖
```bash
# 运行安装脚本
chmod +x install.sh
./install.sh

# 或手动安装
pip install yt-dlp ffmpeg-python whisper speechrecognition pydub
sudo apt-get install ffmpeg  # Ubuntu/Debian
```

### 基本使用
```bash
# 单个视频处理
python scripts/video_to_summary.py --url "https://www.youtube.com/watch?v=xxx"

# 仅处理音频
python scripts/video_to_summary.py --url "URL" --audio-only

# 批量处理
bash scripts/batch_process.sh -i urls.txt -p 3
```

## 📁 项目结构
```
video-to-summary-skill/
├── SKILL.md                    # 技能说明文档
├── README.md                   # 项目说明
├── requirements.txt            # Python依赖
├── install.sh                  # 安装脚本
├── config/                     # 配置文件目录
├── output/                     # 输出文件目录
├── scripts/                    # 执行脚本
│   ├── video_to_summary.py     # 主程序
│   ├── batch_process.sh        # 批量处理脚本
│   └── process_video.sh        # 单视频处理脚本
└── utils/                      # 工具模块
    ├── video_downloader.py     # 视频下载
    ├── audio_extractor.py      # 音频提取
    ├── speech_to_text.py       # 语音转文字
    ├── text_summarizer.py      # 文本总结
    └── platform_detector.py    # 平台检测
```

## 🔧 详细使用

### 命令行参数
```bash
python scripts/video_to_summary.py --help

# 必需参数
--url URL                    视频URL

# 输出配置
--output-dir DIR            输出目录（默认: ./output）
--audio-only                仅处理音频（不下载视频）

# 识别配置
--language LANG            语音识别语言（默认: auto）
--model MODEL              Whisper模型大小（tiny, base, small, medium, large）

# 总结配置
--summary-model MODEL      总结模型（默认: gpt-3.5-turbo）
--summary-style STYLE      总结风格（brief, detailed, academic）
```

### 批量处理
```bash
# 创建URL列表文件
cat > urls.txt << EOF
https://www.youtube.com/watch?v=xxx
https://www.bilibili.com/video/BVxxx
https://www.xiaohongshu.com/discovery/item/xxx
EOF

# 批量处理
bash scripts/batch_process.sh -i urls.txt -p 3 -l zh

# 查看结果
ls -la output/batch_*/
```

### 支持的平台
| 平台 | 状态 | 特点 |
|------|------|------|
| YouTube | ✅ 完整支持 | 需要cookies避免403 |
| Bilibili | ✅ 完整支持 | 支持高清、字幕 |
| 小红书 | ✅ 支持 | 部分视频可能需要特殊处理 |
| 抖音 | ✅ 支持 | 短视频优化 |
| Twitter/X | ✅ 支持 | 视频和音频提取 |
| Instagram | ✅ 支持 | Reels和普通视频 |
| 通用视频 | ✅ 支持 | 兼容大多数网站 |

## ⚙️ 配置说明

### 环境变量（可选）
```bash
# OpenAI API（用于高级总结）
export OPENAI_API_KEY="sk-..."

# Azure语音服务
export AZURE_SPEECH_KEY="..."
export AZURE_SPEECH_REGION="..."

# Claude API
export ANTHROPIC_API_KEY="..."
```

### 配置文件
创建 `config/settings.yaml`：
```yaml
# 下载配置
download:
  output_dir: "./output"
  cookies_browser: "chrome"
  max_quality: "best"
  timeout: 300

# 语音识别
speech_to_text:
  default_model: "base"
  default_language: "auto"
  fallback_engines: ["google", "whisper"]

# 总结配置
summarization:
  default_style: "brief"
  max_length: 1000
  extract_key_points: true

# 平台特定配置
platforms:
  youtube:
    needs_cookies: true
    recommended_quality: "best"
  bilibili:
    needs_referer: true
```

## 📈 输出示例

### 处理后的目录结构
```
output/20240101_120000_abc123/
├── video.mp4                    # 原始视频（可选）
├── audio.mp3                    # 提取的音频
├── transcript.txt               # 完整文字转录
├── transcript_with_timestamps.txt
├── summary.md                   # 智能总结
├── key_points.json              # 关键要点
├── metadata.json                # 处理元数据
└── 处理报告.md                  # 详细报告
```

### 总结报告示例
```markdown
# 📝 视频内容总结

## 基本信息
- 总结时间: 2024-01-01 12:00:00
- 总结方法: abstractive
- 总结风格: brief
- 语言: zh

## 内容摘要
视频讨论了人工智能在医疗领域的应用，包括诊断辅助、药物研发和个性化治疗...

## 主要主题
- 人工智能
- 医疗诊断
- 药物研发
- 个性化医疗

## 关键观点
1. AI可以显著提高疾病诊断的准确率
2. 机器学习加速了药物发现过程
3. 个性化治疗是未来医疗发展方向
```

## 🔍 高级功能

### 音频增强
```python
# 自动降噪和标准化
enhanced_audio = enhance_audio(
    audio_path, 
    output_dir,
    noise_reduction=True,
    normalize=True,
    remove_silence=False
)
```

### 长视频分段处理
```python
# 自动分段处理长视频（>10分钟）
segments = split_audio_by_duration(audio_path, temp_dir, 600)
```

### 自定义总结模板
```yaml
# 创建自定义总结模板
custom_templates:
  business_report:
    sections: ["执行摘要", "市场分析", "竞争态势", "建议方案"]
  academic_lecture:
    sections: ["讲座主题", "核心论点", "研究方法", "主要发现", "启示意义"]
```

## 🐛 故障排除

### 常见问题

1. **YouTube 403错误**
   ```bash
   # 使用浏览器cookies
   python scripts/video_to_summary.py --url "URL" --cookies-browser chrome
   ```

2. **音频提取失败**
   ```bash
   # 检查ffmpeg安装
   ffmpeg -version
   # 重新安装
   sudo apt-get install ffmpeg
   ```

3. **语音识别不准**
   ```bash
   # 尝试不同模型
   python scripts/video_to_summary.py --url "URL" --model "medium" --language "zh"
   ```

4. **内存不足（长视频）**
   ```bash
   # 使用音频-only模式
   python scripts/video_to_summary.py --url "URL" --audio-only
   # 或使用更小的模型
   python scripts/video_to_summary.py --url "URL" --model "base"
   ```

### 日志和调试
```bash
# 启用调试模式
python scripts/video_to_summary.py --url "URL" --debug

# 查看详细日志
tail -f output/*/logs/*.log
```

## 🤝 贡献指南

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/yourusername/video-to-summary-skill.git
cd video-to-summary-skill

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/
```

### 添加新平台支持
1. 在 `utils/platform_detector.py` 中添加平台检测规则
2. 在 `utils/video_downloader.py` 中添加平台特定配置
3. 更新文档和测试

### 代码规范
- 使用Black进行代码格式化
- 使用isort排序imports
- 添加类型注解
- 编写单元测试

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的视频下载工具
- [OpenAI Whisper](https://github.com/openai/whisper) - 高质量的语音识别
- [FFmpeg](https://ffmpeg.org/) - 多媒体处理框架

## 📞 支持与反馈

- 问题报告: [GitHub Issues](https://github.com/yourusername/video-to-summary-skill/issues)
- 功能建议: 通过Issue提交
- 紧急问题: 查看故障排除部分

---

**开始使用：**
```bash
./install.sh
python scripts/video_to_summary.py --url "你的第一个视频URL"
```

享受高效的视频内容分析体验！🎬📝✨