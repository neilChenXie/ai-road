"""
Video downloader with platform-specific handling
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

from .platform_detector import PlatformDetector
from .logger import setup_logger


class VideoDownloader:
    """Download videos from various platforms"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.detector = PlatformDetector()
        self.logger = setup_logger()

    def _get_cookies_args(self, url: str) -> list:
        """Get cookie-related arguments for yt-dlp"""
        args = []

        # Check if cookies are needed
        if not self.config.get('use_cookies', True):
            return args

        # Get platform-specific cookie preferences
        platform, platform_config = self.detector.detect(url)
        if not platform_config.get('supports_cookies', False):
            return args

        # Try browser cookies
        browser = self.config.get('cookies_browser',
                                  platform_config.get('preferred_cookies', 'chrome'))

        args.extend(['--cookies-from-browser', browser])

        return args

    def _get_format_args(self, url: str, audio_only: bool) -> list:
        """Get format-related arguments"""
        if audio_only:
            return ['-f', 'bestaudio']
        return ['-f', 'best']

    def _get_info(self, url: str) -> Optional[Dict]:
        """
        Get video information without downloading

        Args:
            url: Video URL

        Returns:
            Video metadata dict or None
        """
        try:
            args = [
                'yt-dlp',
                '--dump-json',
                '--no-playlist',
                '--no-warnings',
            ]
            args.extend(self._get_cookies_args(url))
            args.append(url)

            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'description': info.get('description', ''),
                }

            return None

        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout getting video info")
            return None
        except Exception as e:
            self.logger.error(f"Error getting video info: {e}")
            return None

    def download(self, url: str, output_path: Path, audio_only: bool = False) -> Tuple[bool, str]:
        """
        Download video or audio

        Args:
            url: Video URL
            output_path: Output directory
            audio_only: Only download audio

        Returns:
            Tuple of (success, output_file_path)
        """
        try:
            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)

            # Get video info first
            info = self._get_info(url)
            if info:
                self.logger.info(f"Video: {info['title']}")
                self.logger.info(f"Duration: {info['duration']}s")
            else:
                self.logger.warning("Could not fetch video info")

            # Build command
            args = [
                'yt-dlp',
                '--no-playlist',
                '--no-warnings',
                '--progress',
                '--newline',
            ]

            # Add cookie args
            args.extend(self._get_cookies_args(url))

            # Add format args
            args.extend(self._get_format_args(url, audio_only))

            # Output template
            if audio_only:
                output_template = str(output_path / "audio.%(ext)s")
            else:
                output_template = str(output_path / "video.%(ext)s")

            args.extend(['-o', output_template])

            # Timeout
            timeout = self.config.get('timeout', 300)
            args.extend(['--socket-timeout', str(timeout)])

            # Add URL
            args.append(url)

            self.logger.info(f"Downloading from {url}...")

            # Run download
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout + 60  # Extra buffer
            )

            if result.returncode != 0:
                self.logger.error(f"Download failed: {result.stderr}")
                return False, ""

            # Find downloaded file
            if audio_only:
                downloaded = list(output_path.glob("audio.*"))
            else:
                downloaded = list(output_path.glob("video.*"))

            if downloaded:
                output_file = downloaded[0]
                self.logger.success(f"Downloaded: {output_file.name}")
                return True, str(output_file)
            else:
                self.logger.error("Could not find downloaded file")
                return False, ""

        except subprocess.TimeoutExpired:
            self.logger.error("Download timeout")
            return False, ""
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            return False, ""

    def download_with_retry(self, url: str, output_path: Path,
                           audio_only: bool = False,
                           max_retries: int = 2) -> Tuple[bool, str]:
        """
        Download with retry logic

        Args:
            url: Video URL
            output_path: Output directory
            audio_only: Only download audio
            max_retries: Maximum retry attempts

        Returns:
            Tuple of (success, output_file_path)
        """
        for attempt in range(max_retries + 1):
            if attempt > 0:
                self.logger.info(f"Retry {attempt}/{max_retries}...")

            success, output_path = self.download(url, output_path, audio_only)

            if success:
                return True, output_path

        self.logger.error(f"Failed after {max_retries} retries")
        return False, ""


if __name__ == '__main__':
    # Test download
    downloader = VideoDownloader({'use_cookies': True})

    # Get info
    info = downloader._get_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    if info:
        print(f"Title: {info['title']}")
        print(f"Duration: {info['duration']}s")
