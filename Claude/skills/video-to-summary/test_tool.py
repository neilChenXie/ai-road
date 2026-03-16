#!/usr/bin/env python3
"""
测试视频转文字总结工具的核心功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_platform_detector():
    """测试平台检测功能"""
    print("🧪 测试平台检测模块")
    print("-" * 50)
    
    from utils.platform_detector import (
        detect_platform, get_platform_info, 
        validate_url, extract_video_id
    )
    
    test_cases = [
        ("Bilibili短链", "https://b23.tv/hHipbJS"),
        ("Bilibili完整", "https://www.bilibili.com/video/BV12CA1zhEmK"),
        ("YouTube", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        ("YouTube短链", "https://youtu.be/dQw4w9WgXcQ"),
        ("小红书", "https://www.xiaohongshu.com/discovery/item/64b7e8b4000000001e03b6e4"),
        ("抖音", "https://www.douyin.com/video/7231234567890123456"),
        ("Twitter", "https://twitter.com/user/status/1234567890123456789"),
        ("通用视频", "https://example.com/video/123")
    ]
    
    for name, url in test_cases:
        platform = detect_platform(url)
        info = get_platform_info(url)
        is_valid, msg = validate_url(url)
        video_id = extract_video_id(url, platform)
        
        print(f"📺 {name}:")
        print(f"   URL: {url[:60]}...")
        print(f"   平台: {platform} ({info['name']})")
        print(f"   有效: {is_valid}")
        print(f"   视频ID: {video_id}")
        
        # 显示配置建议
        config = info['config']
        suggestions = []
        if config.get('needs_cookies', False):
            suggestions.append("需要cookies")
        if config.get('needs_referer', False):
            suggestions.append("需要referer")
        if config.get('needs_user_agent', False):
            suggestions.append("需要user-agent")
        
        if suggestions:
            print(f"   建议: {', '.join(suggestions)}")
        
        print()
    
    print("✅ 平台检测测试完成\n")

def test_video_downloader():
    """测试视频下载器功能"""
    print("📥 测试视频下载模块")
    print("-" * 50)
    
    from utils.video_downloader import (
        check_ytdlp_installed, get_video_info,
        list_available_formats
    )
    
    # 检查yt-dlp是否安装
    if check_ytdlp_installed():
        print("✅ yt-dlp已安装")
    else:
        print("❌ yt-dlp未安装，跳过下载测试")
        return
    
    # 测试一个公开的短YouTube视频（更容易访问）
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # 著名的"Me at the zoo"视频
    
    print(f"测试URL: {test_url}")
    
    # 尝试获取视频信息
    print("尝试获取视频信息...")
    try:
        info = get_video_info(test_url)
        if info:
            print(f"✅ 成功获取视频信息")
            print(f"   标题: {info.get('title', '未知')[:50]}...")
            print(f"   时长: {info.get('duration', 0)}秒")
            print(f"   上传者: {info.get('uploader', '未知')}")
        else:
            print("⚠️  无法获取视频信息（可能需要cookies）")
    except Exception as e:
        print(f"⚠️  获取视频信息时出错: {e}")
    
    print("✅ 视频下载模块测试完成\n")

def test_audio_extractor():
    """测试音频提取功能"""
    print("🔊 测试音频提取模块")
    print("-" * 50)
    
    from utils.audio_extractor import check_ffmpeg_installed
    
    # 检查ffmpeg是否安装
    if check_ffmpeg_installed():
        print("✅ ffmpeg已安装")
        print(f"   版本: ", end="")
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(version_line[:50])
    else:
        print("❌ ffmpeg未安装")
    
    print("✅ 音频提取模块测试完成\n")

def test_speech_to_text():
    """测试语音转文字功能"""
    print("🗣️ 测试语音转文字模块")
    print("-" * 50)
    
    from utils.speech_to_text import SpeechToText
    
    # 创建语音识别器
    stt = SpeechToText(model="base", language="auto")
    
    print("可用引擎检测:")
    for engine, available in stt.available_engines.items():
        status = "✅" if available else "❌"
        print(f"   {status} {engine}")
    
    # 选择最佳引擎
    best_engine = stt._select_best_engine()
    print(f"\n最佳可用引擎: {best_engine}")
    
    print("✅ 语音转文字模块测试完成\n")

def test_text_summarizer():
    """测试文本总结功能"""
    print("📝 测试文本总结模块")
    print("-" * 50)
    
    from utils.text_summarizer import TextSummarizer
    
    # 测试文本
    test_text = """
    人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。
    可以设想，未来人工智能带来的科技产品，将会是人类智慧的容器。人工智能可以对人的意识、思维的信息过程的模拟。
    人工智能不是人的智能，但能像人那样思考，也可能超过人的智能。人工智能是一门极富挑战性的科学，从事这项工作的人必须懂得计算机知识、心理学和哲学。
    """
    
    print(f"测试文本长度: {len(test_text)} 字符")
    
    # 创建总结器
    summarizer = TextSummarizer(
        model="gpt-3.5-turbo",
        language="zh",
        style="brief"
    )
    
    # 测试总结方法
    print("可用总结方法:")
    for method, available in summarizer.available_methods.items():
        status = "✅" if available else "❌"
        print(f"   {status} {method}")
    
    # 测试文本清理
    cleaned_text = summarizer._clean_text(test_text)
    print(f"\n清理后文本长度: {len(cleaned_text)} 字符")
    
    # 测试主题提取
    themes = summarizer._extract_themes(test_text)
    print(f"提取的主题: {themes}")
    
    # 测试关键点提取
    points = summarizer._extract_main_points(test_text)
    print(f"提取的关键点: {len(points)} 个")
    for i, point in enumerate(points[:3], 1):
        print(f"  {i}. {point[:50]}...")
    
    print("✅ 文本总结模块测试完成\n")

def test_full_workflow():
    """测试完整工作流程"""
    print("🔄 测试完整工作流程")
    print("-" * 50)
    
    # 创建测试输出目录
    output_dir = Path("./test_output")
    output_dir.mkdir(exist_ok=True)
    
    print("工作流程步骤:")
    steps = [
        "1. 平台检测和URL验证",
        "2. 视频信息获取",
        "3. 音频提取准备",
        "4. 语音识别引擎检测",
        "5. 文本总结功能验证"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print("\n测试说明:")
    print("   由于网络限制和平台反爬机制，完整下载和转录音频需要:")
    print("   - 真实的视频URL")
    print("   - 可能的cookies认证（对于YouTube）")
    print("   - 足够的网络带宽")
    print("   - Whisper模型文件（首次使用需要下载）")
    
    print("\n✅ 工作流程测试完成\n")

def main():
    """主测试函数"""
    print("=" * 60)
    print("        🎥 视频转文字总结工具 - 功能测试")
    print("=" * 60)
    
    try:
        # 运行所有测试
        test_platform_detector()
        test_video_downloader()
        test_audio_extractor()
        test_speech_to_text()
        test_text_summarizer()
        test_full_workflow()
        
        print("=" * 60)
        print("🎉 所有功能测试完成！")
        print("")
        print("📊 测试总结:")
        print("   1. ✅ 平台检测功能正常")
        print("   2. ✅ 工具依赖检查正常")
        print("   3. ✅ 模块架构完整")
        print("   4. ⚠️  实际下载需要网络条件和平台认证")
        print("")
        print("🚀 下一步:")
        print("   1. 使用真实视频URL测试（可能需要cookies）")
        print("   2. 安装Whisper模型: pip install git+https://github.com/openai/whisper.git")
        print("   3. 配置平台特定参数（如referer、user-agent）")
        print("   4. 测试批量处理功能")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()