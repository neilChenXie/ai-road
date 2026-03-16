#!/usr/bin/env python3
"""
Video to Summary - Main script

Process video URLs to extract audio, transcribe to text, and generate summaries.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    PlatformDetector,
    VideoDownloader,
    AudioExtractor,
    SpeechToText,
    TextSummarizer,
    DependencyChecker,
    setup_logger,
    ProgressHandler
)


class VideoToSummary:
    """Main processing class"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.logger = setup_logger(
            level=self.config.get('logging', {}).get('level', 'INFO')
        )
        self.progress = ProgressHandler(self.logger)

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration from YAML file"""
        import yaml

        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config.yaml'

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)

        return {}

    def _update_config(self, args: argparse.Namespace):
        """Update config with command line arguments"""
        if args.model:
            self.config.setdefault('whisper', {})['model'] = args.model
        if args.language:
            self.config.setdefault('whisper', {})['language'] = args.language
        if args.audio_only:
            self.config.setdefault('download', {})['audio_only'] = True
        if args.output_dir:
            self.config.setdefault('output', {})['output_dir'] = args.output_dir
        if args.keep_temp:
            self.config.setdefault('output', {})['cleanup_temp'] = False
        if args.no_summary:
            self.config.setdefault('output', {})['include_summary'] = False

    def process(self, url: str) -> bool:
        """
        Process video URL to generate summary

        Args:
            url: Video URL

        Returns:
            True if successful, False otherwise
        """
        self.progress.set_total(6)

        # Step 1: Detect platform
        self.progress.next_step("检测视频平台")
        detector = PlatformDetector()
        platform, platform_config = detector.detect(url)
        self.logger.info(f"平台: {platform_config.get('name', 'Unknown')}")
        video_id = detector.get_video_id(url, platform)

        # Create output directory
        output_base = Path(self.config.get('output', {}).get('output_dir', './output'))
        output_dir = output_base / video_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Step 2: Download video/audio
        self.progress.next_step("下载视频")
        downloader = VideoDownloader(self.config.get('download', {}))
        audio_only = self.config.get('download', {}).get('audio_only', False)

        if audio_only:
            # Try audio-only download first
            success, downloaded_file = downloader.download(
                url, output_dir / 'download', audio_only=True
            )
            if success:
                audio_path = Path(downloaded_file)
            else:
                # Fallback to video download then extract
                self.logger.warning("音频下载失败，尝试下载视频后提取")
                success, downloaded_file = downloader.download(
                    url, output_dir / 'download', audio_only=False
                )
                if not success:
                    self.logger.error("视频下载失败")
                    return False

                # Step 3: Extract audio
                self.progress.next_step("提取音频")
                extractor = AudioExtractor()
                audio_path = output_dir / 'audio.mp3'
                success, _ = extractor.extract(
                    Path(downloaded_file), audio_path
                )
                if not success:
                    self.logger.error("音频提取失败")
                    return False
        else:
            success, downloaded_file = downloader.download(
                url, output_dir / 'download', audio_only=False
            )
            if not success:
                self.logger.error("视频下载失败")
                return False

            # Extract audio
            self.progress.next_step("提取音频")
            extractor = AudioExtractor()
            audio_path = output_dir / 'audio.mp3'
            success, _ = extractor.extract(
                Path(downloaded_file), audio_path
            )
            if not success:
                self.logger.error("音频提取失败")
                return False

        # Step 4: Transcribe audio
        self.progress.next_step("语音识别")
        transcriber = SpeechToText(self.config.get('whisper', {}))
        model = self.config.get('whisper', {}).get('model', 'base')
        language = self.config.get('whisper', {}).get('language', 'zh')

        success, transcript_data = transcriber.transcribe(
            audio_path,
            output_dir / 'transcript',
            model=model,
            language=language
        )

        if not success:
            self.logger.error("语音识别失败")
            return False

        # Save transcript files
        transcript_files = transcriber.save_transcript(
            transcript_data,
            output_dir / 'transcript'
        )
        self.logger.info(f"转录文件已保存: {len(transcript_files)} 个")

        # Step 5: Generate summary
        if self.config.get('output', {}).get('include_summary', True):
            self.progress.next_step("生成总结")
            summarizer = TextSummarizer()

            # Get video metadata
            video_info = downloader._get_info(url) or {}
            video_info['platform'] = platform
            video_info['video_id'] = video_id

            summary = summarizer.summarize(transcript_data, video_info)

            # Save summary files
            output_formats = self.config.get('output', {}).get('format', ['md', 'json'])
            summary_files = summarizer.save(summary, output_dir, output_formats)
            self.logger.info(f"总结文件已保存: {len(summary_files)} 个")

        # Step 6: Cleanup
        if self.config.get('output', {}).get('cleanup_temp', True):
            self.progress.next_step("清理临时文件")
            temp_dir = output_dir / 'download'
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)

        # Final report
        self.progress.success("处理完成!")
        self.logger.info(f"输出目录: {output_dir}")

        # Save final report
        self._save_report(output_dir, {
            'url': url,
            'video_id': video_id,
            'platform': platform,
            'success': True,
            'output_files': [str(f.relative_to(output_dir)) for f in output_dir.glob('*') if f.is_file()]
        })

        return True

    def _save_report(self, output_dir: Path, report: Dict):
        """Save processing report"""
        report_path = output_dir / 'report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Video to Summary - Extract and summarize video content'
    )

    parser.add_argument(
        'url',
        nargs='?',
        help='Video URL to process (not required with --check-deps)'
    )

    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory (default: ./output)'
    )

    parser.add_argument(
        '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model size (default: base)'
    )

    parser.add_argument(
        '--language',
        default='auto',
        help='Transcription language (default: auto-detect)'
    )

    parser.add_argument(
        '--audio-only',
        action='store_true',
        help='Download audio only (faster)'
    )

    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='Keep temporary files'
    )

    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Skip summary generation'
    )

    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check dependencies and exit'
    )

    parser.add_argument(
        '--config',
        type=Path,
        help='Path to config.yaml'
    )

    args = parser.parse_args()

    # Check dependencies
    if args.check_deps:
        checker = DependencyChecker()
        results = checker.check_all()
        checker.print_report(results)
        sys.exit(0 if results['all_ok'] else 1)

    # Process video
    processor = VideoToSummary(args.config)
    processor._update_config(args)

    try:
        success = processor.process(args.url)
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
