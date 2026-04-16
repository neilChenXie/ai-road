"""
Text Summarizer - Generate structured summary using LLM
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import logging


class TextSummarizer:
    """Generate structured summary from transcript"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def summarize(self, transcript_data: Dict, video_info: Dict) -> Dict:
        """
        Generate summary from transcript

        Args:
            transcript_data: Whisper transcript data
            video_info: Video metadata

        Returns:
            Summary data dict
        """
        # Extract text
        text = self._extract_text(transcript_data)

        # Build summary structure
        summary = {
            'title': video_info.get('title', '未知标题'),
            'platform': video_info.get('platform', 'unknown'),
            'platform_name': self._get_platform_name(video_info.get('platform', 'unknown')),
            'video_id': video_info.get('video_id', ''),
            'author': video_info.get('uploader', video_info.get('author', '未知')),
            'duration': video_info.get('duration', 0),
            'duration_formatted': self._format_duration(video_info.get('duration', 0)),
            'url': video_info.get('webpage_url', video_info.get('url', '')),
            'processed_at': datetime.now().isoformat(),
            'transcript_length': len(text),
            'summary': self._generate_summary_structure(text, video_info)
        }

        return summary

    def _extract_text(self, transcript_data: Dict) -> str:
        """Extract plain text from transcript"""
        if 'text' in transcript_data:
            return transcript_data['text'].strip()

        if 'segments' in transcript_data:
            return ' '.join(seg.get('text', '') for seg in transcript_data['segments']).strip()

        return ''

    def _get_platform_name(self, platform: str) -> str:
        """Get display name for platform"""
        names = {
            'bilibili': 'B站',
            'xiaohongshu': '小红书'
        }
        return names.get(platform, platform)

    def _format_duration(self, seconds: float) -> str:
        """Format duration to MM:SS or HH:MM:SS"""
        if not seconds:
            return '00:00'

        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def _generate_summary_structure(self, text: str, video_info: Dict) -> Dict:
        """
        Generate summary structure for LLM to fill

        This creates a template that Claude will use to generate the actual summary
        """
        title = video_info.get('title', '未知标题')
        platform = self._get_platform_name(video_info.get('platform', 'unknown'))
        author = video_info.get('uploader', video_info.get('author', '未知'))
        duration = self._format_duration(video_info.get('duration', 0))

        return {
            'overview': f"这是一个来自{platform}的视频，标题为《{title}》，由{author}发布，时长{duration}。",
            'key_info': {
                'platform': platform,
                'duration': duration,
                'author': author
            },
            'core_points': [],
            'detailed_content': text[:5000] if len(text) > 5000 else text,  # Limit for context
            'key_quotes': [],
            'conclusion': ''
        }

    def generate_markdown(self, summary: Dict) -> str:
        """
        Generate Markdown formatted summary

        Args:
            summary: Summary data dict

        Returns:
            Markdown formatted string
        """
        lines = []

        # Title
        lines.append(f"# {summary['title']}\n")

        # Overview
        lines.append("## 概述\n")
        overview = summary['summary'].get('overview', '')
        if overview:
            lines.append(f"{overview}\n")
        else:
            lines.append("视频内容概述...\n")

        # Key Info
        lines.append("## 关键信息\n")
        key_info = summary['summary'].get('key_info', {})
        lines.append(f"- **平台**: {key_info.get('platform', summary['platform_name'])}")
        lines.append(f"- **时长**: {key_info.get('duration', summary['duration_formatted'])}")
        lines.append(f"- **UP主/作者**: {key_info.get('author', summary['author'])}")
        lines.append("")

        # Core Points
        lines.append("## 核心观点\n")
        core_points = summary['summary'].get('core_points', [])
        if core_points:
            for i, point in enumerate(core_points, 1):
                lines.append(f"{i}. {point}")
            lines.append("")
        else:
            lines.append("1. 核心观点一")
            lines.append("2. 核心观点二")
            lines.append("3. 核心观点三")
            lines.append("")

        # Detailed Content
        lines.append("## 详细内容\n")
        detailed = summary['summary'].get('detailed_content', '')
        if detailed:
            # Split into paragraphs
            paragraphs = detailed.split('\n\n')
            for p in paragraphs[:10]:  # Limit paragraphs
                if p.strip():
                    lines.append(f"{p.strip()}\n")
        else:
            lines.append("视频详细内容总结...\n")

        # Key Quotes
        lines.append("## 关键引用\n")
        quotes = summary['summary'].get('key_quotes', [])
        if quotes:
            for quote in quotes:
                lines.append(f"> {quote}")
            lines.append("")
        else:
            lines.append("> 视频中的重要引用或金句\n")

        # Conclusion
        lines.append("## 总结\n")
        conclusion = summary['summary'].get('conclusion', '')
        if conclusion:
            lines.append(f"{conclusion}\n")
        else:
            lines.append("一句话总结视频主旨。\n")

        # Metadata
        lines.append("---")
        lines.append(f"*处理时间: {summary['processed_at']}*")
        lines.append(f"*视频链接: {summary['url']}*")

        return '\n'.join(lines)

    def save(self, summary: Dict, output_dir: Path, formats: List[str] = None) -> Dict[str, Path]:
        """
        Save summary to files

        Args:
            summary: Summary data dict
            output_dir: Output directory
            formats: List of formats (md, json)

        Returns:
            Dict of format -> file path
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}
        formats = formats or ['md', 'json']

        # Clean title for filename
        safe_title = self._safe_filename(summary['title'])

        if 'md' in formats:
            md_path = output_dir / f"{safe_title}.md"
            md_content = self.generate_markdown(summary)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            files['md'] = md_path
            self.logger.info(f"保存Markdown: {md_path}")

        if 'json' in formats:
            json_path = output_dir / f"{safe_title}_summary.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            files['json'] = json_path
            self.logger.info(f"保存JSON: {json_path}")

        return files

    def _safe_filename(self, title: str) -> str:
        """Create safe filename from title"""
        import re
        # Remove invalid characters
        safe = re.sub(r'[<>:"/\\|?*]', '', title)
        # Limit length
        return safe[:100] if len(safe) > 100 else safe
