# 小红书视频下载和总结 - 使用指南

## 概述

这个skill可以让Claude帮助用户自动化处理小红书视频：
- 下载视频
- 提取和转录音频为文字
- 生成内容总结

用户只需提供一个小红书视频URL，其余工作由skill自动完成。

## 何时触发此skill

当用户说出以下任何表述时，应该使用此skill：

- "下载这个小红书视频"
- "帮我转录这个小红书内容"
- "用这个视频链接生成文字稿"
- "我想要这个短视频的总结"
- "提取小红书视频里的关键词"
- "能不能帮我处理这个小红书链接"

## 实现细节

### 命令格式

基础用法，由Claude代表用户运行：

```bash
python scripts/xiaohongshu_download_and_summarize.py "https://www.xiaohongshu.com/explore/xxx"
```

### 带参数的用法

Claude可以根据用户需求调整参数：

```bash
# 如果用户需要更高准确度
python scripts/xiaohongshu_download_and_summarize.py "URL" --model medium

# 如果用户需要保留所有文件
python scripts/xiaohongshu_download_and_summarize.py "URL" --keep-files

# 如果用户需要保存到特定位置
python scripts/xiaohongshu_download_and_summarize.py "URL" --output-dir ~/Documents/videos
```

## 用户交互示例

### 场景1：基础使用

**用户**: "帮我下载并总结这个小红书视频：https://www.xiaohongshu.com/explore/65a1b2xxx"

**Claude**:
1. 检查依赖是否已安装
2. 运行脚本处理视频
3. 输出转录和总结内容
4. 告诉用户结果文件的位置

### 场景2：需要更高精度

**用户**: "我需要完整准确的文字稿，最好不要漏掉细节"

**Claude**:
1. 建议使用更大的Whisper模型（medium或large）
2. 运行：`python ... --model medium`
3. 等待处理完成（可能较长）
4. 提供准确率更高的转录结果

### 场景3：批量处理

**用户**: "我有5个小红书链接，能都处理一下吗？"

**Claude**:
1. 逐个处理每个URL
2. 为每个视频生成单独的转录和总结文件
3. 提供所有文件位置

## 错误处理约定

### 如果依赖未安装

提示用户安装：
```bash
bash scripts/install_deps.sh
```

### 如果下载失败

可能的原因和解决方案：
- URL不正确或已失效 → 让用户确认URL
- 网络问题 → 建议稍后重试
- 被小红书封禁 → 建议使用VPN或等待

### 如果Whisper转录失败

- 检查音频质量是否过差
- 尝试不同的语言代码
- 考虑使用不同的模型

## 配置建议

### 对于一般用户

```bash
python scripts/xiaohongshu_download_and_summarize.py "URL"
```
- 使用默认的base模型
- 自动删除临时文件
- 结果显示在命令行

### 对于内容创作者

```bash
python scripts/xiaohongshu_download_and_summarize.py "URL" --keep-files --output-dir ~/Videos
```
- 保留所有原始文件用于进一步编辑
- 指定输出目录便于管理

### 对于精确度要求高的用户

```bash
python scripts/xiaohongshu_download_and_summarize.py "URL" --model medium
```
- 使用medium或large模型获得更高准确度
- 处理时间会更长，但转录质量更好

## 输出示例

```
==================================================
===== 小红书视频内容总结 =====
==================================================
URL: https://www.xiaohongshu.com/explore/xxx
处理时间: 2024-01-15T14:30:45.123456

【完整转录】
今天要和大家分享一个很有用的小技巧...
[完整的转录文本]

【核心要点总结】
1. 主要讲述了某某技巧的使用方法
2. 强调了三个关键步骤...
[总结内容]

==================================================
【处理完成】
转录文件: /Users/xxx/transcript_20240115_143045.txt
总结文件: /Users/xxx/summary_20240115_143045.txt
==================================================
```

## 常见问题和回答

**Q: 这个工具支持其他平台吗？**
A: 目前特定于小红书优化。其他平台如TikTok、YouTube需要不同的配置。

**Q: 转录的准确度如何？中文支持好吗？**
A: Whisper base模型中文准确度约80-90%，取决于音频质量。如需更高准确度，可使用medium或large模型。

**Q: 视频会被保存吗？**
A: 默认不保存。处理完成后自动删除临时文件。使用`--keep-files`参数可保留。

**Q: 长视频会花很长时间吗？**
A: 是的。处理时间取决于视频长度和选择的Whisper模型。Base模型相对较快。

**Q: 可以同时处理多个视频吗？**
A: 可以，但需逐个处理。建议按顺序提供多个URL。

## 故障排除指南

| 问题 | 解决方案 |
|------|--------|
| yt-dlp command not found | `pip install yt-dlp` |
| FFmpeg not found | `brew install ffmpeg` |
| Whisper not installed | `pip install openai-whisper` |
| 下载失败 | 检查URL、网络连接，稍后重试 |
| 转录出错 | 确保音频质量，检查语言设置 |
| 进程超时 | 稍后重试，考虑使用较小的Whisper模型 |

## 性能参考

基于base模型的典型处理时间：

| 视频长度 | 预计时间 |
|---------|---------|
| 1分钟 | 2-3分钟 |
| 5分钟 | 8-12分钟 |
| 10分钟 | 15-25分钟 |
| 30分钟以上 | 1小时+ |

时间取决于：
- 计算机性能
- 网络速度（下载阶段）
- 音频质量
- Whisper模型大小
