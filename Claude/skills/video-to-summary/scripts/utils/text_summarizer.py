"""
Text summarization utilities
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


class TextSummarizer:
    """Generate structured summaries from transcripts"""

    def __init__(self, config: Dict = None):
        self.config = config or {}

    def summarize(self, transcript_data: Dict, metadata: Dict = None) -> Dict:
        """
        Generate structured summary

        Args:
            transcript_data: Whisper transcript data
            metadata: Video metadata

        Returns:
            Summary data structure
        """
        # Get text
        text = self._get_text(transcript_data)

        # Generate summary components
        summary = {
            'title': metadata.get('title', 'Untitled'),
            'overview': self._generate_overview(text),
            'key_points': self._extract_key_points(text),
            'structure': self._extract_structure(text, transcript_data),
            'word_count': len(text),
            'duration': metadata.get('duration', 0),
            'transcript': text,
        }

        return summary

    def _get_text(self, transcript_data: Dict) -> str:
        """Extract plain text from transcript"""
        segments = transcript_data.get('segments', [])
        return ' '.join(s.get('text', '') for s in segments)

    def _generate_overview(self, text: str, max_words: int = 150) -> str:
        """
        Generate a brief overview

        Args:
            text: Full transcript text
            max_words: Maximum word count for overview

        Returns:
            Overview text
        """
        # Split into sentences
        sentences = re.split(r'[。！？!?]', text)

        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return "无法生成摘要"

        # Take first few sentences
        overview = '。'.join(sentences[:3])

        # Trim to max words
        words = overview.split()
        if len(words) > max_words:
            overview = ' '.join(words[:max_words]) + '...'

        return overview

    def _extract_key_points(self, text: str, max_points: int = 10) -> List[str]:
        """
        Extract key points from text

        Args:
            text: Full transcript text
            max_points: Maximum number of key points

        Returns:
            List of key points
        """
        # Look for patterns indicating important points
        key_point_patterns = [
            r'(首先|第一|首先)[，、：:](.+?)([。！？!?]|$)',
            r'(其次|第二|然后)[，、：:](.+?)([。！？!?]|$)',
            r'(再次|第三|最后)[，、：:](.+?)([。！？!?]|$)',
            r'(关键|重要|核心|主要)[点是][，、：:]?(.+?)([。！？!?]|$)',
            r'(要点|关键点)[，、：:](.+?)([。！？!?]|$)',
        ]

        points = []

        for pattern in key_point_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                point = match.group(2).strip()
                if point and len(point) > 5:  # Filter out too short points
                    points.append(point)

        # If no structured points found, use paragraph sentences
        if not points:
            paragraphs = text.split('\n\n')
            for para in paragraphs[:max_points]:
                sentences = re.split(r'[。！？!?]', para.strip())
                if sentences and sentences[0].strip():
                    points.append(sentences[0].strip() + '。')

        # Limit number of points
        return points[:max_points]

    def _extract_structure(self, text: str, transcript_data: Dict) -> List[Dict]:
        """
        Extract structured sections from transcript

        Args:
            text: Full transcript text
            transcript_data: Full Whisper data with timestamps

        Returns:
            List of sections with timestamps
        """
        segments = transcript_data.get('segments', [])

        # Try to detect section transitions
        # Look for longer pauses or topic changes
        sections = []
        current_section = {
            'start': 0,
            'end': 0,
            'text': '',
            'duration': 0
        }

        for i, segment in enumerate(segments):
            segment_text = segment.get('text', '')
            segment_start = segment.get('start', 0)
            segment_end = segment.get('end', 0)

            # Check for potential section break (long gap or topic indicator)
            next_segment = segments[i + 1] if i + 1 < len(segments) else None
            is_break = False

            if next_segment:
                gap = next_segment.get('start', 0) - segment_end
                if gap > 5:  # 5+ second gap
                    is_break = True

            # Accumulate text
            current_section['text'] += segment_text
            current_section['end'] = segment_end

            # Add section if break or last segment
            if is_break or segment == segments[-1]:
                current_section['duration'] = current_section['end'] - current_section['start']
                current_section['text'] = current_section['text'].strip()
                if current_section['text']:
                    sections.append(current_section.copy())
                # Start new section
                next_start = next_segment.get('start', segment_end) if next_segment else segment_end
                current_section = {
                    'start': next_start,
                    'end': segment_end,
                    'text': '',
                    'duration': 0
                }

        # If no sections found (no breaks), return single section
        if not sections and segments:
            return [{
                'start': segments[0].get('start', 0),
                'end': segments[-1].get('end', 0),
                'text': text,
                'duration': segments[-1].get('end', 0) - segments[0].get('start', 0)
            }]

        return sections

    def to_markdown(self, summary: Dict) -> str:
        """
        Convert summary to Markdown format

        Args:
            summary: Summary data structure

        Returns:
            Markdown formatted summary
        """
        lines = []

        # Title
        lines.append(f"# {summary['title']}")
        lines.append("")

        # Metadata
        if summary.get('duration'):
            duration_min = int(summary['duration'] / 60)
            duration_sec = int(summary['duration'] % 60)
            lines.append(f"**时长**: {duration_min}分{duration_sec}秒")
        if summary.get('word_count'):
            lines.append(f"**字数**: {summary['word_count']} 字")
        lines.append("")

        # Overview
        lines.append("## 概述")
        lines.append(summary['overview'])
        lines.append("")

        # Key Points
        if summary['key_points']:
            lines.append("## 关键点")
            for i, point in enumerate(summary['key_points'], 1):
                lines.append(f"{i}. {point}")
            lines.append("")

        # Structure
        if summary['structure']:
            lines.append("## 详细内容")
            for i, section in enumerate(summary['structure'], 1):
                start_min = int(section['start'] / 60)
                start_sec = int(section['start'] % 60)
                lines.append(f"\n### 第 {i} 部分 ({start_min:02d}:{start_sec:02d})")
                lines.append(section['text'])
                lines.append("")

        return '\n'.join(lines)

    def to_json(self, summary: Dict, output_path: Path) -> None:
        """
        Save summary as JSON

        Args:
            summary: Summary data structure
            output_path: Output file path
        """
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    def save(self, summary: Dict, output_dir: Path, formats: List[str] = ['md', 'json']) -> List[Path]:
        """
        Save summary in multiple formats

        Args:
            summary: Summary data structure
            output_dir: Output directory
            formats: List of formats to save (md, json)

        Returns:
            List of saved file paths
        """
        saved_files = []
        base_name = self._sanitize_filename(summary['title'])

        output_dir.mkdir(parents=True, exist_ok=True)

        if 'md' in formats:
            md_path = output_dir / f"{base_name}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(self.to_markdown(summary))
            saved_files.append(md_path)

        if 'json' in formats:
            json_path = output_dir / f"{base_name}_summary.json"
            self.to_json(summary, json_path)
            saved_files.append(json_path)

        return saved_files

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename by removing invalid characters"""
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        # Replace multiple spaces with single space
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]

        return sanitized or 'summary'


if __name__ == '__main__':
    # Test summarization
    import json

    summarizer = TextSummarizer()

    # Mock transcript data
    transcript_data = {
        'segments': [
            {'start': 0, 'end': 5, 'text': '首先介绍这个问题。'},
            {'start': 5, 'end': 10, 'text': '然后分析原因。'},
            {'start': 10, 'end': 15, 'text': '最后给出解决方案。'},
        ]
    }

    metadata = {'title': '测试视频', 'duration': 15}

    summary = summarizer.summarize(transcript_data, metadata)
    print(summarizer.to_markdown(summary))
