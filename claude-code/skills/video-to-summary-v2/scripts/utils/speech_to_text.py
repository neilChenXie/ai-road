"""
Speech to Text - Transcribe audio using Whisper
"""

import subprocess
import json
from pathlib import Path
from typing import Tuple, Optional, Dict, List
import logging


class SpeechToText:
    """Transcribe audio using OpenAI Whisper"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.model = self.config.get('model', 'base')
        self.language = self.config.get('language', 'zh')

    def transcribe(self, audio_path: Path, output_dir: Path,
                   model: Optional[str] = None,
                   language: Optional[str] = None) -> Tuple[bool, Optional[Dict]]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            output_dir: Directory for output files
            model: Whisper model size (tiny/base/small/medium/large)
            language: Language code (zh/en/auto)

        Returns:
            Tuple of (success, transcript_data)
        """
        if not audio_path.exists():
            self.logger.error(f"音频文件不存在: {audio_path}")
            return False, None

        output_dir.mkdir(parents=True, exist_ok=True)

        model = model or self.model
        language = language or self.language

        # Build whisper command
        cmd = [
            'whisper',
            str(audio_path),
            '--model', model,
            '--output_dir', str(output_dir),
            '--output_format', 'json'
        ]

        # Add language if specified and not auto
        if language and language != 'auto':
            cmd.extend(['--language', language])

        self.logger.info(f"语音转录: {audio_path}")
        self.logger.debug(f"模型: {model}, 语言: {language}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes max
            )

            if result.returncode != 0:
                self.logger.error(f"转录失败: {result.stderr}")
                return False, None

            # Read the output JSON
            json_file = output_dir / f"{audio_path.stem}.json"
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return True, data

            return False, None

        except subprocess.TimeoutExpired:
            self.logger.error("转录超时")
            return False, None
        except Exception as e:
            self.logger.error(f"转录异常: {e}")
            return False, None

    def get_text(self, transcript_data: Dict) -> str:
        """Extract plain text from transcript data"""
        if 'text' in transcript_data:
            return transcript_data['text'].strip()

        # Fallback to segments
        if 'segments' in transcript_data:
            texts = [seg.get('text', '') for seg in transcript_data['segments']]
            return ' '.join(texts).strip()

        return ''

    def get_segments(self, transcript_data: Dict) -> List[Dict]:
        """Get segments with timestamps"""
        segments = []

        for seg in transcript_data.get('segments', []):
            segments.append({
                'start': seg.get('start', 0),
                'end': seg.get('end', 0),
                'text': seg.get('text', '').strip()
            })

        return segments

    def save_transcript(self, transcript_data: Dict, output_dir: Path) -> Dict[str, Path]:
        """
        Save transcript in multiple formats

        Args:
            transcript_data: Transcript data from Whisper
            output_dir: Output directory

        Returns:
            Dict of format -> file path
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        # Save JSON
        json_path = output_dir / 'transcript.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)
        files['json'] = json_path

        # Save plain text
        text_path = output_dir / 'transcript.txt'
        text = self.get_text(transcript_data)
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        files['txt'] = text_path

        # Save SRT format
        srt_path = output_dir / 'transcript.srt'
        self._save_srt(transcript_data, srt_path)
        files['srt'] = srt_path

        return files

    def _save_srt(self, transcript_data: Dict, output_path: Path):
        """Save transcript as SRT subtitle format"""
        segments = transcript_data.get('segments', [])

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, seg in enumerate(segments, 1):
                start = self._format_srt_time(seg.get('start', 0))
                end = self._format_srt_time(seg.get('end', 0))
                text = seg.get('text', '').strip()

                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
