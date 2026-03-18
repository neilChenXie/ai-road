# Changelog - Video to Summary V2.2

## 发布日期
2026-03-16

## 主要更新

### CLI 命令简化 (核心改进)

解决了 `--url` 报错的问题。

**修改前：**
```bash
python3 scripts/video_to_summary.py --url "https://youtube.com/watch?v=xxx"
```

**修改后：**
```bash
python scripts/video_to_summary.py "https://youtube.com/watch?v=xxx"
```
### YAML front matter 规范化

description 字段添加引号包裹，符合 YAML 语法规范。
解决了之前“总结视频：URL”无法击中Skill的问题。

---

## 文件修改详情

### 1. `SKILL.md`

**修改内容：**

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| YAML description | 无引号 | 引号包裹（规范化） |
| pip 安装命令 | `pip3 install` | `pip install` |
| URL 参数 | `--url "URL"` | `"URL"` (位置参数) |
| python 命令 | `python3` | `python` |

**命令对比：**

```bash
# 旧命令
python3 scripts/video_to_summary.py --url "URL" --output-dir ./output

# 新命令
python scripts/video_to_summary.py "URL" --output-dir ./output
```

---

## 改进说明

1. **命令更简洁**
   - 移除冗余的 `--url` 标志
   - URL 作为位置参数更符合常见 CLI 工具习惯

2. **安装命令统一**
   - `pip` 替代 `pip3`，避免不同系统的命令差异

3. **YAML front matter 规范化**
   - description 字段添加引号包裹，符合 YAML 语法规范
   - 内部双引号改为单引号，避免转义问题

4. **项目结构更规范**
   - 添加 `.gitignore` 防止输出文件被提交

---

## 使用示例

```bash
# 处理 YouTube 视频
python scripts/video_to_summary.py "https://youtube.com/watch?v=xxx"

# 处理 Bilibili 视频
python scripts/video_to_summary.py "https://b23.tv/xxx"

# 处理小红书视频
python scripts/video_to_summary.py "https://www.xiaohongshu.com/..."

# 指定 Whisper 模型
python scripts/video_to_summary.py "URL" --model medium

# 音频模式（更快）
python scripts/video_to_summary.py "URL" --audio-only

# 自定义输出目录
python scripts/video_to_summary.py "URL" --output-dir ~/videos/analysis
```
