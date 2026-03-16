#!/usr/bin/env python3
"""
文本总结模块 - 智能总结提取关键信息
"""

import os
import json
import re
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class TextSummarizer:
    """文本总结处理器"""
    
    def __init__(
        self, 
        model: str = "gpt-3.5-turbo",
        language: str = "zh",
        style: str = "brief"
    ):
        self.model = model
        self.language = language
        self.style = style
        self.available_methods = self._detect_available_methods()
        
        logger.info(f"初始化文本总结器，模型: {model}, 语言: {language}, 风格: {style}")
    
    def summarize(
        self, 
        text: str, 
        output_dir: Path,
        max_length: int = 1000,
        extract_key_points: bool = True
    ) -> Optional[Path]:
        """
        总结文本内容
        
        Args:
            text: 输入文本
            output_dir: 输出目录
            max_length: 总结最大长度
            extract_key_points: 是否提取关键点
        
        Returns:
            总结文件路径
        """
        try:
            if not text or len(text.strip()) < 50:
                logger.warning("文本过短，无需总结")
                return None
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 清理和预处理文本
            cleaned_text = self._clean_text(text)
            logger.info(f"文本预处理完成: {len(cleaned_text)} 字符")
            
            # 选择总结方法
            method = self._select_summary_method(len(cleaned_text))
            logger.info(f"选择总结方法: {method}")
            
            # 生成总结
            summary_result = self._generate_summary(cleaned_text, method, max_length)
            
            if not summary_result:
                logger.error("总结生成失败")
                return None
            
            # 保存总结结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_path = output_dir / f"summary_{timestamp}.md"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(self._format_summary(summary_result, cleaned_text))
            
            # 如果需要，提取关键点
            if extract_key_points:
                key_points = self._extract_key_points(cleaned_text)
                if key_points:
                    key_points_path = output_dir / f"key_points_{timestamp}.json"
                    with open(key_points_path, 'w', encoding='utf-8') as f:
                        json.dump(key_points, f, ensure_ascii=False, indent=2)
                    logger.info(f"关键点已保存: {key_points_path}")
            
            logger.info(f"总结已保存: {summary_path}")
            return summary_path
            
        except Exception as e:
            logger.error(f"文本总结过程中发生错误: {e}", exc_info=True)
            return None
    
    def _clean_text(self, text: str) -> str:
        """清理和预处理文本"""
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符但保留中文标点
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？；：、""''()【】《》「」『』.,!?;:]', ' ', text)
        
        # 分段（按句子或段落）
        sentences = re.split(r'[。！？\.!?]\s*', text)
        cleaned_sentences = [s.strip() for s in sentences if s.strip()]
        
        return '。'.join(cleaned_sentences) + '。'
    
    def _select_summary_method(self, text_length: int) -> str:
        """根据文本长度选择总结方法"""
        if text_length < 1000:
            # 短文本使用提取式总结
            return "extractive"
        elif text_length < 5000:
            # 中等长度使用AI模型总结
            if "openai" in self.available_methods:
                return "openai"
            elif "claude" in self.available_methods:
                return "claude"
            else:
                return "abstractive"
        else:
            # 长文本使用分层总结
            return "hierarchical"
    
    def _generate_summary(
        self, 
        text: str, 
        method: str, 
        max_length: int
    ) -> Optional[Dict[str, Any]]:
        """生成总结"""
        try:
            if method == "extractive":
                return self._extractive_summary(text, max_length)
            elif method == "abstractive":
                return self._abstractive_summary(text, max_length)
            elif method == "openai":
                return self._openai_summary(text, max_length)
            elif method == "claude":
                return self._claude_summary(text, max_length)
            elif method == "hierarchical":
                return self._hierarchical_summary(text, max_length)
            else:
                logger.warning(f"未知总结方法: {method}，使用提取式总结")
                return self._extractive_summary(text, max_length)
                
        except Exception as e:
            logger.error(f"总结生成过程中发生错误: {e}")
            return None
    
    def _extractive_summary(self, text: str, max_length: int) -> Dict[str, Any]:
        """提取式总结（基于关键词和句子重要性）"""
        try:
            # 分句
            sentences = [s.strip() for s in text.split('。') if s.strip()]
            
            if not sentences:
                return {"summary": "无有效内容", "method": "extractive"}
            
            # 简单实现：取前N个句子
            important_sentences = sentences[:min(5, len(sentences))]
            summary = '。'.join(important_sentences) + '。'
            
            # 确保不超过最大长度
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            return {
                "summary": summary,
                "method": "extractive",
                "sentence_count": len(important_sentences),
                "original_sentences": len(sentences)
            }
            
        except Exception as e:
            logger.error(f"提取式总结失败: {e}")
            return {"summary": "总结生成失败", "method": "extractive", "error": str(e)}
    
    def _abstractive_summary(self, text: str, max_length: int) -> Dict[str, Any]:
        """抽象式总结（基于规则和模板）"""
        try:
            # 这里可以使用更复杂的规则
            # 简单实现：生成基于模板的总结
            
            # 提取关键信息
            key_themes = self._extract_themes(text)
            main_points = self._extract_main_points(text)
            
            # 根据语言和风格选择模板
            if self.language == "zh":
                if self.style == "brief":
                    summary = f"主要内容：{key_themes[0] if key_themes else '未识别'}。\n"
                    summary += f"关键点：{', '.join(main_points[:3]) if main_points else '未提取'}。"
                else:
                    summary = f"内容概述：本文讨论了{', '.join(key_themes[:3]) if key_themes else '多个主题'}。\n\n"
                    summary += f"核心观点：\n"
                    for i, point in enumerate(main_points[:5], 1):
                        summary += f"{i}. {point}\n"
            else:
                summary = f"Main content: {key_themes[0] if key_themes else 'Not identified'}.\n"
                summary += f"Key points: {', '.join(main_points[:3]) if main_points else 'Not extracted'}."
            
            return {
                "summary": summary,
                "method": "abstractive",
                "themes": key_themes[:5],
                "points": main_points[:10],
                "style": self.style
            }
            
        except Exception as e:
            logger.error(f"抽象式总结失败: {e}")
            return {"summary": "总结生成失败", "method": "abstractive", "error": str(e)}
    
    def _openai_summary(self, text: str, max_length: int) -> Dict[str, Any]:
        """使用OpenAI API总结"""
        try:
            # 这里需要OpenAI API密钥
            # 暂时使用抽象式总结替代
            logger.warning("OpenAI API需要配置，使用抽象式总结替代")
            return self._abstractive_summary(text, max_length)
            
        except Exception as e:
            logger.error(f"OpenAI总结失败: {e}")
            return {"summary": "OpenAI总结失败", "method": "openai", "error": str(e)}
    
    def _claude_summary(self, text: str, max_length: int) -> Dict[str, Any]:
        """使用Claude API总结"""
        try:
            # 这里需要Claude API密钥
            logger.warning("Claude API需要配置，使用抽象式总结替代")
            return self._abstractive_summary(text, max_length)
            
        except Exception as e:
            logger.error(f"Claude总结失败: {e}")
            return {"summary": "Claude总结失败", "method": "claude", "error": str(e)}
    
    def _hierarchical_summary(self, text: str, max_length: int) -> Dict[str, Any]:
        """分层总结（适用于长文本）"""
        try:
            # 将长文本分段
            segments = self._split_long_text(text, segment_length=2000)
            
            if not segments:
                return self._abstractive_summary(text, max_length)
            
            # 对每个分段进行初步总结
            segment_summaries = []
            for i, segment in enumerate(segments, 1):
                segment_result = self._extractive_summary(segment, max_length=300)
                if segment_result and "summary" in segment_result:
                    segment_summaries.append(f"第{i}部分: {segment_result['summary']}")
            
            # 合并分段总结
            combined_summary = "\n\n".join(segment_summaries)
            
            # 对合并的总结再进行一次总结
            if len(combined_summary) > max_length:
                final_result = self._extractive_summary(combined_summary, max_length)
            else:
                final_result = {
                    "summary": combined_summary,
                    "method": "hierarchical",
                    "segments": len(segments)
                }
            
            return final_result
            
        except Exception as e:
            logger.error(f"分层总结失败: {e}")
            return {"summary": "分层总结失败", "method": "hierarchical", "error": str(e)}
    
    def _extract_themes(self, text: str, max_themes: int = 5) -> List[str]:
        """提取主题"""
        # 简单实现：基于高频词
        words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        
        if not words:
            words = re.findall(r'\b\w{4,}\b', text)
        
        from collections import Counter
        word_freq = Counter(words)
        
        # 排除常见词
        common_words = {"这个", "那个", "我们", "他们", "可以", "但是", "因为", "所以"}
        themes = [word for word, count in word_freq.most_common(20) 
                 if word not in common_words and count > 1]
        
        return themes[:max_themes]
    
    def _extract_main_points(self, text: str, max_points: int = 10) -> List[str]:
        """提取主要观点"""
        # 简单实现：基于句子长度和位置
        sentences = [s.strip() for s in text.split('。') if s.strip() and len(s) > 10]
        
        if not sentences:
            return []
        
        # 优先选择开头和结尾的句子，以及较长的句子
        points = []
        
        # 开头句子（通常包含主要观点）
        if sentences:
            points.append(sentences[0])
        
        # 结尾句子（通常包含结论）
        if len(sentences) > 1:
            points.append(sentences[-1])
        
        # 中间较长的句子
        sorted_by_length = sorted(sentences[1:-1] if len(sentences) > 2 else sentences, 
                                 key=len, reverse=True)
        points.extend(sorted_by_length[:3])
        
        # 去重
        unique_points = []
        for point in points:
            if point not in unique_points:
                unique_points.append(point)
        
        return unique_points[:max_points]
    
    def _extract_key_points(self, text: str) -> Dict[str, Any]:
        """提取关键点（用于JSON输出）"""
        try:
            themes = self._extract_themes(text, 3)
            main_points = self._extract_main_points(text, 5)
            
            # 估算阅读时间（假设每分钟300词）
            word_count = len(text.split())
            reading_time = max(1, word_count // 300)
            
            return {
                "themes": themes,
                "main_points": main_points,
                "word_count": word_count,
                "estimated_reading_time_minutes": reading_time,
                "summary_style": self.style,
                "language": self.language,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"提取关键点失败: {e}")
            return {}
    
    def _split_long_text(self, text: str, segment_length: int = 2000) -> List[str]:
        """分割长文本"""
        if len(text) <= segment_length:
            return [text]
        
        segments = []
        current_segment = ""
        
        # 尽量在句子边界分割
        sentences = re.split(r'([。！？\.!?]\s*)', text)
        
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i+1]
            else:
                sentence = sentences[i]
            
            if len(current_segment) + len(sentence) <= segment_length:
                current_segment += sentence
            else:
                if current_segment:
                    segments.append(current_segment)
                current_segment = sentence
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def _format_summary(self, summary_result: Dict[str, Any], original_text: str) -> str:
        """格式化总结输出"""
        template = f"""# 📝 视频内容总结

## 基本信息
- 总结时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 总结方法: {summary_result.get('method', 'unknown')}
- 总结风格: {self.style}
- 语言: {self.language}

## 内容摘要

{summary_result.get('summary', '无总结内容')}

"""
        
        # 添加额外信息
        if 'themes' in summary_result and summary_result['themes']:
            template += f"\n## 主要主题\n"
            for theme in summary_result['themes']:
                template += f"- {theme}\n"
        
        if 'points' in summary_result and summary_result['points']:
            template += f"\n## 关键观点\n"
            for i, point in enumerate(summary_result['points'][:5], 1):
                template += f"{i}. {point}\n"
        
        # 添加统计信息
        word_count = len(original_text.split())
        char_count = len(original_text)
        
        template += f"""
## 统计信息
- 原文词数: {word_count}
- 原文字符数: {char_count}
- 总结长度: {len(summary_result.get('summary', ''))} 字符
- 压缩率: {len(summary_result.get('summary', '')) / max(char_count, 1) * 100:.1f}%

---

*此总结由视频转文字总结工具自动生成*
"""
        
        return template
    
    def _detect_available_methods(self) -> Dict[str, bool]:
        """检测可用总结方法"""
        methods = {
            "extractive": True,  # 总是可用
            "abstractive": True,  # 总是可用
            "openai": self._check_openai_available(),
            "claude": self._check_claude_available(),
            "hierarchical": True  # 总是可用
        }
        return methods
    
    def _check_openai_available(self) -> bool:
        """检查OpenAI API是否可用"""
        # 这里需要检查环境变量中的API密钥
        # 暂时返回False
        return False
    
    def _check_claude_available(self) -> bool:
        """检查Claude API是否可用"""
        # 这里需要检查环境变量中的API密钥
        # 暂时返回False
        return False

# 兼容性函数
def summarize_text(
    text: str,
    output_dir: Path,
    model: str = "gpt-3.5-turbo",
    language: str = "zh",
    style: str = "brief"
) -> Optional[Path]:
    """
    兼容性函数
    
    Args:
        text: 输入文本
        output_dir: 输出目录
        model: 总结模型
        language: 语言
        style: 总结风格
    
    Returns:
        总结文件路径
    """
    summarizer = TextSummarizer(model=model, language=language, style=style)
    return summarizer.summarize(text, output_dir)

def create_detailed_report(
    transcript_path: Path,
    summary_path: Path,
    output_dir: Path
) -> Optional[Path]:
    """
    创建详细报告
    
    Args:
        transcript_path: 转录文件路径
        summary_path: 总结文件路径
        output_dir: 输出目录
    
    Returns:
        报告文件路径
    """
    try:
        if not transcript_path.exists() or not summary_path.exists():
            logger.error("转录或总结文件不存在")
            return None
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 读取文件内容
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = f.read()
        
        # 生成报告
        report_path = output_dir / "detailed_report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 📊 视频分析详细报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 总结摘要\n")
            f.write(summary + "\n\n")
            
            f.write("## 完整转录（前1000字符）\n")
            f.write("```\n")
            f.write(transcript[:1000])
            if len(transcript) > 1000:
                f.write("\n...\n")
                f.write(f"（全文共{len(transcript)}字符，此处显示前1000字符）")
            f.write("\n```\n\n")
            
            f.write("## 文件信息\n")
            f.write(f"- 转录文件: {transcript_path.name} ({transcript_path.stat().st_size} 字节)\n")
            f.write(f"- 总结文件: {summary_path.name} ({summary_path.stat().st_size} 字节)\n")
            f.write(f"- 字符统计: {len(transcript)} 字符, {len(transcript.split())} 词\n")
        
        logger.info(f"详细报告已生成: {report_path}")
        return report_path
        
    except Exception as e:
        logger.error(f"创建详细报告时发生错误: {e}")
        return None

if __name__ == '__main__':
    # 测试代码
    import sys
    
    if len(sys.argv) > 1:
        text_file = Path(sys.argv[1])
        print(f"测试文本总结: {text_file}")
        
        if text_file.exists():
            with open(text_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            output_dir = Path("./test_summary")
            result = summarize_text(text, output_dir)
            
            if result:
                print(f"总结成功: {result}")
            else:
                print("总结失败")
        else:
            print("文件不存在")