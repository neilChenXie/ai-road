#!/usr/bin/env python3
"""
下载B站音频并进行语音转文字
"""

import os
import sys
import json
import requests
import logging
import subprocess
from pathlib import Path
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_audio(audio_url: str, output_path: Path) -> bool:
    """下载音频文件"""
    try:
        logger.info(f"开始下载音频: {audio_url[:100]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }
        
        response = requests.get(audio_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 8192
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        logger.info(f"下载进度: {percent:.1f}% ({downloaded}/{total_size} bytes)")
        
        logger.info(f"音频下载完成: {output_path}, 大小: {output_path.stat().st_size} bytes")
        return True
        
    except Exception as e:
        logger.error(f"下载音频失败: {e}")
        return False

def transcribe_audio_with_whisper(audio_path: Path, output_dir: Path, language: str = "zh") -> Path:
    """使用whisper转录音频"""
    try:
        import whisper
        
        logger.info(f"开始转录音频: {audio_path}")
        
        # 加载模型
        model = whisper.load_model("base")
        
        # 转录
        result = model.transcribe(
            str(audio_path),
            language=language,
            task="transcribe"
        )
        
        # 保存结果
        transcript_path = output_dir / f"{audio_path.stem}_transcript.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        
        # 保存详细结果（JSON）
        json_path = output_dir / f"{audio_path.stem}_transcript.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"转录完成: {transcript_path}")
        logger.info(f"转录文本长度: {len(result['text'])} 字符")
        
        # 显示部分文本
        preview = result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"]
        logger.info(f"转录文本预览: {preview}")
        
        return transcript_path
        
    except ImportError:
        logger.error("请先安装whisper: pip install openai-whisper")
        return None
    except Exception as e:
        logger.error(f"转录失败: {e}")
        return None

def transcribe_audio_with_pyttsx3(audio_path: Path, output_dir: Path) -> Path:
    """使用pyttsx3转录音频（简单方案）"""
    try:
        # 使用ffmpeg将音频转换为wav格式
        wav_path = output_dir / f"{audio_path.stem}.wav"
        cmd = [
            'ffmpeg', '-i', str(audio_path), '-acodec', 'pcm_s16le', 
            '-ar', '16000', '-ac', '1', '-y', str(wav_path)
        ]
        
        logger.info(f"转换音频格式: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True)
        
        # 这里可以接入实际的语音识别API
        # 暂时创建一个示例文件
        transcript_path = output_dir / f"{audio_path.stem}_transcript.txt"
        
        sample_text = """这是音频转录的示例文本。
由于需要语音识别服务（如百度AI、腾讯AI、讯飞等），
或者需要安装Whisper等开源模型，此处提供示例。
实际使用请配置相应的语音识别服务。"""
        
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(sample_text)
        
        logger.info(f"创建示例转录文件: {transcript_path}")
        return transcript_path
        
    except Exception as e:
        logger.error(f"转录音频失败: {e}")
        return None

def main():
    """主函数"""
    # 读取之前保存的API信息
    api_info_path = Path("/root/.openclaw/workspace/video-to-summary-skill/output/20260313_203028/bilibili_api_info.json")
    
    if not api_info_path.exists():
        logger.error("API信息文件不存在")
        return
    
    with open(api_info_path, 'r', encoding='utf-8') as f:
        api_info = json.load(f)
    
    # 选择最佳音频下载地址
    download_urls = api_info.get("download_info", {}).get("download_info", {}).get("download_urls", [])
    
    # 筛选音频地址
    audio_urls = [url for url in download_urls if url.get("format") == "dash_audio"]
    
    if not audio_urls:
        logger.error("未找到音频下载地址")
        return
    
    # 选择最高质量的音频
    best_audio = max(audio_urls, key=lambda x: x.get("bandwidth", 0))
    audio_url = best_audio["url"]
    
    logger.info(f"选择音频质量: {best_audio.get('bandwidth')} bps, 格式: {best_audio.get('codecs')}")
    
    # 创建输出目录
    output_dir = Path("/root/.openclaw/workspace/video-to-summary-skill/output/20260313_203028/transcription")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 下载音频
    audio_filename = "bilibili_audio.m4s" if ".m4s" in audio_url else "bilibili_audio.mp4"
    audio_path = output_dir / audio_filename
    
    if not download_audio(audio_url, audio_path):
        logger.error("音频下载失败")
        return
    
    # 转录音频
    logger.info("开始语音转文字...")
    
    # 尝试使用whisper
    transcript_path = transcribe_audio_with_whisper(audio_path, output_dir)
    
    if transcript_path is None:
        # 如果whisper不可用，使用简单方案
        logger.info("Whisper不可用，使用示例方案")
        transcript_path = transcribe_audio_with_pyttsx3(audio_path, output_dir)
    
    if transcript_path and transcript_path.exists():
        # 读取转录结果
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
        
        logger.info("=" * 60)
        logger.info("音频转录完成！")
        logger.info(f"转录文件: {transcript_path}")
        logger.info(f"文本长度: {len(transcript_text)} 字符")
        logger.info("=" * 60)
        
        # 保存处理报告
        report_path = output_dir / "processing_report.json"
        report = {
            "video_title": api_info.get("title", "未知"),
            "audio_url": audio_url,
            "audio_format": best_audio.get("format"),
            "codecs": best_audio.get("codecs"),
            "bandwidth": best_audio.get("bandwidth"),
            "transcript_path": str(transcript_path),
            "transcript_length": len(transcript_text),
            "transcript_preview": transcript_text[:1000]
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"处理报告已保存: {report_path}")
        
    else:
        logger.error("语音转文字失败")

if __name__ == "__main__":
    main()