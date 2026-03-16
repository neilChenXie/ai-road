#!/usr/bin/env python3
"""
音频提取模块 - 从视频提取高质量音频
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Optional
import tempfile

logger = logging.getLogger(__name__)

def extract_audio(
    video_path: Optional[Path],
    url: str,
    output_dir: Path,
    audio_only: bool = False,
    audio_format: str = "mp3",
    audio_quality: int = 192
) -> Optional[Path]:
    """
    从视频提取音频
    
    Args:
        video_path: 视频文件路径（如果为None且audio_only=True，则直接从URL下载音频）
        url: 视频URL（当video_path为None时使用）
        output_dir: 输出目录
        audio_only: 是否仅处理音频（不下载视频）
        audio_format: 音频格式 (mp3, wav, m4a, flac等)
        audio_quality: 音频质量 (kbps, 仅对mp3有效)
    
    Returns:
        提取的音频文件路径，失败返回None
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if video_path and video_path.exists():
            # 从本地视频文件提取音频
            logger.info(f"从视频文件提取音频: {video_path}")
            return _extract_from_file(video_path, output_dir, audio_format, audio_quality)
        
        elif audio_only:
            # 直接从URL下载音频
            logger.info(f"直接从URL下载音频: {url}")
            return _download_audio_only(url, output_dir, audio_format, audio_quality)
        
        else:
            logger.error("既无视频文件也未启用audio_only模式")
            return None
            
    except Exception as e:
        logger.error(f"音频提取过程中发生错误: {e}", exc_info=True)
        return None

def _extract_from_file(
    video_path: Path,
    output_dir: Path,
    audio_format: str,
    audio_quality: int
) -> Optional[Path]:
    """从本地视频文件提取音频"""
    try:
        # 生成输出文件名
        video_name = video_path.stem
        audio_filename = f"{video_name}_audio.{audio_format}"
        audio_path = output_dir / audio_filename
        
        logger.info(f"提取音频到: {audio_path}")
        
        # 构建ffmpeg命令
        cmd = [
            "ffmpeg",
            "-i", str(video_path),    # 输入文件
            "-vn",                    # 不包含视频
            "-y"                     # 覆盖输出文件
        ]
        
        # 根据音频格式添加参数
        if audio_format == "mp3":
            cmd.extend([
                "-acodec", "libmp3lame",
                "-ab", f"{audio_quality}k",
                "-ac", "2",           # 立体声
                "-ar", "44100"        # 采样率
            ])
        elif audio_format == "wav":
            cmd.extend([
                "-acodec", "pcm_s16le",
                "-ac", "2",
                "-ar", "44100"
            ])
        elif audio_format == "m4a":
            cmd.extend([
                "-acodec", "aac",
                "-ab", f"{audio_quality}k",
                "-ac", "2"
            ])
        elif audio_format == "flac":
            cmd.extend([
                "-acodec", "flac",
                "-compression_level", "5",
                "-ac", "2",
                "-ar", "44100"
            ])
        else:
            logger.warning(f"不支持的音频格式: {audio_format}，使用mp3代替")
            audio_format = "mp3"
            audio_filename = f"{video_name}_audio.{audio_format}"
            audio_path = output_dir / audio_filename
            cmd.extend([
                "-acodec", "libmp3lame",
                "-ab", f"{audio_quality}k"
            ])
        
        cmd.append(str(audio_path))
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行ffmpeg命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            logger.info(f"音频提取成功: {audio_path}")
            
            # 验证文件
            if audio_path.exists() and audio_path.stat().st_size > 0:
                file_size_mb = audio_path.stat().st_size / (1024 * 1024)
                logger.info(f"音频文件大小: {file_size_mb:.2f} MB")
                return audio_path
            else:
                logger.error("提取的音频文件无效")
                return None
        else:
            logger.error(f"音频提取失败: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"从文件提取音频时发生错误: {e}", exc_info=True)
        return None

def _download_audio_only(
    url: str,
    output_dir: Path,
    audio_format: str,
    audio_quality: int
) -> Optional[Path]:
    """直接从URL下载音频"""
    try:
        logger.info(f"使用yt-dlp直接下载音频: {url}")
        
        # 构建yt-dlp命令
        cmd = [
            "yt-dlp",
            "-P", str(output_dir),
            "-o", f"%(title)s_audio.%(ext)s",
            "-x",                     # 提取音频
            "--audio-format", audio_format,
            "--audio-quality", str(audio_quality),
            url
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            logger.info("音频下载成功")
            
            # 查找下载的音频文件
            for ext in [f".{audio_format}", ".mp3", ".m4a", ".wav", ".flac"]:
                for file in output_dir.glob(f"*{ext}"):
                    if file.is_file():
                        logger.info(f"找到音频文件: {file}")
                        return file
            
            logger.warning("未找到下载的音频文件")
            return None
            
        else:
            logger.error(f"音频下载失败: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"下载音频时发生错误: {e}", exc_info=True)
        return None

def enhance_audio(
    audio_path: Path,
    output_dir: Path,
    noise_reduction: bool = True,
    normalize: bool = True,
    remove_silence: bool = False
) -> Optional[Path]:
    """
    音频增强处理
    
    Args:
        audio_path: 原始音频文件路径
        output_dir: 输出目录
        noise_reduction: 是否降噪
        normalize: 是否标准化音量
        remove_silence: 是否移除静音部分
    
    Returns:
        增强后的音频文件路径
    """
    try:
        if not audio_path.exists():
            logger.error(f"音频文件不存在: {audio_path}")
            return None
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成输出文件名
        audio_name = audio_path.stem
        enhanced_filename = f"{audio_name}_enhanced{audio_path.suffix}"
        enhanced_path = output_dir / enhanced_filename
        
        logger.info(f"增强音频: {audio_path} -> {enhanced_path}")
        
        # 构建ffmpeg命令
        cmd = ["ffmpeg", "-i", str(audio_path), "-y"]
        
        # 音频滤镜链
        filters = []
        
        if noise_reduction:
            # 降噪处理
            filters.append("afftdn=nf=-20")
            logger.info("启用降噪")
        
        if normalize:
            # 音量标准化
            filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
            logger.info("启用音量标准化")
        
        if remove_silence:
            # 移除静音部分
            filters.append("silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-30dB")
            logger.info("启用静音移除")
        
        if filters:
            cmd.extend(["-af", ",".join(filters)])
        
        cmd.append(str(enhanced_path))
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            if enhanced_path.exists() and enhanced_path.stat().st_size > 0:
                file_size_mb = enhanced_path.stat().st_size / (1024 * 1024)
                logger.info(f"音频增强成功: {enhanced_path} ({file_size_mb:.2f} MB)")
                return enhanced_path
            else:
                logger.error("增强后的音频文件无效")
                return None
        else:
            logger.error(f"音频增强失败: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"音频增强过程中发生错误: {e}", exc_info=True)
        return None

def split_audio_by_duration(
    audio_path: Path,
    output_dir: Path,
    segment_duration: int = 600
) -> list[Path]:
    """
    按时长分割音频（适用于长时间音频）
    
    Args:
        audio_path: 音频文件路径
        output_dir: 输出目录
        segment_duration: 每段时长（秒）
    
    Returns:
        分割后的音频文件路径列表
    """
    try:
        if not audio_path.exists():
            logger.error(f"音频文件不存在: {audio_path}")
            return []
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"分割音频: {audio_path} (每段{segment_duration}秒)")
        
        # 构建ffmpeg命令
        cmd = [
            "ffmpeg",
            "-i", str(audio_path),
            "-f", "segment",
            "-segment_time", str(segment_duration),
            "-c", "copy",
            "-y",
            str(output_dir / f"{audio_path.stem}_%03d{audio_path.suffix}")
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            # 收集生成的分段文件
            segments = []
            for file in sorted(output_dir.glob(f"{audio_path.stem}_*{audio_path.suffix}")):
                if file.is_file():
                    segments.append(file)
            
            logger.info(f"音频分割完成，生成 {len(segments)} 个分段")
            return segments
        else:
            logger.error(f"音频分割失败: {result.stderr}")
            return []
            
    except Exception as e:
        logger.error(f"音频分割过程中发生错误: {e}", exc_info=True)
        return []

def check_ffmpeg_installed() -> bool:
    """检查ffmpeg是否已安装"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

if __name__ == '__main__':
    # 测试代码
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"测试音频提取: {url}")
        audio = extract_audio(None, url, Path("./test_audio"), audio_only=True)
        if audio:
            print(f"音频提取成功: {audio}")
        else:
            print("音频提取失败")