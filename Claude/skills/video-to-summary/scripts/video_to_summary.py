#!/usr/bin/env python3
"""
视频转文字总结工具 v2 - 主程序
支持：B站API方案 + 多平台视频下载 → 提取音频 → 语音转文字 → 智能总结
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.video_downloader import VideoDownloader
from utils.audio_extractor import extract_audio
from utils.speech_to_text import transcribe_audio
from utils.text_summarizer import summarize_text
from utils.platform_detector import detect_platform, get_platform_info, has_api_support

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoToSummaryProcessorV2:
    """视频转文字总结处理器 v2 - 支持B站API"""
    
    def __init__(self, args):
        self.args = args
        self.output_dir = Path(args.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一的任务ID
        self.task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.work_dir = self.output_dir / self.task_id
        self.work_dir.mkdir(exist_ok=True)
        
        # 创建下载器
        self.downloader = VideoDownloader(
            output_base_dir=str(self.work_dir),
            use_api=args.use_api
        )
        
        logger.info(f"任务ID: {self.task_id}")
        logger.info(f"工作目录: {self.work_dir}")
        logger.info(f"API支持: {'启用' if args.use_api else '禁用'}")
        
    def analyze_url(self, url: str) -> dict:
        """分析URL，提供处理建议"""
        logger.info(f"分析URL: {url}")
        
        analysis = {
            "url": url,
            "platform": None,
            "platform_info": None,
            "api_support": None,
            "recommendations": [],
            "warnings": [],
            "estimated_duration": "未知",
            "download_method": "未知"
        }
        
        try:
            # 1. 检测平台
            platform = detect_platform(url)
            analysis["platform"] = platform
            
            # 2. 获取平台信息
            platform_info = get_platform_info(url)
            analysis["platform_info"] = platform_info
            
            # 3. 检查API支持
            api_info = has_api_support(url)
            analysis["api_support"] = api_info
            
            # 4. 生成建议
            platform_name = platform_info.get("name", platform)
            logger.info(f"检测到平台: {platform_name}")
            
            # B站特定建议
            if platform == "bilibili":
                if api_info.get("has_api"):
                    analysis["recommendations"].append("✅ 使用B站API方案可绕过412反爬问题")
                    analysis["download_method"] = "B站API方案"
                    
                    # 获取视频信息估计时长
                    try:
                        from utils.bilibili_api import BilibiliAPI
                        api = BilibiliAPI()
                        bvid = api.extract_bvid(url)
                        if bvid:
                            video_info = api.get_video_info(bvid)
                            if video_info:
                                duration = video_info.get("duration", 0)
                                if duration > 0:
                                    mins = duration // 60
                                    secs = duration % 60
                                    analysis["estimated_duration"] = f"{mins}分{secs}秒 ({duration}秒)"
                                    analysis["video_title"] = video_info.get("title", "未知")[:50] + "..."
                    except:
                        pass
                else:
                    analysis["warnings"].append("⚠️  B站有412反爬风险，建议启用API支持 (--use-api)")
                    analysis["download_method"] = "yt-dlp（有412风险）"
            
            # YouTube建议
            elif platform == "youtube":
                analysis["recommendations"].append("✅ YouTube支持良好")
                analysis["download_method"] = "yt-dlp（需要cookies）"
            
            # 其他平台
            else:
                analysis["download_method"] = "yt-dlp"
            
            # 通用建议
            if self.args.audio_only:
                analysis["recommendations"].append("✅ 仅音频模式可节省带宽和处理时间")
                analysis["estimated_size"] = "较小（仅音频）"
            else:
                analysis["estimated_size"] = "较大（视频+音频）"
            
            return analysis
            
        except Exception as e:
            logger.error(f"URL分析失败: {e}")
            analysis["error"] = str(e)
            return analysis
    
    def process(self, url: str) -> dict:
        """处理单个视频URL"""
        result = {
            "success": False,
            "task_id": self.task_id,
            "url": url,
            "work_dir": str(self.work_dir),
            "steps": {},
            "errors": []
        }
        
        try:
            logger.info(f"开始处理视频: {url}")
            
            # 1. 分析URL
            analysis = self.analyze_url(url)
            result["analysis"] = analysis
            result["steps"]["analysis"] = {
                "status": "completed",
                "data": analysis
            }
            
            # 打印分析结果
            self._print_analysis(analysis)
            
            # 2. 下载视频/音频
            logger.info(f"开始下载，方法: {analysis.get('download_method', '未知')}")
            
            download_result = self.downloader.download_video(
                url=url,
                quality=self.args.quality,
                audio_only=self.args.audio_only
            )
            
            result["steps"]["download"] = {
                "status": "completed" if download_result.get("success") else "failed",
                "data": download_result
            }
            
            if not download_result.get("success"):
                error_msg = download_result.get("error", "未知错误")
                result["errors"].append(f"下载失败: {error_msg}")
                logger.error(f"下载失败: {error_msg}")
                
                # 尝试备用方案
                if analysis.get("platform") == "bilibili" and not self.args.use_api:
                    result["errors"].append("建议重试并启用API支持: --use-api")
                
                return result
            
            # 3. 提取音频（如果下载的是视频）
            audio_path = None
            if download_result.get("method") == "yt-dlp" and not self.args.audio_only:
                # 从下载的视频文件中提取音频
                files = download_result.get("files", [])
                if files:
                    video_path = Path(files[0])
                    logger.info(f"从视频提取音频: {video_path}")
                    
                    audio_path = extract_audio(
                        video_path=video_path,
                        url=url,
                        output_dir=self.work_dir,
                        audio_only=False
                    )
                    
                    if audio_path and audio_path.exists():
                        result["steps"]["audio_extraction"] = {
                            "status": "completed",
                            "file": str(audio_path)
                        }
                        logger.info(f"音频提取完成: {audio_path}")
                    else:
                        result["steps"]["audio_extraction"] = {"status": "failed"}
                        result["errors"].append("音频提取失败")
                        logger.error("音频提取失败")
                        return result
                else:
                    result["errors"].append("未找到下载的视频文件")
                    return result
            
            elif download_result.get("method") == "bilibili_api":
                # API方案需要特殊处理
                result["steps"]["audio_extraction"] = {
                    "status": "deferred",
                    "message": "B站API方案需要专用下载器获取音频"
                }
                logger.info("B站API方案需要专用处理，跳过音频提取")
                return self._handle_bilibili_api_result(download_result, result)
            
            # 4. 语音转文字
            if audio_path and audio_path.exists():
                logger.info(f"开始语音转文字: {audio_path}")
                
                transcript_path = transcribe_audio(
                    audio_path=audio_path,
                    output_dir=self.work_dir,
                    language=self.args.language,
                    model=self.args.model
                )
                
                if transcript_path and transcript_path.exists():
                    result["steps"]["speech_to_text"] = {
                        "status": "completed",
                        "file": str(transcript_path)
                    }
                    
                    # 读取转录文本
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        transcript_text = f.read()
                    
                    result["transcript_length"] = len(transcript_text)
                    logger.info(f"语音转文字完成: {transcript_path} ({len(transcript_text)}字符)")
                    
                    # 5. 智能总结
                    if transcript_text.strip() and not self.args.summary_only:
                        logger.info("开始智能总结")
                        
                        summary_path = summarize_text(
                            text=transcript_text,
                            output_dir=self.work_dir,
                            model=self.args.summary_model,
                            language=self.args.language,
                            style=self.args.summary_style
                        )
                        
                        if summary_path and summary_path.exists():
                            result["steps"]["summarization"] = {
                                "status": "completed",
                                "file": str(summary_path)
                            }
                            logger.info(f"智能总结完成: {summary_path}")
                        else:
                            result["steps"]["summarization"] = {"status": "failed"}
                            logger.warning("智能总结失败")
                else:
                    result["steps"]["speech_to_text"] = {"status": "failed"}
                    result["errors"].append("语音转文字失败")
                    logger.error("语音转文字失败")
            else:
                logger.warning("无音频文件可供转文字")
            
            # 6. 生成元数据和报告
            self._generate_metadata(result)
            self._generate_report(result)
            
            result["success"] = True
            result["completion_time"] = datetime.now().isoformat()
            
            logger.info(f"处理完成！结果保存在: {self.work_dir}")
            return result
            
        except Exception as e:
            logger.error(f"处理过程中发生错误: {e}", exc_info=True)
            result["errors"].append(str(e))
            return result
    
    def _handle_bilibili_api_result(self, download_result: dict, result: dict) -> dict:
        """处理B站API下载结果"""
        try:
            logger.info("处理B站API下载结果")
            
            # 保存API获取的信息
            api_info_path = self.work_dir / "bilibili_api_info.json"
            with open(api_info_path, 'w', encoding='utf-8') as f:
                json.dump(download_result, f, ensure_ascii=False, indent=2)
            
            result["steps"]["bilibili_api_info"] = {
                "status": "completed",
                "file": str(api_info_path)
            }
            
            # 生成API信息报告
            report_path = self.work_dir / "B站API_信息报告.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# B站API信息报告\n\n")
                f.write(f"## 视频信息\n")
                f.write(f"- BVID: {download_result.get('bvid', '未知')}\n")
                f.write(f"- 标题: {download_result.get('title', '未知')}\n")
                
                if download_result.get("download_info"):
                    download_info = download_result["download_info"]
                    f.write(f"\n## 下载信息\n")
                    f.write(f"- 获取方法: {download_result.get('method')}\n")
                    
                    if download_info.get("download_urls"):
                        f.write(f"\n### 可用下载地址 ({len(download_info['download_urls'])}个)\n")
                        for i, url_info in enumerate(download_info["download_urls"][:5]):
                            f.write(f"{i+1}. **{url_info.get('format', '未知')}**\n")
                            f.write(f"   - 地址: {url_info.get('url', '')[:80]}...\n")
                            if url_info.get('size'):
                                f.write(f"   - 大小: {url_info['size']:,} 字节\n")
                            f.write("\n")
                    
                    f.write(f"\n## 后续步骤\n")
                    f.write("1. 使用专用下载工具下载上述地址\n")
                    f.write("2. 下载后使用本工具处理本地文件\n")
                    f.write("3. 或等待工具更新支持B站直接下载\n")
            
            result["steps"]["bilibili_api_report"] = {
                "status": "completed",
                "file": str(report_path)
            }
            
            logger.info(f"B站API信息报告已生成: {report_path}")
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"处理B站API结果失败: {e}")
            result["errors"].append(f"B站API处理失败: {e}")
            return result
    
    def _print_analysis(self, analysis: dict):
        """打印URL分析结果"""
        print("\n" + "=" * 60)
        print("🔍 URL分析结果")
        print("=" * 60)
        
        platform_name = analysis.get("platform_info", {}).get("name", "未知")
        print(f"📺 平台: {platform_name}")
        
        if analysis.get("video_title"):
            print(f"📝 标题: {analysis['video_title']}")
        
        print(f"⏱️  预计时长: {analysis.get('estimated_duration', '未知')}")
        print(f"📦 预计大小: {analysis.get('estimated_size', '未知')}")
        print(f"⬇️  下载方法: {analysis.get('download_method', '未知')}")
        
        # 建议
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            print("\n✅ 建议:")
            for rec in recommendations:
                print(f"  • {rec}")
        
        # 警告
        warnings = analysis.get("warnings", [])
        if warnings:
            print("\n⚠️  警告:")
            for warn in warnings:
                print(f"  • {warn}")
        
        print("=" * 60 + "\n")
    
    def _generate_metadata(self, result: dict):
        """生成处理元数据"""
        metadata = {
            "task_id": self.task_id,
            "url": result.get("url"),
            "timestamp": datetime.now().isoformat(),
            "args": vars(self.args) if hasattr(self.args, '__dict__') else str(self.args),
            "result": result
        }
        
        metadata_path = self.work_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"元数据已保存: {metadata_path}")
        return metadata_path
    
    def _generate_report(self, result: dict):
        """生成处理报告"""
        report_path = self.work_dir / "处理报告.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 视频处理报告 v2\n\n")
            f.write(f"## 任务信息\n")
            f.write(f"- 任务ID: {self.task_id}\n")
            f.write(f"- 处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- 工作目录: {self.work_dir}\n")
            f.write(f"- 处理状态: {'✅ 成功' if result.get('success') else '❌ 失败'}\n\n")
            
            # URL信息
            f.write(f"## URL信息\n")
            f.write(f"- URL: {result.get('url', '未知')}\n")
            if result.get("analysis"):
                analysis = result["analysis"]
                f.write(f"- 平台: {analysis.get('platform_info', {}).get('name', '未知')}\n")
                if analysis.get("video_title"):
                    f.write(f"- 标题: {analysis['video_title']}\n")
            
            # 步骤状态
            f.write(f"\n## 处理步骤\n")
            steps = result.get("steps", {})
            for step_name, step_info in steps.items():
                status = step_info.get("status", "unknown")
                status_icon = "✅" if status == "completed" else "❌" if status == "failed" else "⚠️"
                f.write(f"- {step_name}: {status_icon} {status}\n")
            
            # 生成的文件
            files = list(self.work_dir.glob("*"))
            if files:
                f.write(f"\n## 生成文件\n")
                for file_path in sorted(files):
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        size_mb = size / (1024 * 1024)
                        f.write(f"- {file_path.name} ({size_mb:.2f} MB)\n")
            
            # 错误信息
            errors = result.get("errors", [])
            if errors:
                f.write(f"\n## 错误信息\n")
                for error in errors:
                    f.write(f"- {error}\n")
        
        logger.info(f"处理报告已生成: {report_path}")
        return report_path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='视频转文字总结工具 v2 - 支持B站API方案，绕过412反爬问题'
    )
    
    # 必需参数
    parser.add_argument('--url', required=True, help='视频URL')
    
    # 输出配置
    parser.add_argument('--output-dir', default='./output', help='输出目录')
    
    # API和下载配置
    parser.add_argument('--use-api', action='store_true', 
                       help='启用API方案（对B站等平台推荐）')
    parser.add_argument('--quality', default='720p',
                       choices=['480p', '720p', '1080p', 'best', 'audio'],
                       help='视频质量')
    parser.add_argument('--audio-only', action='store_true', 
                       help='仅处理音频（不下载视频）')
    
    # 识别配置
    parser.add_argument('--language', default='auto', 
                       help='语音识别语言 (zh, en, ja, ko, auto等)')
    parser.add_argument('--model', default='base',
                       choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v3'],
                       help='Whisper模型大小')
    
    # 总结配置
    parser.add_argument('--summary-only', action='store_true',
                       help='仅生成摘要，不进行语音转文字')
    parser.add_argument('--summary-model', default='gpt-3.5-turbo',
                       help='总结使用的模型')
    parser.add_argument('--summary-style', default='brief',
                       choices=['brief', 'detailed', 'academic', 'bullet'],
                       help='总结风格')
    
    # 调试选项
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--analyze-only', action='store_true',
                       help='仅分析URL，不实际处理')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    
    # 创建处理器
    processor = VideoToSummaryProcessorV2(args)
    
    # 如果仅分析，不处理
    if args.analyze_only:
        analysis = processor.analyze_url(args.url)
        print("\n" + "=" * 60)
        print("📊 URL分析完成（仅分析模式）")
        print("=" * 60)
        print(f"建议使用命令: python {sys.argv[0]} --url \"{args.url}\" --use-api")
        sys.exit(0)
    
    # 执行处理
    result = processor.process(args.url)
    
    # 输出结果
    print("\n" + "=" * 60)
    if result.get("success"):
        print("✅ 处理成功！")
        print(f"   任务ID: {result.get('task_id')}")
        print(f"   结果目录: {result.get('work_dir')}")
        print(f"   查看报告: {result.get('work_dir')}/处理报告.md")
        
        # 显示转录长度
        if result.get("transcript_length"):
            print(f"   转录文本: {result['transcript_length']} 字符")
        
        # B站API特殊提示
        if result.get("steps", {}).get("bilibili_api_report"):
            print(f"\n📋 B站API信息已保存，请查看: {result.get('work_dir')}/B站API_信息报告.md")
            print("   下载地址已获取，建议使用专用工具下载")
    else:
        print("❌ 处理失败")
        errors = result.get("errors", [])
        if errors:
            print(f"   错误信息:")
            for error in errors:
                print(f"   • {error}")
        
        # 提供建议
        print(f"\n💡 建议:")
        print(f"   1. 检查URL是否正确")
        print(f"   2. 对于B站视频，尝试: --use-api")
        print(f"   3. 检查网络连接")
        print(f"   4. 查看详细日志")
    
    print("=" * 60)
    
    sys.exit(0 if result.get("success") else 1)

if __name__ == '__main__':
    main()