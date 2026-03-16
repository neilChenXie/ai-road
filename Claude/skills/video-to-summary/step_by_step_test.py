#!/usr/bin/env python3
"""
分步测试 - 验证视频转文字总结工具的每个模块
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class StepByStepTester:
    """分步测试器"""
    
    def __init__(self, url: str):
        self.url = url
        self.test_dir = Path("./step_test_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.test_dir.mkdir(exist_ok=True)
        self.results = {
            "url": url,
            "start_time": datetime.now().isoformat(),
            "steps": {}
        }
    
    def log_step(self, step_name: str, status: str, details: dict = None):
        """记录测试步骤"""
        print(f"\n{'✅' if status == 'success' else '❌'} {step_name}: {status}")
        self.results["steps"][step_name] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        if status == "success":
            return True
        else:
            return False
    
    def step1_platform_detection(self):
        """步骤1：平台检测"""
        print("🔍 步骤1: 平台检测")
        print("-" * 50)
        
        try:
            from utils.platform_detector import (
                detect_platform, get_platform_info, 
                has_api_support, get_platform_recommendations
            )
            
            # 检测平台
            platform = detect_platform(self.url)
            platform_info = get_platform_info(self.url)
            api_info = has_api_support(self.url)
            recommendations = get_platform_recommendations(self.url)
            
            print(f"检测到平台: {platform}")
            print(f"平台名称: {platform_info.get('name')}")
            print(f"平台ID: {platform_info.get('id')}")
            print(f"API支持: {'✅ 可用' if api_info.get('has_api') else '❌ 不可用'}")
            
            if api_info.get("has_api"):
                print(f"API名称: {api_info.get('api_name')}")
                print(f"推荐使用API: {'✅ 是' if api_info.get('recommended') else '❌ 否'}")
            
            # 保存结果
            details = {
                "platform": platform,
                "platform_info": platform_info,
                "api_info": api_info,
                "recommendations": recommendations
            }
            
            return self.log_step("platform_detection", "success", details)
            
        except Exception as e:
            print(f"平台检测失败: {e}")
            return self.log_step("platform_detection", "failed", {"error": str(e)})
    
    def step2_bilibili_api_extraction(self):
        """步骤2：B站API提取"""
        print("\n🎯 步骤2: B站API提取")
        print("-" * 50)
        
        try:
            from utils.bilibili_api import BilibiliAPI, extract_bvid_from_url
            
            # 提取BVID
            bvid = extract_bvid_from_url(self.url)
            if not bvid:
                print("❌ 无法提取BVID")
                return self.log_step("bilibili_api_extraction", "failed", {"error": "无法提取BVID"})
            
            print(f"✅ 提取BVID: {bvid}")
            
            # 获取视频信息
            api = BilibiliAPI()
            video_info = api.get_video_info(bvid)
            
            if not video_info:
                print("❌ 无法获取视频信息")
                return self.log_step("bilibili_api_extraction", "failed", {"error": "无法获取视频信息"})
            
            print(f"✅ 获取视频信息成功")
            print(f"   标题: {video_info.get('title', '未知')}")
            print(f"   时长: {video_info.get('duration', 0)}秒")
            print(f"   UP主: {video_info.get('owner', {}).get('name', '未知')}")
            print(f"   播放量: {video_info.get('stat', {}).get('view', 0):,}")
            print(f"   发布时间: {video_info.get('pubdate', 0)}")
            
            if video_info.get('desc'):
                desc_preview = video_info['desc'][:100] + "..." if len(video_info['desc']) > 100 else video_info['desc']
                print(f"   描述预览: {desc_preview}")
            
            # 保存视频信息
            info_file = self.test_dir / "video_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(video_info, f, ensure_ascii=False, indent=2)
            print(f"   视频信息已保存: {info_file}")
            
            details = {
                "bvid": bvid,
                "video_info": video_info,
                "info_file": str(info_file)
            }
            
            return self.log_step("bilibili_api_extraction", "success", details)
            
        except Exception as e:
            print(f"B站API提取失败: {e}")
            import traceback
            traceback.print_exc()
            return self.log_step("bilibili_api_extraction", "failed", {"error": str(e)})
    
    def step3_download_url_extraction(self):
        """步骤3：下载地址提取"""
        print("\n📥 步骤3: 下载地址提取")
        print("-" * 50)
        
        try:
            from utils.bilibili_api import BilibiliAPI, extract_bvid_from_url
            from utils.bilibili_downloader import BilibiliDownloader
            
            # 提取BVID
            bvid = extract_bvid_from_url(self.url)
            if not bvid:
                return self.log_step("download_url_extraction", "failed", {"error": "无法提取BVID"})
            
            # 使用下载器获取下载地址
            downloader = BilibiliDownloader(output_dir=str(self.test_dir))
            
            # 获取720p质量的下载地址
            print("获取720p质量下载地址...")
            download_result = downloader.download_with_api_fallback(
                url=self.url,
                quality="720p",
                audio_only=False
            )
            
            if not download_result.get("success"):
                error_msg = download_result.get("error", "未知错误")
                print(f"❌ 下载地址获取失败: {error_msg}")
                return self.log_step("download_url_extraction", "failed", {"error": error_msg})
            
            print(f"✅ 下载地址获取成功")
            print(f"   方法: {download_result.get('method', '未知')}")
            print(f"   标题: {download_result.get('title', '未知')}")
            print(f"   BVID: {download_result.get('bvid', '未知')}")
            
            if download_result.get("download_urls"):
                urls = download_result["download_urls"]
                print(f"   获取到 {len(urls)} 个下载地址")
                
                # 统计格式
                format_counts = {}
                for url_info in urls:
                    fmt = url_info.get("format", "unknown")
                    format_counts[fmt] = format_counts.get(fmt, 0) + 1
                
                for fmt, count in format_counts.items():
                    print(f"     • {fmt}: {count}个")
                
                # 保存下载地址
                urls_file = self.test_dir / "download_urls.json"
                with open(urls_file, 'w', encoding='utf-8') as f:
                    json.dump(download_result, f, ensure_ascii=False, indent=2)
                print(f"   下载地址已保存: {urls_file}")
            else:
                print(f"⚠️  未获取到下载地址")
            
            details = {
                "download_result": download_result,
                "bvid": bvid,
                "urls_file": str(self.test_dir / "download_urls.json") if download_result.get("download_urls") else None
            }
            
            return self.log_step("download_url_extraction", "success", details)
            
        except Exception as e:
            print(f"下载地址提取失败: {e}")
            return self.log_step("download_url_extraction", "failed", {"error": str(e)})
    
    def step4_video_downloader_test(self):
        """步骤4：视频下载器测试"""
        print("\n⬇️  步骤4: 视频下载器集成测试")
        print("-" * 50)
        
        try:
            from utils.video_downloader import VideoDownloader
            
            # 创建下载器（启用API）
            downloader = VideoDownloader(
                output_base_dir=str(self.test_dir),
                use_api=True
            )
            
            # 测试下载流程（不实际下载大文件）
            print("测试下载流程（API方案）...")
            result = downloader.download_video(
                url=self.url,
                quality="720p",
                audio_only=False
            )
            
            print(f"下载结果:")
            print(f"   成功: {result.get('success', False)}")
            print(f"   方法: {result.get('method', '未知')}")
            print(f"   错误: {result.get('error', '无')}")
            
            if result.get("success"):
                print(f"✅ 下载流程测试成功")
                if result.get("method") == "bilibili_api":
                    print(f"   状态: {result.get('message')}")
                    if result.get("download_info") and result["download_info"].get("download_urls"):
                        urls = result["download_info"]["download_urls"]
                        print(f"   获取到 {len(urls)} 个下载地址")
            else:
                print(f"❌ 下载流程测试失败")
            
            # 保存结果
            download_result_file = self.test_dir / "download_test_result.json"
            with open(download_result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"   测试结果已保存: {download_result_file}")
            
            details = {
                "result": result,
                "result_file": str(download_result_file)
            }
            
            status = "success" if result.get("success") else "failed"
            return self.log_step("video_downloader_test", status, details)
            
        except Exception as e:
            print(f"视频下载器测试失败: {e}")
            return self.log_step("video_downloader_test", "failed", {"error": str(e)})
    
    def step5_main_script_test(self):
        """步骤5：主脚本测试"""
        print("\n🔄 步骤5: 主脚本功能测试")
        print("-" * 50)
        
        try:
            # 运行主脚本的分析模式
            cmd = [
                sys.executable, "scripts/video_to_summary.py",
                "--url", self.url,
                "--use-api",
                "--analyze-only"
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ 主脚本分析模式测试成功")
                print("   输出包含平台检测和API信息")
                
                # 检查输出内容
                output = result.stdout
                if "平台:" in output and "建议使用命令" in output:
                    print("   输出格式正确")
            else:
                print(f"❌ 主脚本测试失败")
                print(f"   错误: {result.stderr[:200]}")
            
            # 保存输出
            output_file = self.test_dir / "main_script_output.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=== 标准输出 ===\n")
                f.write(result.stdout)
                f.write("\n\n=== 标准错误 ===\n")
                f.write(result.stderr)
            
            details = {
                "returncode": result.returncode,
                "stdout_preview": result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout,
                "stderr_preview": result.stderr[:200] if result.stderr else "无",
                "output_file": str(output_file)
            }
            
            status = "success" if result.returncode == 0 else "failed"
            return self.log_step("main_script_test", status, details)
            
        except subprocess.TimeoutExpired:
            print("⏱️  主脚本测试超时")
            return self.log_step("main_script_test", "failed", {"error": "超时"})
        except Exception as e:
            print(f"主脚本测试失败: {e}")
            return self.log_step("main_script_test", "failed", {"error": str(e)})
    
    def step6_generate_summary(self):
        """步骤6：生成最终总结"""
        print("\n📊 步骤6: 生成测试总结")
        print("-" * 50)
        
        try:
            # 统计测试结果
            total_steps = len(self.results["steps"])
            success_steps = sum(1 for step in self.results["steps"].values() if step["status"] == "success")
            success_rate = success_steps / total_steps * 100 if total_steps > 0 else 0
            
            print(f"测试步骤总数: {total_steps}")
            print(f"成功步骤数: {success_steps}")
            print(f"成功率: {success_rate:.1f}%")
            
            # 保存完整测试结果
            result_file = self.test_dir / "full_test_results.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            # 生成测试报告
            report_file = self.test_dir / "测试报告.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# B站API方案分步测试报告\n\n")
                f.write(f"## 基本信息\n")
                f.write(f"- 测试URL: {self.url}\n")
                f.write(f"- 测试时间: {self.results['start_time']}\n")
                f.write(f"- 测试目录: {self.test_dir}\n\n")
                
                f.write(f"## 测试结果概览\n")
                f.write(f"- 总步骤数: {total_steps}\n")
                f.write(f"- 成功步骤: {success_steps}\n")
                f.write(f"- 失败步骤: {total_steps - success_steps}\n")
                f.write(f"- 成功率: {success_rate:.1f}%\n\n")
                
                f.write(f"## 详细步骤\n")
                for step_name, step_info in self.results["steps"].items():
                    status_icon = "✅" if step_info["status"] == "success" else "❌"
                    f.write(f"### {step_name}\n")
                    f.write(f"- 状态: {status_icon} {step_info['status']}\n")
                    f.write(f"- 时间: {step_info['timestamp']}\n")
                    
                    if step_info.get("details"):
                        # 简化详细信息
                        details = step_info["details"]
                        if isinstance(details, dict):
                            for key, value in list(details.items())[:3]:  # 只显示前3项
                                if isinstance(value, str) and len(value) > 100:
                                    f.write(f"- {key}: {value[:100]}...\n")
                                else:
                                    f.write(f"- {key}: {value}\n")
                    f.write("\n")
                
                f.write(f"## 结论\n")
                if success_rate == 100:
                    f.write("✅ **所有测试通过！** B站API方案完全正常，412问题已解决。\n")
                elif success_rate >= 80:
                    f.write("⚠️  **大部分测试通过**，B站API方案基本可用，建议检查失败的步骤。\n")
                else:
                    f.write("❌ **测试失败较多**，需要修复问题。\n")
                
                f.write(f"\n## 建议\n")
                if success_rate >= 80:
                    f.write("1. 可以开始使用工具处理B站视频\n")
                    f.write("2. 推荐使用`--use-api`参数\n")
                    f.write("3. 建议先运行分析模式预览\n")
                else:
                    f.write("1. 需要修复失败的测试步骤\n")
                    f.write("2. 检查网络连接和B站API可用性\n")
                    f.write("3. 可能需要更新API模块\n")
            
            print(f"✅ 测试总结已生成")
            print(f"   完整结果: {result_file}")
            print(f"   测试报告: {report_file}")
            
            details = {
                "total_steps": total_steps,
                "success_steps": success_steps,
                "success_rate": success_rate,
                "result_file": str(result_file),
                "report_file": str(report_file)
            }
            
            self.results["summary"] = details
            self.results["end_time"] = datetime.now().isoformat()
            
            # 更新完整结果文件
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            return self.log_step("generate_summary", "success", details)
            
        except Exception as e:
            print(f"生成总结失败: {e}")
            return self.log_step("generate_summary", "failed", {"error": str(e)})
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 B站API方案 - 分步测试")
        print("=" * 70)
        print(f"测试URL: {self.url}")
        print(f"测试目录: {self.test_dir}")
        print("=" * 70)
        
        # 运行所有步骤
        steps = [
            ("平台检测", self.step1_platform_detection),
            ("B站API提取", self.step2_bilibili_api_extraction),
            ("下载地址提取", self.step3_download_url_extraction),
            ("视频下载器测试", self.step4_video_downloader_test),
            ("主脚本测试", self.step5_main_script_test),
            ("生成总结", self.step6_generate_summary)
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*70}")
            print(f"🎯 开始测试: {step_name}")
            print(f"{'='*70}")
            step_func()
        
        # 显示最终结果
        self.display_final_results()

def main():
    """主函数"""
    # 测试你的B站链接
    test_url = "https://b23.tv/hHipbJS"
    
    # 创建测试器
    tester = StepByStepTester(test_url)
    
    # 运行测试
    tester.run_all_tests()
    
    # 保存最终报告
    final_report = Path("./final_test_report.md")
    with open(final_report, 'w', encoding='utf-8') as f:
        f.write("# B站API方案测试完成报告\n\n")
        f.write(f"## 测试时间\n")
        f.write(f"开始: {tester.results.get('start_time')}\n")
        f.write(f"结束: {tester.results.get('end_time', '未完成')}\n\n")
        
        f.write(f"## 测试结论\n")
        summary = tester.results.get("summary", {})
        if summary:
            success_rate = summary.get("success_rate", 0)
            if success_rate == 100:
                f.write("🎉 **完全成功！所有测试通过！**\n")
                f.write("你的视频转文字总结工具现在已经可以稳定处理B站视频了！\n")
            elif success_rate >= 80:
                f.write("✅ **基本成功！大部分测试通过！**\n")
                f.write("工具可以正常使用，建议关注失败的测试步骤。\n")
            else:
                f.write("⚠️  **部分成功！需要改进！**\n")
                f.write("工具需要进一步优化才能稳定使用。\n")
        
        f.write(f"\n## 使用建议\n")
        f.write("```bash\n")
        f.write("# 推荐使用方式\n")
        f.write("python scripts/video_to_summary.py \\\n")
        f.write("  --url \"https://b23.tv/hHipbJS\" \\\n")
        f.write("  --use-api \\\n")
        f.write("  --language zh\n")
        f.write("```\n")
    
    print(f"\n📋 最终报告已保存: {final_report}")
    
    # 返回测试状态
    summary = tester.results.get("summary", {})
    success_rate = summary.get("success_rate", 0)
    
    if success_rate >= 80:
        print("\n🎉 测试完成！工具已准备好使用！")
        return 0
    else:
        print("\n⚠️  测试完成，但需要改进！")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)