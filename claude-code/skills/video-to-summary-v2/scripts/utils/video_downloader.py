"""
Video Downloader - Download videos with platform-specific strategies
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Tuple, Optional, Dict
import logging


class VideoDownloader:
    """Download videos from different platforms"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.timeout = self.config.get('timeout', 300)

    def download(self, url: str, output_dir: Path, platform: str) -> Tuple[bool, Optional[str]]:
        """
        Download video from URL

        Args:
            url: Video URL
            output_dir: Output directory
            platform: Detected platform

        Returns:
            Tuple of (success, file_path)
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build yt-dlp command based on platform
        cmd = self._build_command(url, output_dir, platform)

        self.logger.info(f"下载视频: {url}")
        self.logger.debug(f"命令: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode != 0:
                self.logger.error(f"下载失败: {result.stderr}")
                return False, None

            # Find downloaded file
            downloaded_files = list(output_dir.glob('video.*'))
            if downloaded_files:
                return True, str(downloaded_files[0])

            return False, None

        except subprocess.TimeoutExpired:
            self.logger.error(f"下载超时 ({self.timeout}s)")
            return False, None
        except Exception as e:
            self.logger.error(f"下载异常: {e}")
            return False, None

    def _build_command(self, url: str, output_dir: Path, platform: str) -> list:
        """Build yt-dlp command with platform-specific options"""

        output_template = str(output_dir / 'video.%(ext)s')

        base_cmd = [
            'yt-dlp',
            '--no-playlist',
            '--no-warnings',
            '-o', output_template
        ]

        # Platform-specific options
        if platform == 'bilibili':
            cmd = base_cmd.copy()
            # B站可能需要cookies
            if self.config.get('use_cookies'):
                browser = self.config.get('cookies_browser', 'chrome')
                cmd.extend(['--cookies-from-browser', browser])

        elif platform == 'xiaohongshu':
            # 小红书需要特殊的headers
            cmd = base_cmd.copy()
            cmd.extend([
                '--referer', 'https://www.xiaohongshu.com',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ])

        else:
            cmd = base_cmd.copy()

        cmd.append(url)
        return cmd

    def get_info(self, url: str) -> Optional[Dict]:
        """
        Get video information without downloading

        Args:
            url: Video URL

        Returns:
            Video info dict or None
        """
        try:
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-playlist', url],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return json.loads(result.stdout)

            return None

        except Exception as e:
            self.logger.error(f"获取视频信息失败: {e}")
            return None
