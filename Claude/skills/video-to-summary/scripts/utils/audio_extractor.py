"""
Audio extraction from video files
"""

import subprocess
from pathlib import Path
from typing import Tuple

from .logger import setup_logger


class AudioExtractor:
    """Extract audio from video files"""

    def __init__(self):
        self.logger = setup_logger()

    def extract(self, video_path: Path, output_path: Path,
                codec: str = 'mp3', bitrate: str = '128k') -> Tuple[bool, str]:
        """
        Extract audio from video

        Args:
            video_path: Path to video file
            output_path: Path for output audio file
            codec: Audio codec (mp3, wav, m4a, etc.)
            bitrate: Audio bitrate (e.g., 128k, 192k, 320k)

        Returns:
            Tuple of (success, output_file_path)
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build FFmpeg command
            args = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # No video
                '-acodec', self._get_codec(codec),
                '-ab', bitrate,
                '-y',  # Overwrite output
                str(output_path)
            ]

            self.logger.info(f"Extracting audio from {video_path.name}...")

            # Run FFmpeg
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                self.logger.error(f"Extraction failed: {result.stderr}")
                return False, ""

            # Check if output file exists
            if output_path.exists():
                self.logger.success(f"Extracted: {output_path.name}")
                return True, str(output_path)
            else:
                self.logger.error("Output file not created")
                return False, ""

        except Exception as e:
            self.logger.error(f"Extraction error: {e}")
            return False, ""

    def _get_codec(self, format_name: str) -> str:
        """Get FFmpeg codec for format"""
        codecs = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'm4a': 'aac',
            'aac': 'aac',
            'flac': 'flac',
            'ogg': 'libvorbis',
        }
        return codecs.get(format_name.lower(), 'libmp3lame')

    def convert(self, input_path: Path, output_path: Path,
                codec: str = 'mp3', bitrate: str = '128k') -> Tuple[bool, str]:
        """
        Convert audio to different format

        Args:
            input_path: Path to input audio file
            output_path: Path for output audio file
            codec: Output codec
            bitrate: Output bitrate

        Returns:
            Tuple of (success, output_file_path)
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            args = [
                'ffmpeg',
                '-i', str(input_path),
                '-acodec', self._get_codec(codec),
                '-ab', bitrate,
                '-y',
                str(output_path)
            ]

            self.logger.info(f"Converting {input_path.name} to {codec}...")

            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0 and output_path.exists():
                self.logger.success(f"Converted: {output_path.name}")
                return True, str(output_path)

            return False, ""

        except Exception as e:
            self.logger.error(f"Conversion error: {e}")
            return False, ""

    def get_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds"""
        try:
            args = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(audio_path)
            ]

            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return float(result.stdout.strip())

            return 0.0

        except Exception:
            return 0.0


if __name__ == '__main__':
    # Test extraction
    extractor = AudioExtractor()

    # Check duration
    video = Path("/tmp/video-processing/audio.mp3")
    if video.exists():
        duration = extractor.get_duration(video)
        print(f"Duration: {duration}s")
