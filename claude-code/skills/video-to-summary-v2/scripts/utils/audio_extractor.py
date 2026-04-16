"""
Audio Extractor - Extract audio from video files using FFmpeg
"""

import subprocess
from pathlib import Path
from typing import Tuple, Optional
import logging


class AudioExtractor:
    """Extract audio from video files"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract(self, video_path: Path, audio_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Extract audio from video file

        Args:
            video_path: Path to video file
            audio_path: Path for output audio file

        Returns:
            Tuple of (success, audio_path)
        """
        if not video_path.exists():
            self.logger.error(f"视频文件不存在: {video_path}")
            return False, None

        # Ensure output directory exists
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # FFmpeg command to extract audio
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # No video
            '-acodec', 'libmp3lame',  # MP3 codec
            '-q:a', '2',  # Quality
            '-y',  # Overwrite
            str(audio_path)
        ]

        self.logger.info(f"提取音频: {video_path} -> {audio_path}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                self.logger.error(f"音频提取失败: {result.stderr}")
                return False, None

            if audio_path.exists():
                return True, str(audio_path)

            return False, None

        except subprocess.TimeoutExpired:
            self.logger.error("音频提取超时")
            return False, None
        except Exception as e:
            self.logger.error(f"音频提取异常: {e}")
            return False, None

    def get_duration(self, audio_path: Path) -> Optional[float]:
        """
        Get audio duration in seconds

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds or None
        """
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-show_entries',
                 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                 str(audio_path)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return float(result.stdout.strip())

            return None

        except Exception:
            return None
