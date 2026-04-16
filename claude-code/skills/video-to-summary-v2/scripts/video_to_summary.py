#!/usr/bin/env python3
"""
Video to Summary V2 - Main script

Process video URLs to extract audio, transcribe to text, and generate summaries.
Supports Bilibili and XiaoHongShu platforms.
"""

import argparse
import json
import sys
import shutil
from pathlib import Path
from typing import Dict, Optional
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    PlatformDetector,
    VideoDownloader,
    AudioExtractor,
    SpeechToText,
    TextSummarizer,
    DependencyChecker
)


def setup_logging(level: str = 'INFO') -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(__name__)


class VideoToSummary:
    """Main processing class"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.logger = setup_logging(
            level=self.config.get('logging', {}).get('level', 'INFO')
        )

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration from YAML file"""
        try:
            import yaml
        except ImportError:
            return {}

        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config.yaml'

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)

        return {}

    def process(self, url: str, output_dir: Optional[Path] = None) -> bool:
        """
        Process video URL to generate summary

        Args:
            url: Video URL
            output_dir: Optional output directory

        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"开始处理: {url}")

        # Step 1: Detect platform
        self.logger.info("步骤 1/6: 检测平台")
        detector = PlatformDetector()
        platform, platform_config = detector.detect(url)

        if platform == 'unknown':
            self.logger.error("不支持的平台，目前仅支持B站和小红书")
            return False

        self.logger.info(f"检测到平台: {platform_config.get('name', platform)}")
        video_id = detector.get_video_id(url, platform) or 'unknown'

        # Setup output directory
        output_base = output_dir or Path(self.config.get('output', {}).get('output_dir', './output'))
        work_dir = Path(output_base) / video_id
        work_dir.mkdir(parents=True, exist_ok=True)

        # Step 2: Download video
        self.logger.info("步骤 2/6: 下载视频")
        downloader = VideoDownloader(self.config.get('download', {}))
        download_dir = work_dir / 'download'

        success, video_file = downloader.download(url, download_dir, platform)
        if not success:
            self.logger.error("视频下载失败")
            return False

        self.logger.info(f"视频已下载: {video_file}")

        # Step 3: Extract audio
        self.logger.info("步骤 3/6: 提取音频")
        extractor = AudioExtractor()
        audio_path = work_dir / 'audio.mp3'

        success, _ = extractor.extract(Path(video_file), audio_path)
        if not success:
            self.logger.error("音频提取失败")
            return False

        self.logger.info(f"音频已提取: {audio_path}")

        # Step 4: Transcribe audio
        self.logger.info("步骤 4/6: 语音转录")
        transcriber = SpeechToText(self.config.get('whisper', {}))
        transcript_dir = work_dir / 'transcript'

        model = self.config.get('whisper', {}).get('model', 'base')
        language = self.config.get('whisper', {}).get('language', 'zh')

        success, transcript_data = transcriber.transcribe(
            audio_path, transcript_dir, model=model, language=language
        )

        if not success:
            self.logger.error("语音转录失败")
            return False

        # Save transcript files
        transcriber.save_transcript(transcript_data, transcript_dir)
        self.logger.info(f"转录完成，保存到: {transcript_dir}")

        # Step 5: Generate summary
        self.logger.info("步骤 5/6: 生成总结")
        summarizer = TextSummarizer()

        # Get video info
        video_info = downloader.get_info(url) or {}
        video_info['platform'] = platform
        video_info['video_id'] = video_id

        summary = summarizer.summarize(transcript_data, video_info)

        # Save summary files
        output_formats = self.config.get('output', {}).get('summary_formats', ['md', 'json'])
        summary_files = summarizer.save(summary, work_dir, output_formats)
        self.logger.info(f"总结已生成: {list(summary_files.values())}")

        # Step 6: Cleanup
        cleanup = self.config.get('output', {}).get('cleanup_temp', True)
        if cleanup:
            self.logger.info("步骤 6/6: 清理临时文件")
            if download_dir.exists():
                shutil.rmtree(download_dir)
            if audio_path.exists():
                audio_path.unlink()
            self.logger.info("临时文件已清理")
        else:
            self.logger.info("步骤 6/6: 跳过清理")

        # Print summary path
        if 'md' in summary_files:
            print(f"\n✅ 处理完成!")
            print(f"📄 总结文件: {summary_files['md']}")

        return True

    def detect_only(self, url: str) -> Dict:
        """Detect platform without full processing"""
        detector = PlatformDetector()
        platform, config = detector.detect(url)
        video_id = detector.get_video_id(url, platform)

        return {
            'url': url,
            'platform': platform,
            'platform_name': config.get('name', 'Unknown'),
            'video_id': video_id,
            'supported': platform != 'unknown'
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Video to Summary V2 - 提取视频内容并生成总结 (支持B站和小红书)'
    )

    parser.add_argument(
        'url',
        nargs='?',
        help='视频URL (B站或小红书)'
    )

    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        help='输出目录 (默认: ./output)'
    )

    parser.add_argument(
        '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='base',
        help='Whisper模型大小 (默认: base)'
    )

    parser.add_argument(
        '--language',
        default='zh',
        help='转录语言 (默认: zh)'
    )

    parser.add_argument(
        '--detect-only',
        action='store_true',
        help='仅检测平台，不处理'
    )

    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='检查依赖状态'
    )

    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='保留临时文件'
    )

    parser.add_argument(
        '--config',
        type=Path,
        help='配置文件路径'
    )

    args = parser.parse_args()

    # Check dependencies
    if args.check_deps:
        checker = DependencyChecker()
        results = checker.check_all()
        checker.print_report(results)
        sys.exit(0 if results['all_ok'] else 1)

    # Need URL for other operations
    if not args.url:
        parser.print_help()
        print("\n错误: 需要提供视频URL")
        sys.exit(1)

    # Create processor
    processor = VideoToSummary(args.config)

    # Update config from args
    if args.model:
        processor.config.setdefault('whisper', {})['model'] = args.model
    if args.language:
        processor.config.setdefault('whisper', {})['language'] = args.language
    if args.keep_temp:
        processor.config.setdefault('output', {})['cleanup_temp'] = False

    # Detect only mode
    if args.detect_only:
        result = processor.detect_only(args.url)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    # Process video
    try:
        success = processor.process(args.url, args.output_dir)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
