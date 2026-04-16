## video-to-summary开发经验

[博客：基于OpenClaw和Claude Code搭建视频下载总结工作流](https://chenxie.fun/post/building-a-video-download-summary-workflow-based-on-openclaw-and-claude-code-xnwff.html)

### 必备技能（人）

#### 对AI能力的理解

如果AI认为SKILL.md中的方式太低效，会自己跳过我们写的脚本！

```
测试scripts下的脚本OK，但claude就不按SKILL.md的流程运行脚本

这是一个很常见的 Skill 编写问题——Claude 没有被强制执行 Skill 中的脚本，而是自行决定用更简单的方式完成任务。Claude 是一个有自主判断能力的AI，SKILL.md 不是程序代码，是对 Claude 的"指令"。写得越明确、越强硬，Claude 就越会照做。

根本原因:
Skill 的 SKILL.md 本质上是给 Claude 看的说明文档，Claude 会阅读后自行决定怎么做。如果 Claude 认为直接用命令行更简单，它就会跳过你的 Python 脚本。

解决方法：(按经验不一定100%生效)
1. 在 SKILL.md 中明确强制要求

## ⚠️ 重要：必须使用本 Skill 的 Python 脚本

**禁止**直接调用 yt-dlp、whisper 等命令行工具。
必须通过运行 `python skill_script.py` 来完成任务。


2. 把逻辑封装进脚本，降低"绕过"的动机
如果你的 Python 脚本只是简单封装了命令行调用，Claude 会觉得"我直接调用更省事"。应该把真正的价值放进脚本里，比如：
* 自动处理错误重试
* 格式化输出结果
* 多步骤流程编排
```

Deepseek-v3.2支持128K上下文，开发过程中出现超出context限制的问题。

*[信息源](https://docsbot.ai/models/compare/glm-5/minimax-m2-5)*

| 模型名称 | 支持的最大上下文窗口 (Tokens) |
| :--------- | :------------------------------ |
| **Kimi-2.5**         | **262K**                              |
| **GLM-5**         | **200K**                              |
| **Minimax-M2.1**         | **未明确**                              |
| **Minimax-M2.5**         | **1000K (1M)**                              |
| **Claude Sonnet 4.6**         | **200K / 1000K (1M)**                              |
| **Claude Haiku 4.5**         | **200K**                              |
| **GPT-4o**         | **128K**                              |
| **GPT-5 mini**         | **400K**                              |

#### 必会工具

使用Claude官方的`/skill-creator`这个skill来创建SKILL。

使用官方校验工具`skills-ref`：https://github.com/agentskills/agentskills/tree/main/skills-ref

> 生成的Description有格式问题，导致“总结视频”等指令**击不中**本Skill

`yt-dlp`基本用法

`ffmpeg`基本用法

#### SKILL的标准文件架构 #skills#

```bash
skill-name/
├── SKILL.md          ← 必须，核心文件
└── （可选资源）
   ├── scripts/      ← 可执行脚本，用于确定性/重复性任务
   ├── references/   ← 按需加载到上下文的参考文档
   └── assets/       ← 输出中用到的文件（模板、字体、图标等）
```

#### SKILL运行的加载顺序 #skills#

1. Claude启动时，只加载SKILL.md的YAML头
2. 当指令击中YAML头后，AI读取SKILL.md的正文，了解该如何执行。（本项目经验，如果AI认为此文档的流程太繁琐，它会自己执行，不遵循SKILL.md文档正文。
3. 执行过程中，如果AI发现需要脚本时，运行scripts下的脚本。

![image](https://chenxie-fun.oss-cn-shenzhen.aliyuncs.com/se_roadimage-20260319160629-gh3ffpx.png)

#### 如何测试SKILL #skills#

SKILL.md文档，应该是结构清晰可读，所以需要人工阅读理解(也可以借助AI给意见)
脚本可以单独测试能否跑通，如果工程化，需包含单元测试（官方evals不包含）

```bash
your-skill/
├── SKILL.md
├── scripts/
│   └── process.py
└── tests/              ← 自己加，不是 evals 体系的一部分
    └── test_process.py
```

#### claude code的读取文件范围 #claude_code#

Claude会自动读取本目录、多级父目录（根含.claude）

```bash
 AI_Road
 ├── .claude/
 └── Claude/
    └─── skills/
        ├── video-to-summary/
        └── video-to-summary-v2/
```

### 工作流及过程控制 #git#

#### 通过git的了解具体修改了什么

代码通过git管理，`VS Source Control` 或 `GitLens`了解具体修改了什么。

**VS自带Source Control**

![image](https://chenxie-fun.oss-cn-shenzhen.aliyuncs.com/se_roadimage-20260316154007-2lplmc8.png)

![image](https://chenxie-fun.oss-cn-shenzhen.aliyuncs.com/se_roadimage-20260316154148-n7g2aai.png)

**使用 GitLens 扩展（推荐）**

**安装 GitLens**

1. 打开扩展面板（`Ctrl + Shift + X`）
2. 搜索并安装  **"GitLens"**  扩展

**使用 GitLens 对比**

1. **打开 GitLens 面板**：

   - 点击左侧活动栏的 GitLens 图标
   - 或按 `Ctrl + Shift + G`然后切换到 GitLens 视图
2. **对比提交**：

   - 在  **"COMMITS"**  部分找到要对比的提交
   - 右键点击较新的 commit，选择  **"Select for Compare"**
   - 右键点击较旧的 commit，选择  **"Compare with Selected"**
3. **查看差异**：

   - 差异会显示在专门的对比编辑器中
   - 左侧是旧版本，右侧是新版本

#### 让AI输出开发日志

```bash
# 与AI对话，用一个Session来开发一个功能或调试一个BUG。
# 在完成or多次尝试放弃后，让AI生成总结
Review本次多轮对话的内容，将本次开发解决的问题，修改的代码解释，输出到[PATH-To-PROJECT]/dev-logs/[时间or版本].md
```

![](https://chenxie-fun.oss-cn-shenzhen.aliyuncs.com/se_roadexcalidraw-image-20260318103504-spp1yy0.svg)

### 重要经验

无法击中skill，description的格式错误

通过python运行ok，copy到~/.claude/skills/之后反而不行，且跳脱出script，可能是SKILL.md中，没有说明脚本的路径！

这也解释了，为啥在这个/Project/目录下能运行，因为SKILL.md中，说的是`python scripts/video_to_summary.py "URL" --output-dir ./output`，脚本是相对路径。

![image](https://chenxie-fun.oss-cn-shenzhen.aliyuncs.com/se_roadimage-20260317175805-ymdtsoa.png)

改了之后，还是没有运行python脚本

```bash
我的指令"总结视频：https://www.xiaohongshu.com/discovery/item/69789b0c000000000a03e904?app_platform=ios&app_version=9.19.1&share_from_user_hidden=true&xsec_source=app_share&type=video&xsec_token=CBasxfKm6Hps04unTQe7LYoxsL3HsD1XtgYhZjwGw4ow4=&author_share=1&xhsshare=CopyLink&shareRedId=Nz0yQUg9NkFHTEk5PkA0PTk1QT1KPThN&apptime=1770074094&share_id=32c42785d8c04da9a94ab7fad47caf04&recLinkType=video”
⏺ Skill(video-to-summary-v2)  
  ⎿  Successfully loaded skill 

⏺ Searched for 2 patterns (ctrl+o to expand)

⏺ 让我帮你获取这个小红书视频的内容并生成总结。

⏺ Fetch(https://www.xiaohongshu.com/discovery/item/69789b0c000000000a03e904)
```

claude分析的原因是`SKILL.md`的描述不够直接，让大模型自己去`fetch url`了。通过修改SKILL.md，更明确一步一步执行，Debug了这个问题。

### 部署经验

#### yt-dlp无法下载视频

可能是yt-dlp版本问题，更新yt-dlp版本即可。

```bash
[generic] Extracting URL: ...
[generic] Falling back on generic information extractor
ERROR: Unsupported URL
```