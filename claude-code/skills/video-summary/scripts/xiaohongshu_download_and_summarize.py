#!/usr/bin/env python3
"""
小红书视频下载和总结脚本

使用方法：
    python xiaohongshu_download_and_summarize.py "视频URL"
    python xiaohongshu_download_and_summarize.py "视频URL" --model base --language zh
"""

import sys
import os
import subprocess
import json
import argparse
import tempfile
import shutil
from datetime import datetime
from pathlib import Path


class XiaohongshuSummarizer:
    """小红书视频下载和总结工具"""
    
    def __init__(self, video_url, model="base", language="zh", keep_files=False, output_dir=None):
        """
        初始化
        
        Args:
            video_url: 小红书视频URL
            model: Whisper模型大小 (tiny, base, small, medium, large)
            language: 语言代码 (默认: zh)
            keep_files: 是否保留所有文件 (默认: False)
            output_dir: 输出目录 (默认: 当前目录)
        """
        self.video_url = video_url
        self.model = model
        self.language = language
        self.keep_files = keep_files
        self.output_dir = Path(output_dir) if output_dir else Path("./temp")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建临时工作目录
        self.work_dir = tempfile.mkdtemp(prefix="xiaohongshu_")
        self.work_path = Path(self.work_dir)
        
        self.video_file = None
        self.audio_file = None
        self.transcript_file = None
        self.summary_file = None
        
        print(f"[初始化] 工作目录: {self.work_dir}")
    
    def download_video(self):
        """使用yt-dlp下载视频"""
        print("\n[步骤1] 下载视频...")
        
        try:
            output_template = str(self.work_path / "video.%(ext)s")
            
            cmd = [
                "yt-dlp",
                "--referer", "https://www.xiaohongshu.com",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "-f", "best",
                "-o", output_template,
                self.video_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise RuntimeError(f"下载失败: {result.stderr}")
            
            # 找到下载的视频文件
            video_files = list(self.work_path.glob("video.*"))
            if not video_files:
                raise RuntimeError("未找到下载的视频文件")
            
            self.video_file = video_files[0]
            print(f"✓ 视频下载成功: {self.video_file.name}")
            return True
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("下载超时（超过5分钟）")
        except Exception as e:
            raise RuntimeError(f"下载失败: {str(e)}")
    
    def extract_audio(self):
        """使用FFmpeg提取音频"""
        print("\n[步骤2] 提取音频...")
        
        try:
            self.audio_file = self.work_path / "audio.mp3"
            
            cmd = [
                "ffmpeg",
                "-i", str(self.video_file),
                "-q:a", "0",
                "-map", "a",
                "-y",  # 覆盖现有文件
                str(self.audio_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise RuntimeError(f"音频提取失败: {result.stderr}")
            
            if not self.audio_file.exists():
                raise RuntimeError("未找到提取的音频文件")
            
            print(f"✓ 音频提取成功: {self.audio_file.name}")
            return True
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("音频提取超时")
        except FileNotFoundError:
            raise RuntimeError("FFmpeg未安装。请运行: brew install ffmpeg")
        except Exception as e:
            raise RuntimeError(f"音频提取失败: {str(e)}")
    
    def transcribe_audio(self):
        """使用Whisper进行语音转文字"""
        print("\n[步骤3] 转录音频为文字...")
        
        try:
            cmd = [
                "whisper",
                str(self.audio_file),
                "--model", self.model,
                "--language", self.language,
                "--output_format", "txt",
                "--output_dir", str(self.work_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                raise RuntimeError(f"转录失败: {result.stderr}")
            
            # 找到转录文件
            transcript_files = list(self.work_path.glob("audio.txt"))
            if not transcript_files:
                raise RuntimeError("未找到转录结果文件")
            
            self.transcript_file = transcript_files[0]
            
            with open(self.transcript_file, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
            
            print(f"✓ 转录完成，字数: {len(transcript_text)}")
            return transcript_text
            
        except FileNotFoundError:
            raise RuntimeError("Whisper未安装。请运行: pip install openai-whisper")
        except subprocess.TimeoutExpired:
            raise RuntimeError("转录超时（超过10分钟）")
        except Exception as e:
            raise RuntimeError(f"转录失败: {str(e)}")
    
    def summarize_content(self, transcript_text):
        """总结转录内容"""
        print("\n[步骤4] 生成内容总结...")
        
        try:
            # 简单的总结逻辑：提取重要句子
            sentences = [s.strip() for s in transcript_text.split('。') if s.strip()]
            
            if not sentences:
                return transcript_text
            
            # 计算摘要长度（原文本的20-30%）
            summary_length = max(1, len(sentences) // 4)
            
            # 选择关键句子
            # 这是一个简单的实现，可以被更复杂的算法替代
            summary_sentences = sentences[:summary_length]
            summary = '。'.join(summary_sentences) + '。'
            
            print(f"✓ 总结完成，原文{len(transcript_text)}字，总结{len(summary)}字")
            return summary
            
        except Exception as e:
            print(f"⚠ 总结过程出错，返回原文本: {str(e)}")
            return transcript_text
    
    def save_results(self, transcript_text, summary_text):
        """保存结果文件"""
        print("\n[步骤5] 保存结果...")
        
        try:
            # 保存完整转录
            transcript_output = self.output_dir / f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(transcript_output, 'w', encoding='utf-8') as f:
                f.write(f"视频URL: {self.video_url}\n")
                f.write(f"处理时间: {datetime.now().isoformat()}\n")
                f.write("="*50 + "\n\n")
                f.write(transcript_text)
            
            # 保存总结
            summary_output = self.output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(summary_output, 'w', encoding='utf-8') as f:
                f.write(f"视频URL: {self.video_url}\n")
                f.write(f"处理时间: {datetime.now().isoformat()}\n")
                f.write("="*50 + "\n\n")
                f.write(summary_text)
            
            print(f"✓ 转录保存至: {transcript_output}")
            print(f"✓ 总结保存至: {summary_output}")
            
            return str(transcript_output), str(summary_output)
            
        except Exception as e:
            raise RuntimeError(f"保存结果失败: {str(e)}")
    
    def cleanup(self):
        """清理临时文件"""
        if not self.keep_files and os.path.exists(self.work_dir):
            try:
                shutil.rmtree(self.work_dir)
                print(f"\n✓ 已删除临时文件")
            except Exception as e:
                print(f"\n⚠ 删除临时文件失败: {str(e)}")
    
    def run(self):
        """运行完整流程"""
        try:
            # 下载视频
            self.download_video()
            
            # 提取音频
            self.extract_audio()
            
            # 转录
            transcript_text = self.transcribe_audio()
            
            # 总结
            summary_text = self.summarize_content(transcript_text)
            
            # 保存结果
            transcript_file, summary_file = self.save_results(transcript_text, summary_text)
            
            # 清理临时文件
            self.cleanup()
            
            # 输出最终结果
            print("\n" + "="*50)
            print("===== 小红书视频内容总结 =====")
            print("="*50)
            print(f"URL: {self.video_url}")
            print(f"处理时间: {datetime.now().isoformat()}")
            print("\n【完整转录】")
            print(transcript_text)
            print("\n【核心要点总结】")
            print(summary_text)
            print("\n" + "="*50)
            print("【处理完成】")
            print(f"转录文件: {transcript_file}")
            print(f"总结文件: {summary_file}")
            print("="*50)
            
            return True
            
        except Exception as e:
            print(f"\n✗ 处理失败: {str(e)}", file=sys.stderr)
            self.cleanup()
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="下载小红书视频并生成转录和总结",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python xiaohongshu_download_and_summarize.py "https://www.xiaohongshu.com/explore/xxx"
  python xiaohongshu_download_and_summarize.py "https://..." --model base --language zh
  python xiaohongshu_download_and_summarize.py "https://..." --keep-files --output-dir ./results
        """
    )
    
    parser.add_argument("url", help="小红书视频URL")
    parser.add_argument("--model", default="base", 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper模型大小 (默认: base)")
    parser.add_argument("--language", default="zh",
                       help="语言代码 (默认: zh)")
    parser.add_argument("--keep-files", action="store_true",
                       help="完成后保留所有文件")
    parser.add_argument("--output-dir", default=None,
                       help="输出目录 (默认: 当前目录)")
    
    args = parser.parse_args()
    
    # 创建总结器实例
    summarizer = XiaohongshuSummarizer(
        args.url,
        model=args.model,
        language=args.language,
        keep_files=args.keep_files,
        output_dir=args.output_dir
    )
    
    # 运行
    success = summarizer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
