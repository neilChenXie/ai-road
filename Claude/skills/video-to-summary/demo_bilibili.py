#!/usr/bin/env python3
"""
演示如何使用视频转文字总结工具处理Bilibili链接
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demonstrate_bilibili_processing():
    """演示Bilibili视频处理流程"""
    print("🎬 Bilibili视频转文字总结工具演示")
    print("=" * 60)
    
    # 你的Bilibili链接
    bilibili_url = "https://b23.tv/hHipbJS"
    print(f"📺 目标视频: {bilibili_url}")
    print()
    
    from utils.platform_detector import (
        detect_platform, get_platform_info, 
        get_platform_recommendations
    )
    
    # 1. 平台检测
    print("1️⃣ 平台检测和分析")
    print("-" * 40)
    
    platform = detect_platform(bilibili_url)
    platform_info = get_platform_info(bilibili_url)
    recommendations = get_platform_recommendations(bilibili_url)
    
    print(f"✅ 检测到平台: {platform_info['name']}")
    print(f"   平台ID: {platform_info['id']}")
    print(f"   配置: {platform_info['config']}")
    print()
    
    print("📋 处理建议:")
    for rec in recommendations.get('general', []):
        print(f"   • {rec}")
    
    if 'yt-dlp_options' in recommendations:
        print(f"\n🛠️ 推荐yt-dlp参数:")
        for opt in recommendations['yt-dlp_options']:
            print(f"   {opt}")
    
    print()
    
    # 2. 构建处理命令
    print("2️⃣ 构建处理命令")
    print("-" * 40)
    
    # 基本命令
    base_cmd = "python scripts/video_to_summary.py"
    
    # 针对Bilibili的优化参数
    bilibili_params = [
        f'--url "{bilibili_url}"',
        '--output-dir "./bilibili_output"',
        '--language "zh"',
        '--model "base"',
        '--summary-style "brief"'
    ]
    
    # Bilibili特定建议
    if platform_info['config'].get('needs_referer', False):
        bilibili_params.append('# --referer "https://www.bilibili.com"  # B站需要referer')
    
    full_cmd = f"{base_cmd} {' '.join(bilibili_params)}"
    
    print("💻 完整命令:")
    print(f"   {full_cmd}")
    print()
    
    # 3. 批量处理示例
    print("3️⃣ 批量处理示例")
    print("-" * 40)
    
    batch_example = """# 创建URL列表文件
cat > bilibili_urls.txt << EOF
https://b23.tv/hHipbJS
https://www.bilibili.com/video/BV12CA1zhEmK
# 更多B站视频...
EOF

# 批量处理（3个并行，中文识别）
bash scripts/batch_process.sh -i bilibili_urls.txt -p 3 -l zh
"""
    
    print(batch_example)
    print()
    
    # 4. 预期输出
    print("4️⃣ 预期输出文件")
    print("-" * 40)
    
    expected_files = """
output/bilibili_output/YYYYMMDD_HHMMSS_任务ID/
├── video.mp4                    # 下载的视频文件（如果未使用--audio-only）
├── audio.mp3                    # 提取的音频文件
├── transcript.txt               # 完整文字转录
├── transcript_with_timestamps.txt # 带时间戳的转录
├── summary.md                   # 智能总结报告
├── key_points.json              # 关键要点（JSON格式）
├── metadata.json                # 处理元数据
└── 处理报告.md                  # 详细处理报告
"""
    
    print(expected_files)
    print()
    
    # 5. 实际使用建议
    print("5️⃣ 实际使用建议")
    print("-" * 40)
    
    suggestions = [
        "对于Bilibili视频，可能需要设置referer头",
        "长视频建议使用 --audio-only 参数仅处理音频",
        "中文内容使用 --language zh 提高识别准确率",
        "网络不稳定时，可以增加超时时间",
        "批量处理时，根据服务器性能调整并行数量"
    ]
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
    
    print()
    
    # 6. 故障排除
    print("6️⃣ Bilibili特定故障排除")
    print("-" * 40)
    
    troubleshooting = {
        "HTTP 412错误": "B站反爬虫机制，需要设置合适的headers",
        "下载速度慢": "尝试使用 --quality 720p 降低质量",
        "无法获取视频信息": "可能需要模拟浏览器访问",
        "音频提取失败": "检查ffmpeg安装和权限"
    }
    
    for issue, solution in troubleshooting.items():
        print(f"• {issue}: {solution}")
    
    print()
    print("=" * 60)
    print("🚀 开始处理你的Bilibili视频:")
    print()
    print(f"   1. 进入工具目录:")
    print(f"      cd /root/.openclaw/workspace/video-to-summary-skill")
    print()
    print(f"   2. 激活虚拟环境:")
    print(f"      source venv/bin/activate")
    print()
    print(f"   3. 运行处理命令:")
    print(f"      python scripts/video_to_summary.py \\")
    print(f"        --url \"{bilibili_url}\" \\")
    print(f"        --language zh \\")
    print(f"        --audio-only \\")
    print(f"        --model tiny")
    print()
    print("💡 提示: 第一次运行时，建议先用 --audio-only 和 --model tiny 快速测试")
    print("=" * 60)

def demonstrate_url_expansion():
    """演示URL展开功能"""
    print("\n🔗 URL展开功能演示")
    print("=" * 60)
    
    print("你的链接是Bilibili短链接: https://b23.tv/hHipbJS")
    print("这种短链接需要展开为完整URL才能处理")
    print()
    
    print("工具内置的URL处理功能:")
    print("1. 自动检测短链接平台")
    print("2. 尝试获取重定向后的真实URL")
    print("3. 提取视频ID和基本信息")
    print()
    
    print("手动展开示例:")
    print("```bash")
    print("# 使用curl获取重定向")
    print('curl -s -L -I "https://b23.tv/hHipbJS" | grep -i location')
    print()
    print("# 或者使用Python")
    print('import requests')
    print('response = requests.head("https://b23.tv/hHipbJS", allow_redirects=True)')
    print('print("最终URL:", response.url)')
    print("```")
    
    print()
    print("在我们的工具中，这些步骤已经自动化:")
    print("✅ 平台自动检测")
    print("✅ URL验证和标准化")
    print("✅ 平台特定参数配置")
    print("✅ 错误处理和重试机制")

def main():
    """主演示函数"""
    demonstrate_bilibili_processing()
    demonstrate_url_expansion()
    
    print("\n🎯 总结:")
    print("你的工具已经具备了完整的Bilibili视频处理能力:")
    print("1. ✅ 平台检测和URL处理（支持短链接）")
    print("2. ✅ 视频下载和音频提取")
    print("3. ✅ 语音转文字和智能总结")
    print("4. ✅ 批量处理和错误恢复")
    print("5. ✅ 生产环境部署支持")
    print()
    print("📅 下一步:")
    print("现在就可以用你的Bilibili链接进行真实测试！")

if __name__ == "__main__":
    main()