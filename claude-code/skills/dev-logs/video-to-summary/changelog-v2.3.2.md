# video-to-summary-v2 Changelog v2.3.2

## 问题描述

**核心问题**：Skill 在本地调试 OK 之后，打包到 `~/.claude/skills/` 目录后，能成功触发（被击中），但不按 SKILL.md 中的说明执行 Python 程序。

**具体表现**：
- 用户输入视频 URL 时，skill 成功加载
- 但模型没有执行 `bash run.sh "URL"` 或 `python scripts/video_to_summary.py`
- 反而尝试使用 `WebFetch` 工具抓取视频页面
- 或者输出 "Searched for 2 patterns"、"TaskOutput" 等非预期行为

---

## 问题根因分析

Claude Code 加载 skill 后，模型对 SKILL.md 的**执行率不高**。可能原因：

1. **SKILL.md 文档太长** - 127 行的详细文档，模型没有仔细阅读关键指令
2. **指令不够明确** - 使用了 "视频文件需要下载后才能处理" 这类描述性语言
3. **缺少强制执行标记** - 没有 "IMMEDIATELY execute" 这类强制短语
4. **路径问题** - 项目中使用 `/Users/chen/Project/AI_Road/...`，但实际加载路径是 `~/.claude/skills/`

---

## 尝试的 SKILL.md 版本

### 版本 1：原始详细文档（失败）

**文件位置**：`/Users/chen/Project/AI_Road/Claude/skills/video-to-summary-v2/SKILL.md`

特点：
- 127 行，包含完整配置说明、输出文件结构、故障排除
- 使用描述性语言："视频文件需要下载后才能处理"
- 提供多种参数选项

**结果**：模型不使用脚本

---

### 版本 2：简化版（/Users/chen/.claude/skills/）

**文件位置**：`/Users/chen/.claude/skills/video-to-summary-v2/SKILL.md`

修改内容：
- 简化为约 50 行
- 增加明确工作流程："使用 Bash 工具执行"
- 添加禁止指令："不要使用 TaskOutput 或其他工具"

关键代码：
```bash
cd ~/.claude/skills/video-to-summary-v2 && python scripts/video_to_summary.py "视频URL"
```

**结果**：部分改进，但仍不稳定

---

### 版本 3：Immediate Action Protocol（当前版本）

**文件位置**：`/Users/chen/Project/AI_Road/Claude/skills/video-to-summary-v2/SKILL.md`（用户修改）

修改内容：
- 开头就是明确的 "IMMEDIATELY HANDLE ANY VIDEO URL"
- 使用 `run.sh` 包装脚本而非直接调用 Python
- 简洁的工作流程步骤（1. Run, 2. Read, 3. Present）
- 更短的文档（约 100 行但结构清晰）

关键代码：
```bash
bash /Users/chen/Project/AI_Road/Claude/skills/video-to-summary-v2/run.sh "VIDEO_URL"
```

---

## 当前状态

**问题未完全解决**。模型有时仍会跳过执行脚本。

---

## 待验证方案

1. **检查 run.sh 是否存在** - 确认 `/Users/chen/Project/AI_Road/Claude/skills/video-to-summary-v2/run.sh` 文件存在且可执行
2. **同步文件到 ~/.claude/skills/** - 将修改后的 SKILL.md 复制到安装目录
3. **测试 skill 触发** - 使用相同视频 URL 测试

---

## 经验总结

1. **skill 执行率问题**：SKILL.md 写得再好，模型也可能不按指示执行
2. **路径一致性**：开发目录和安装目录的路径差异可能导致问题
3. **文档风格**：成功的 skill 倾向于开头就是可执行代码，而非详细说明
4. **工具限制**：视频需要下载处理，不能用 WebFetch，这个限制需要更明确地传达
