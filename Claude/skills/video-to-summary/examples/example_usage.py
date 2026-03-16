#!/usr/bin/env python3
"""
视频转文字总结工具 - 使用示例
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.platform_detector import detect_platform, get_platform_info
from utils.video_downloader import download_video, get_video_info
from utils.audio_extractor import extract_audio
from utils.speech_to_text import transcribe_audio
from utils.text_summarizer import summarize_text

def example_basic_usage():
    """基本使用示例"""
    print("🎥 视频转文字总结工具 - 使用示例")
    print("=" * 50)
    
    # 示例URL（请替换为真实URL进行测试）
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # YouTube示例
        "https://www.bilibili.com/video/BV1GJ411x7h7",  # Bilibili示例
        "https://vimeo.com/123456789",                  # Vimeo示例
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📋 示例 {i}: {url}")
        print("-" * 30)
        
        # 1. 检测平台
        platform = detect_platform(url)
        platform_info = get_platform_info(url)
        print(f"✅ 平台检测: {platform_info['name']}")
        
        # 2. 获取视频信息
        video_info = get_video_info(url)
        if video_info:
            title = video_info.get('title', '未知标题')
            duration = video_info.get('duration', 0)
            print(f"✅ 视频信息: {title} ({duration}秒)")
        else:
            print("⚠️  无法获取视频信息")
        
        print("")

def example_workflow():
    """完整工作流程示例"""
    print("\n🔄 完整工作流程示例")
    print("=" * 50)
    
    # 假设的URL和输出目录
    test_url = "https://www.youtube.com/watch?v=example"
    output_dir = Path("./example_output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"📥 输入URL: {test_url}")
    print(f"📁 输出目录: {output_dir}")
    
    # 工作流程步骤
    steps = [
        ("1️⃣ 下载视频", "download_video()"),
        ("2️⃣ 提取音频", "extract_audio()"),
        ("3️⃣ 语音转文字", "transcribe_audio()"),
        ("4️⃣ 智能总结", "summarize_text()"),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}: {step_func}")
        # 在实际使用中，这里会调用相应的函数
        print(f"  执行中... (示例中跳过)")
    
    print("\n🎉 工作流程完成！")
    print(f"   输出文件保存在: {output_dir}")

def example_batch_processing():
    """批量处理示例"""
    print("\n📦 批量处理示例")
    print("=" * 50)
    
    # 创建示例URL列表文件
    urls_content = """# 视频URL列表示例
https://www.youtube.com/watch?v=video1
https://www.bilibili.com/video/BVxxxx1
https://www.xiaohongshu.com/discovery/item/xxx1

https://www.youtube.com/watch?v=video2
# 这是一个注释行，会被忽略
https://www.bilibili.com/video/BVxxxx2
"""
    
    urls_file = Path("./example_urls.txt")
    urls_file.write_text(urls_content, encoding='utf-8')
    
    print(f"📄 创建示例URL文件: {urls_file}")
    print("文件内容:")
    print(urls_content)
    
    print("\n📋 批量处理命令:")
    print(f"  bash scripts/batch_process.sh -i {urls_file} -p 2 -l zh")
    
    print("\n📊 预期输出结构:")
    print("""
  output/
  └── batch_YYYYMMDD_HHMMSS/
      ├── 001_video1/
      │   ├── audio.mp3
      │   ├── transcript.txt
      │   ├── summary.md
      │   └── metadata.json
      ├── 002_BVxxxx1/
      │   └── ...
      ├── logs/
      │   ├── 001.log
      │   └── 002.log
      └── 批量处理报告.md
    """)

def example_configuration():
    """配置示例"""
    print("\n⚙️ 配置示例")
    print("=" * 50)
    
    config_example = """# config/settings.yaml 示例

# 下载配置
download:
  output_dir: "./output"
  cookies_browser: "chrome"  # chrome, firefox, safari, edge, brave
  max_quality: "best"        # best, 1080p, 720p, 480p, audio
  timeout: 300               # 下载超时（秒）
  retries: 3                 # 重试次数

# 语音识别配置
speech_to_text:
  default_model: "base"      # tiny, base, small, medium, large
  default_language: "auto"   # auto, zh, en, ja, ko, etc.
  fallback_engines:          # 备用引擎顺序
    - "whisper"
    - "google"
    - "azure"
  
  # Whisper特定配置
  whisper:
    device: "cpu"           # cpu, cuda
    compute_type: "float32" # float32, float16, int8

# 总结配置
summarization:
  default_style: "brief"    # brief, detailed, academic, bullet
  max_length: 1000          # 总结最大长度
  extract_key_points: true  # 是否提取关键点
  
  # AI模型配置（可选）
  ai_models:
    openai:
      model: "gpt-3.5-turbo"
      temperature: 0.7
    claude:
      model: "claude-3-haiku-20240307"
      temperature: 0.3

# 平台特定配置
platforms:
  youtube:
    needs_cookies: true
    recommended_quality: "best"
    max_duration: 7200      # 最大时长（秒），0表示无限制
    
  bilibili:
    needs_referer: true
    user_agent: "Mozilla/5.0"
    
  xiaohongshu:
    needs_user_agent: true
    timeout: 180

# 音频处理配置
audio:
  default_format: "mp3"
  quality: 192              # kbps（仅对mp3有效）
  sample_rate: 44100        # 采样率
  channels: 2               # 声道数（1=单声道，2=立体声）
  
  # 音频增强
  enhancement:
    noise_reduction: true
    normalize: true
    remove_silence: false
"""
    
    print("配置文件示例 (config/settings.yaml):")
    print(config_example)
    
    print("\n🎯 环境变量配置:")
    print("""  # OpenAI API（用于高级总结）
  export OPENAI_API_KEY="sk-..."
  
  # Azure语音服务
  export AZURE_SPEECH_KEY="your-key"
  export AZURE_SPEECH_REGION="eastus"
  
  # Claude API
  export ANTHROPIC_API_KEY="your-key"
  
  # 代理设置（如需）
  export HTTP_PROXY="http://proxy:port"
  export HTTPS_PROXY="http://proxy:port"
  """)

def example_integration():
    """集成示例"""
    print("\n🔗 集成到其他项目示例")
    print("=" * 50)
    
    integration_code = """# 集成到Python项目示例

import sys
from pathlib import Path

# 添加视频转文字工具路径
sys.path.append("/path/to/video-to-summary-skill")

from utils.video_downloader import download_video
from utils.audio_extractor import extract_audio
from utils.speech_to_text import transcribe_audio
from utils.text_summarizer import summarize_text

def analyze_video_content(url: str, output_dir: Path):
    \"\"\"分析视频内容\"\"\"
    try:
        # 1. 下载视频
        print(f"下载视频: {url}")
        video_path = download_video(
            url=url,
            output_dir=output_dir,
            platform="youtube",  # 或自动检测
            cookies_browser="chrome"
        )
        
        if not video_path:
            print("视频下载失败")
            return None
        
        # 2. 提取音频
        print("提取音频...")
        audio_path = extract_audio(
            video_path=video_path,
            url=url,
            output_dir=output_dir,
            audio_format="mp3",
            audio_quality=192
        )
        
        if not audio_path:
            print("音频提取失败")
            return None
        
        # 3. 语音转文字
        print("语音转文字...")
        transcript_path = transcribe_audio(
            audio_path=audio_path,
            output_dir=output_dir,
            language="zh",
            model="base"
        )
        
        if not transcript_path:
            print("语音转文字失败")
            return None
        
        # 读取转录文本
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        print(f"转录完成: {len(transcript)} 字符")
        
        # 4. 智能总结
        print("生成总结...")
        summary_path = summarize_text(
            text=transcript,
            output_dir=output_dir,
            model="gpt-3.5-turbo",
            language="zh",
            style="brief"
        )
        
        if summary_path:
            print(f"总结已保存: {summary_path}")
        
        return {
            "video": video_path,
            "audio": audio_path,
            "transcript": transcript_path,
            "summary": summary_path
        }
        
    except Exception as e:
        print(f"分析失败: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    result = analyze_video_content(
        "https://www.youtube.com/watch?v=example",
        Path("./analysis_results")
    )
    
    if result:
        print("✅ 分析成功！")
        for key, value in result.items():
            if value:
                print(f"  {key}: {value}")
"""
    
    print("Python集成代码示例:")
    print(integration_code)

def main():
    """主函数"""
    print("=" * 60)
    print("        🎥 视频转文字总结工具 - 完整示例")
    print("=" * 60)
    
    examples = [
        ("基本使用", example_basic_usage),
        ("完整工作流程", example_workflow),
        ("批量处理", example_batch_processing),
        ("配置示例", example_configuration),
        ("集成示例", example_integration),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{'='*20} 示例 {i}: {name} {'='*20}")
        func()
    
    print("\n" + "=" * 60)
    print("🎉 所有示例展示完成！")
    print("")
    print("📚 下一步:")
    print("  1. 运行安装脚本: ./install.sh")
    print("  2. 尝试真实URL: python scripts/video_to_summary.py --url '你的视频URL'")
    print("  3. 查看文档: cat README.md")
    print("  4. 配置高级功能: 编辑 config/settings.yaml")
    print("")
    print("💡 提示: 在实际使用前，请确保已安装所有依赖")
    print("=" * 60)

if __name__ == "__main__":
    main()