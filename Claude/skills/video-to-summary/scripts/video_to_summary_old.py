#!/usr/bin/env python3
"""
视频转文字总结工具 - 主程序
支持：下载视频 → 提取音频 → 语音转文字 → 智能总结
"""

import os
import sys
import argparse
import json
import subprocess
import tempfile
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.video_downloader import download_video
from utils.audio_extractor import extract_audio
from utils.speech_to_text import transcribe_audio
from utils.text_summarizer import summarize_text
from utils.platform_detector import detect_platform

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoToSummaryProcessor:
    """视频转文字总结处理器"""
    
    def __init__(self, args):
        self.args = args
        self.output_dir = Path(args.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一的任务ID
        self.task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.work_dir = self.output_dir / self.task_id
        self.work_dir.mkdir(exist_ok=True)
        
        logger.info(f"任务ID: {self.task_id}")
        logger.info(f"工作目录: {self.work_dir}")
        
    def process(self, url):
        """处理单个视频URL"""
        try:
            logger.info(f"开始处理视频: {url}")
            
            # 1. 检测视频平台
            platform = detect_platform(url)
            logger.info(f"检测到平台: {platform}")
            
            # 2. 下载视频（或仅音频）
            video_path = None
            if not self.args.audio_only:
                video_path = download_video(
                    url=url,
                    output_dir=self.work_dir,
                    platform=platform,
                    cookies_browser=self.args.cookies_browser
                )
                if video_path and video_path.exists():
                    logger.info(f"视频下载完成: {video_path}")
                else:
                    logger.warning("视频下载失败或用户选择仅音频模式")
            
            # 3. 提取音频
            audio_path = extract_audio(
                video_path=video_path,
                url=url,
                output_dir=self.work_dir,
                audio_only=self.args.audio_only
            )
            if audio_path and audio_path.exists():
                logger.info(f"音频提取完成: {audio_path}")
            else:
                logger.error("音频提取失败")
                return False
            
            # 4. 语音转文字
            transcript_path = transcribe_audio(
                audio_path=audio_path,
                output_dir=self.work_dir,
                language=self.args.language,
                model=self.args.model
            )
            if transcript_path and transcript_path.exists():
                logger.info(f"语音转文字完成: {transcript_path}")
                
                # 读取转录文本
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    transcript_text = f.read()
                logger.info(f"转录文本长度: {len(transcript_text)} 字符")
            else:
                logger.error("语音转文字失败")
                return False
            
            # 5. 智能总结
            if transcript_text.strip():
                summary_path = summarize_text(
                    text=transcript_text,
                    output_dir=self.work_dir,
                    model=self.args.summary_model,
                    language=self.args.language,
                    style=self.args.summary_style
                )
                if summary_path and summary_path.exists():
                    logger.info(f"智能总结完成: {summary_path}")
                else:
                    logger.warning("智能总结失败，但转录已完成")
            
            # 6. 生成元数据
            self._generate_metadata(url, platform, video_path, audio_path, transcript_path)
            
            # 7. 生成结果报告
            self._generate_report()
            
            logger.info(f"处理完成！结果保存在: {self.work_dir}")
            return True
            
        except Exception as e:
            logger.error(f"处理过程中发生错误: {e}", exc_info=True)
            return False
    
    def _generate_metadata(self, url, platform, video_path, audio_path, transcript_path):
        """生成处理元数据"""
        metadata = {
            "task_id": self.task_id,
            "url": url,
            "platform": platform,
            "timestamp": datetime.now().isoformat(),
            "audio_only": self.args.audio_only,
            "language": self.args.language,
            "model": self.args.model,
            "files": {
                "video": str(video_path) if video_path else None,
                "audio": str(audio_path) if audio_path else None,
                "transcript": str(transcript_path) if transcript_path else None,
            }
        }
        
        metadata_path = self.work_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"元数据已保存: {metadata_path}")
        return metadata_path
    
    def _generate_report(self):
        """生成处理报告"""
        report_path = self.work_dir / "处理报告.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 视频处理报告\n\n")
            f.write(f"## 任务信息\n")
            f.write(f"- 任务ID: {self.task_id}\n")
            f.write(f"- 处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- 工作目录: {self.work_dir}\n\n")
            
            # 列出生成的文件
            files = list(self.work_dir.glob("*"))
            if files:
                f.write(f"## 生成文件\n")
                for file_path in sorted(files):
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        size_mb = size / (1024 * 1024)
                        f.write(f"- {file_path.name} ({size_mb:.2f} MB)\n")
        
        logger.info(f"处理报告已生成: {report_path}")
        return report_path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='视频转文字总结工具 - 下载视频、提取音频、语音转文字、智能总结'
    )
    
    # 必需参数
    parser.add_argument('--url', required=True, help='视频URL')
    
    # 输出配置
    parser.add_argument('--output-dir', default='./output', help='输出目录')
    
    # 处理选项
    parser.add_argument('--audio-only', action='store_true', 
                       help='仅处理音频（不下载视频）')
    parser.add_argument('--cookies-browser', default='chrome',
                       choices=['chrome', 'firefox', 'safari', 'edge', 'brave'],
                       help='浏览器cookies来源（用于YouTube等平台）')
    
    # 识别配置
    parser.add_argument('--language', default='auto', 
                       help='语音识别语言 (zh, en, ja, ko, auto等)')
    parser.add_argument('--model', default='base',
                       choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v3'],
                       help='Whisper模型大小')
    
    # 总结配置
    parser.add_argument('--summary-model', default='gpt-3.5-turbo',
                       help='总结使用的模型')
    parser.add_argument('--summary-style', default='brief',
                       choices=['brief', 'detailed', 'academic', 'bullet'],
                       help='总结风格')
    
    # 调试选项
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    
    # 创建处理器并执行
    processor = VideoToSummaryProcessor(args)
    success = processor.process(args.url)
    
    if success:
        print(f"\n✅ 处理成功！")
        print(f"   结果目录: {processor.work_dir}")
        print(f"   查看报告: {processor.work_dir / '处理报告.md'}")
        sys.exit(0)
    else:
        print(f"\n❌ 处理失败，请检查日志")
        sys.exit(1)

if __name__ == '__main__':
    main()