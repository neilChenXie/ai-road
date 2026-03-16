#!/usr/bin/env python3
"""
语音转文字模块 - 支持多种语音识别引擎
"""

import os
import sys
import json
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import timedelta

logger = logging.getLogger(__name__)

class SpeechToText:
    """语音转文字处理器"""
    
    def __init__(self, model: str = "base", language: str = "auto"):
        self.model = model
        self.language = language
        self.available_engines = self._detect_available_engines()
        
        logger.info(f"初始化语音转文字引擎，模型: {model}, 语言: {language}")
        logger.info(f"可用引擎: {list(self.available_engines.keys())}")
    
    def transcribe(
        self, 
        audio_path: Path, 
        output_dir: Path
    ) -> Optional[Path]:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            output_dir: 输出目录
        
        Returns:
            转录文本文件路径
        """
        try:
            if not audio_path.exists():
                logger.error(f"音频文件不存在: {audio_path}")
                return None
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 选择最佳可用引擎
            engine = self._select_best_engine()
            if not engine:
                logger.error("没有可用的语音识别引擎")
                return None
            
            logger.info(f"使用引擎: {engine}")
            
            # 根据音频大小决定是否分段处理
            audio_size_mb = audio_path.stat().st_size / (1024 * 1024)
            if audio_size_mb > 100:  # 大于100MB的音频分段处理
                logger.info(f"音频较大 ({audio_size_mb:.1f}MB)，启用分段处理")
                return self._transcribe_large_audio(audio_path, output_dir, engine)
            else:
                return self._transcribe_with_engine(audio_path, output_dir, engine)
                
        except Exception as e:
            logger.error(f"语音转文字过程中发生错误: {e}", exc_info=True)
            return None
    
    def _select_best_engine(self) -> Optional[str]:
        """选择最佳可用引擎"""
        # 优先级：Whisper > Azure > Google > 其他
        priority_order = ["whisper", "azure", "google", "vosk", "sphinx"]
        
        for engine in priority_order:
            if self.available_engines.get(engine, False):
                return engine
        
        return None
    
    def _transcribe_with_engine(
        self, 
        audio_path: Path, 
        output_dir: Path,
        engine: str
    ) -> Optional[Path]:
        """使用指定引擎转录"""
        try:
            transcript_path = output_dir / f"{audio_path.stem}_transcript.txt"
            timestamp_path = output_dir / f"{audio_path.stem}_timestamps.txt"
            json_path = output_dir / f"{audio_path.stem}_transcript.json"
            
            if engine == "whisper":
                success = self._transcribe_with_whisper(
                    audio_path, transcript_path, timestamp_path, json_path
                )
            elif engine == "azure":
                success = self._transcribe_with_azure(
                    audio_path, transcript_path
                )
            elif engine == "google":
                success = self._transcribe_with_google(
                    audio_path, transcript_path
                )
            elif engine == "vosk":
                success = self._transcribe_with_vosk(
                    audio_path, transcript_path
                )
            else:
                logger.warning(f"引擎 {engine} 暂未实现，使用Whisper替代")
                success = self._transcribe_with_whisper(
                    audio_path, transcript_path, timestamp_path, json_path
                )
            
            if success and transcript_path.exists():
                # 读取转录文本并统计
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    transcript_text = f.read()
                
                word_count = len(transcript_text.split())
                char_count = len(transcript_text)
                logger.info(f"转录完成: {word_count} 词, {char_count} 字符")
                
                return transcript_path
            else:
                logger.error(f"使用引擎 {engine} 转录失败")
                return None
                
        except Exception as e:
            logger.error(f"引擎 {engine} 转录过程中发生错误: {e}", exc_info=True)
            return None
    
    def _transcribe_large_audio(
        self, 
        audio_path: Path, 
        output_dir: Path,
        engine: str
    ) -> Optional[Path]:
        """处理大型音频文件（分段转录）"""
        try:
            from .audio_extractor import split_audio_by_duration
            
            # 创建临时目录存放分段音频
            temp_dir = output_dir / "segments"
            temp_dir.mkdir(exist_ok=True)
            
            # 分段音频（每10分钟一段）
            segments = split_audio_by_duration(audio_path, temp_dir, segment_duration=600)
            
            if not segments:
                logger.error("音频分段失败")
                return None
            
            logger.info(f"音频分段完成，共 {len(segments)} 段")
            
            # 转录每个分段
            all_transcripts = []
            for i, segment in enumerate(segments, 1):
                logger.info(f"转录第 {i}/{len(segments)} 段: {segment.name}")
                
                segment_output = output_dir / f"segment_{i:03d}"
                segment_output.mkdir(exist_ok=True)
                
                transcript = self._transcribe_with_engine(segment, segment_output, engine)
                if transcript and transcript.exists():
                    with open(transcript, 'r', encoding='utf-8') as f:
                        all_transcripts.append(f.read().strip())
                    logger.info(f"第 {i} 段转录完成")
                else:
                    logger.warning(f"第 {i} 段转录失败，跳过")
            
            # 合并所有转录
            if all_transcripts:
                merged_text = "\n\n".join(all_transcripts)
                transcript_path = output_dir / f"{audio_path.stem}_transcript.txt"
                
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(merged_text)
                
                # 清理临时文件
                import shutil
                shutil.rmtree(temp_dir)
                
                logger.info(f"大型音频转录完成，合并 {len(all_transcripts)} 段")
                return transcript_path
            else:
                logger.error("所有分段转录都失败")
                return None
                
        except Exception as e:
            logger.error(f"大型音频转录过程中发生错误: {e}", exc_info=True)
            return None
    
    def _transcribe_with_whisper(
        self,
        audio_path: Path,
        transcript_path: Path,
        timestamp_path: Path,
        json_path: Path
    ) -> bool:
        """使用OpenAI Whisper转录"""
        try:
            # 构建Whisper命令
            cmd = [
                "whisper",
                str(audio_path),
                "--model", self.model,
                "--output_dir", str(transcript_path.parent),
                "--output_format", "txt",
                "--verbose", "False"
            ]
            
            if self.language != "auto":
                cmd.extend(["--language", self.language])
            
            logger.info(f"执行Whisper命令: {' '.join(cmd)}")
            
            # 执行转录
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                # 检查输出文件
                expected_files = [
                    transcript_path,
                    timestamp_path,
                    json_path
                ]
                
                for file in expected_files:
                    if file.exists():
                        logger.info(f"生成文件: {file.name}")
                
                return True
            else:
                logger.error(f"Whisper转录失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Whisper转录过程中发生错误: {e}", exc_info=True)
            return False
    
    def _transcribe_with_azure(
        self,
        audio_path: Path,
        transcript_path: Path
    ) -> bool:
        """使用Azure语音服务转录"""
        try:
            # 这里需要配置Azure语音服务的密钥和区域
            # 由于需要API密钥，这里只提供框架代码
            logger.warning("Azure语音服务需要API密钥，暂未实现完整功能")
            return False
            
        except Exception as e:
            logger.error(f"Azure转录过程中发生错误: {e}")
            return False
    
    def _transcribe_with_google(
        self,
        audio_path: Path,
        transcript_path: Path
    ) -> bool:
        """使用Google语音服务转录"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(str(audio_path)) as source:
                audio = recognizer.record(source)
                
                try:
                    text = recognizer.recognize_google(
                        audio,
                        language=self.language if self.language != "auto" else "zh-CN"
                    )
                    
                    with open(transcript_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    
                    logger.info("Google语音识别成功")
                    return True
                    
                except sr.UnknownValueError:
                    logger.error("Google语音识别无法理解音频")
                    return False
                except sr.RequestError as e:
                    logger.error(f"Google语音识别服务错误: {e}")
                    return False
                    
        except Exception as e:
            logger.error(f"Google转录过程中发生错误: {e}")
            return False
    
    def _transcribe_with_vosk(
        self,
        audio_path: Path,
        transcript_path: Path
    ) -> bool:
        """使用Vosk离线语音识别"""
        try:
            # Vosk需要下载模型文件
            logger.warning("Vosk需要下载语言模型，暂未实现完整功能")
            return False
            
        except Exception as e:
            logger.error(f"Vosk转录过程中发生错误: {e}")
            return False
    
    def _detect_available_engines(self) -> Dict[str, bool]:
        """检测可用引擎"""
        engines = {
            "whisper": self._check_whisper_installed(),
            "azure": self._check_azure_available(),
            "google": self._check_google_available(),
            "vosk": self._check_vosk_available(),
            "sphinx": self._check_sphinx_available()
        }
        return engines
    
    def _check_whisper_installed(self) -> bool:
        """检查Whisper是否安装"""
        try:
            result = subprocess.run(["whisper", "--version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _check_azure_available(self) -> bool:
        """检查Azure语音服务是否可用"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            # 这里需要检查环境变量或配置文件中的API密钥
            # 暂时返回False
            return False
        except ImportError:
            return False
    
    def _check_google_available(self) -> bool:
        """检查Google语音识别是否可用"""
        try:
            import speech_recognition as sr
            return True
        except ImportError:
            return False
    
    def _check_vosk_available(self) -> bool:
        """检查Vosk是否可用"""
        try:
            import vosk
            return True
        except ImportError:
            return False
    
    def _check_sphinx_available(self) -> bool:
        """检查CMU Sphinx是否可用"""
        try:
            from pocketsphinx import pocketsphinx
            return True
        except ImportError:
            return False

# 兼容性函数
def transcribe_audio(
    audio_path: Path,
    output_dir: Path,
    language: str = "auto",
    model: str = "base"
) -> Optional[Path]:
    """
    兼容性函数
    
    Args:
        audio_path: 音频文件路径
        output_dir: 输出目录
        language: 识别语言
        model: Whisper模型大小
    
    Returns:
        转录文本文件路径
    """
    stt = SpeechToText(model=model, language=language)
    return stt.transcribe(audio_path, output_dir)

def get_transcript_stats(transcript_path: Path) -> Dict[str, Any]:
    """
    获取转录统计信息
    
    Args:
        transcript_path: 转录文件路径
    
    Returns:
        统计信息字典
    """
    try:
        if not transcript_path.exists():
            return {}
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 基本统计
        lines = text.strip().split('\n')
        words = text.split()
        characters = len(text)
        
        return {
            "file_size": transcript_path.stat().st_size,
            "line_count": len(lines),
            "word_count": len(words),
            "character_count": characters,
            "average_word_length": characters / max(len(words), 1),
            "estimated_duration_minutes": len(words) / 150  # 假设每分钟150词
        }
    except Exception as e:
        logger.error(f"获取转录统计时发生错误: {e}")
        return {}

if __name__ == '__main__':
    # 测试代码
    import sys
    if len(sys.argv) > 1:
        audio_file = Path(sys.argv[1])
        print(f"测试语音转文字: {audio_file}")
        
        output_dir = Path("./test_transcript")
        result = transcribe_audio(audio_file, output_dir)
        
        if result:
            print(f"转录成功: {result}")
            stats = get_transcript_stats(result)
            print(f"统计信息: {stats}")
        else:
            print("转录失败")