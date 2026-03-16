"""
Speech to text using OpenAI Whisper
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from .logger import setup_logger


class SpeechToText:
    """Speech recognition using Whisper"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = setup_logger()

    def transcribe(self, audio_path: Path, output_path: Path,
                   model: str = 'base', language: str = 'zh') -> Tuple[bool, Dict]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            output_path: Output directory for transcript files
            model: Whisper model size (tiny/base/small/medium/large)
            language: Language code (e.g., zh, en, auto)

        Returns:
            Tuple of (success, transcript_data)
        """
        try:
            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)

            # Build Whisper command
            args = [
                'whisper',
                str(audio_path),
                '--model', model,
                '--language', language if language != 'auto' else '',
                '--output_format', 'json',
                '--output_dir', str(output_path),
                '--verbose', 'False',
            ]

            # Temperature for deterministic output
            temperature = self.config.get('temperature', 0.0)
            if temperature is not None:
                args.extend(['--temperature', str(temperature)])

            # Device selection
            device = self.config.get('device', 'auto')
            if device != 'auto':
                args.extend(['--device', device])

            self.logger.info(f"Transcribing with Whisper ({model})...")

            # Run Whisper
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode != 0:
                self.logger.error(f"Transcription failed: {result.stderr}")
                return False, {}

            # Find generated JSON file
            json_file = self._find_json_output(output_path, audio_path.stem)

            if not json_file:
                self.logger.error("Could not find transcript JSON file")
                return False, {}

            # Read transcript
            with open(json_file, 'r', encoding='utf-8') as f:
                transcript_data = json.load(f)

            self.logger.success(f"Transcribed: {len(transcript_data.get('segments', []))} segments")

            return True, transcript_data

        except subprocess.TimeoutExpired:
            self.logger.error("Transcription timeout")
            return False, {}
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return False, {}

    def _find_json_output(self, output_dir: Path, base_name: str) -> Optional[Path]:
        """Find Whisper JSON output file"""
        for json_file in output_dir.glob("*.json"):
            if base_name in json_file.stem:
                return json_file
        return None

    def to_text(self, transcript_data: Dict) -> str:
        """
        Convert transcript JSON to plain text

        Args:
            transcript_data: Whisper transcript data

        Returns:
            Plain text transcript
        """
        segments = transcript_data.get('segments', [])
        text_parts = [segment.get('text', '').strip() for segment in segments]
        return '\n'.join(text_parts)

    def save_transcript(self, transcript_data: Dict, output_path: Path) -> List[Path]:
        """
        Save transcript in multiple formats

        Args:
            transcript_data: Whisper transcript data
            output_path: Output directory

        Returns:
            List of saved file paths
        """
        saved_files = []
        base_name = transcript_data.get('text', 'transcript').split()[0]

        # Save JSON
        json_path = output_path / f"{base_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)
        saved_files.append(json_path)

        # Save plain text
        text = self.to_text(transcript_data)
        txt_path = output_path / f"{base_name}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        saved_files.append(txt_path)

        # Save SRT (subtitles)
        srt_path = output_path / f"{base_name}.srt"
        self._save_srt(transcript_data, srt_path)
        saved_files.append(srt_path)

        return saved_files

    def _save_srt(self, transcript_data: Dict, output_path: Path):
        """Save transcript as SRT subtitle format"""
        segments = transcript_data.get('segments', [])

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start = segment.get('start', 0)
                end = segment.get('end', 0)
                text = segment.get('text', '').strip()

                # Format timestamps
                start_time = self._format_timestamp(start)
                end_time = self._format_timestamp(end)

                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as SRT timestamp"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    def post_process(self, text: str) -> str:
        """
        Post-process transcript for common errors

        Args:
            text: Raw transcript text

        Returns:
            Processed text
        """
        # Common Whisper corrections (can be expanded)
        corrections = {
            '股市投机': '腓肠肌',
            '赖收浴质': '耐受力',
        }

        processed = text
        for wrong, correct in corrections.items():
            processed = processed.replace(wrong, correct)

        return processed


if __name__ == '__main__':
    # Test transcription
    transcriber = SpeechToText({'temperature': 0.0})

    audio_path = Path("/tmp/video-processing/audio.mp3")
    if audio_path.exists():
        output_dir = Path("/tmp/test-transcript")
        success, transcript = transcriber.transcribe(
            audio_path,
            output_dir,
            model='base',
            language='zh'
        )
        if success:
            print(f"Transcribed {len(transcript.get('segments', []))} segments")
