# video-to-summary Changelog v2.3.1

## 摘要
放到~/.claude/skills/文件夹下，无法正常运行。
试图知道如何调试一个skill，了解到skill-creator这个官方创建skill的skill。
试图通过skill-creator来调试优化，结果没有解决问题。

Review之前成功的，发现之前是在直接执行python脚本
```bash
Bash(cd /Users/chen/Project/AI_Road/Claude/.tmp/../skills/video-to-summary && python3 scripts/video_to_summary.py "https://www.xiaohongshu.com/discovery/item/6988680…)
```

所以，我定位到问题：放到~/.claude/skills/文件夹下后，运行“总结视频：xxx”，根本没有去跑python脚本（AI基于自己的理解在用yt-dlp）。

## 过程

人工小改之后，放到claude code发现无法正常运行。
然后我询问claude.ai
```bash
我要写一个SKILL，标准的文件架构是什么样的？
# skill-name/
# ├── SKILL.md          ← 必须，核心文件
# └── （可选资源）
#    ├── scripts/      ← 可执行脚本，用于确定性/重复性任务
#    ├── references/   ← 按需加载到上下文的参考文档
#    └── assets/       ← 输出中用到的文件（模板、字体、图标等）

如果我在一个Project文件夹下开发我的skill项目，我能怎么测试我的skill？
# 回答像是我在线上弄了一个怎么测试

我在本地开发，也有claude Code工具。我的意思是，我的Skill项目没有放在~/.claude/skills/文件夹下，怎么测试能不能跑通
#通过回答，我了解有个skill-creator这个名词

skill-creator 是什么
#skill-creator 是 Anthropic 内置的一个 skill，专门用来帮你创建和优化其他 skill 的。
```
## 尝试skill-creator
然后得知了/skill-creator 这个官方创建skill的skill。
用以下命令试图优化我的skill
```bash
/skill-creator 检查video-to-summary skill存在哪些问题？
#发现了些问题，但就结果来看，没有解决核心问题
修复这些问题
#改完，手动复制到~/.claude/skills/

总结视频 https://www.xiaohongshu.com/discovery/item/6981f4a0000000001a028d46?app_platform=ios&app_version=9.19.4&share_from_user_hidden=true&xsec_source=app_share&type=video&xsec_token=CB8jYB5RyF-cLbhbT-nwGRrIdRfigS1zZoFFaSinhEInc=&author_share=1&xhsshare=CopyLink&shareRedId=Nz0yQUg9NkFHTEk5PkA0PTk1QT1KPThN&apptime=1771339938&share_id=22749b3a1bcc4fc0a4c294ff6b2164ae&recLinkType=video
#改完也不行

怎么测试 video-to-summary这个skill？
# 回复用skill-creator的evals/evals.json

基于这个项目的脚本，帮我写一下evals/evals.json
测试仅保留bilibli和xiaohongshu，其他先删掉
#不用测试youtube.com等

运行测试
#测试成功

找个temp文件夹，测试”总结视频：xxx“
#无论B站、小红书都不行
```

## 反观之前能成功的命令

```bash
❯ 视频总结：https://www.xiaohongshu.com/discovery/item/6988680a000000001a03589c?app_platform=ios&app_version=9.19.5&share_from_user_hidden=true&xsec_source=app_share&type=video&xsec_token=CBVhwelUP7oQfX3G3azO2ikYuqsJq-IA2CYBPJnDP3Re8=&author_share=1&xhsshare=CopyLink&shareRedId=Nz0yQUg9NkFHTEk5PkA0PTk1QT1KPThN&apptime=1772673082&share_id=0c21067a36fc457ba74db829309f4fa6&recLinkType=video

⏺ Skill(video-to-summary)
⎿  Successfully loaded skill

⏺ Read 1 file (ctrl+o to expand)

⏺ 我来帮你处理这个小红书视频。正在运行视频转文字工具。

⏺ Bash(cd /Users/chen/Project/AI_Road/Claude/.tmp/../skills/video-to-summary && python3 scripts/video_to_summary.py "https://www.xiaohongshu.com/discovery/item/6988680…)
   ⎿ 2026-03-16 18:21:01 - INFO - [1/6] 检测视频平台
     2026-03-16 18:21:01 - INFO - 平台: XiaoHongShu (小红书)
     2026-03-16 18:21:01 - INFO - [2/6] 下载视频 
     … +17 lines (ctrl+o to expand)
   ⎿  Shell cwd was reset to /Users/chen/Project/AI_Road/Claude/.tmp
   ⎿ (timeout10m) 

⏺ 视频处理完成。让我查看生成的总结。   
```

发现之前其实claude在直接执行python

```bash
Bash(cd /Users/chen/Project/AI_Road/Claude/.tmp/../skills/video-to-summary && python3 scripts/video_to_summary.py "https://www.xiaohongshu.com/discovery/item/6988680…)
```
## 找到关键问题

所以，我定位到问题：放到~/.claude/skills/文件夹下后，运行“总结视频：xxx”，根本没有去跑python脚本（AI基于自己的理解在用yt-dlp）。