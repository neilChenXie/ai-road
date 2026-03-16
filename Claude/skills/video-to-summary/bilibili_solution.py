#!/usr/bin/env python3
"""
B站412问题解决方案演示
"""

import subprocess
import json
import time

def test_bilibili_solutions():
    """测试多种B站412解决方案"""
    
    bilibili_url = "https://www.bilibili.com/video/BV12CA1zhEmK"
    
    print("🎯 B站412问题解决方案测试")
    print("=" * 60)
    print(f"目标视频: {bilibili_url}")
    print()
    
    solutions = [
        {
            "name": "方案1: 基本访问",
            "cmd": ["yt-dlp", "--dump-json", bilibili_url],
            "desc": "无任何header设置，通常会导致412错误"
        },
        {
            "name": "方案2: Referer设置",
            "cmd": ["yt-dlp", "--referer", "https://www.bilibili.com", "--dump-json", bilibili_url],
            "desc": "设置Referer头，部分情况下有效"
        },
        {
            "name": "方案3: 完整headers",
            "cmd": ["yt-dlp", 
                   "--referer", "https://www.bilibili.com",
                   "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                   "--add-header", "Accept-Language: zh-CN,zh;q=0.9",
                   "--add-header", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "--dump-json", bilibili_url],
            "desc": "模拟完整浏览器headers"
        },
        {
            "name": "方案4: Cookies方式 (推荐)",
            "cmd": ["yt-dlp", "--cookies-from-browser", "chrome", "--dump-json", bilibili_url],
            "desc": "使用浏览器cookies，最可能成功的方式"
        },
        {
            "name": "方案5: 使用代理",
            "cmd": ["yt-dlp", "--proxy", "http://proxy:port", "--dump-json", bilibili_url],
            "desc": "通过代理服务器访问"
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"{i}. {solution['name']}")
        print(f"   描述: {solution['desc']}")
        print(f"   命令: {' '.join(solution['cmd'])}")
        
        try:
            print("   测试中...", end="", flush=True)
            result = subprocess.run(
                solution["cmd"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # 尝试解析JSON
                try:
                    data = json.loads(result.stdout)
                    print(f" ✅ 成功!")
                    print(f"    标题: {data.get('title', '未知')[:40]}...")
                    print(f"    时长: {data.get('duration', 0)}秒")
                except json.JSONDecodeError:
                    print(f" ❓ 返回非JSON数据")
            else:
                error_msg = result.stderr.strip().split('\n')[-1]
                print(f" ❌ 失败: {error_msg[:60]}...")
                
        except subprocess.TimeoutExpired:
            print(" ⏱️  超时")
        except Exception as e:
            print(f" 💥 异常: {e}")
        
        print()
        time.sleep(1)  # 避免请求过快
    
    print("=" * 60)
    print("📋 解决方案总结:")
    print()
    print("⚠️  B站412问题的根本原因:")
    print("   • 反爬虫机制检测到自动化访问")
    print("   • 缺少正常浏览器的指纹信息")
    print("   • IP地址被限制")
    print()
    print("✅ 有效的解决方案:")
    print("   1. 使用浏览器cookies (--cookies-from-browser)")
    print("   2. 完整的headers模拟")
    print("   3. 更换IP地址或使用代理")
    print("   4. 降低请求频率")
    print()
    print("🔧 在我们的工具中如何实现:")
    print("   1. 已内置headers配置")
    print("   2. 支持cookies参数传递")
    print("   3. 有错误重试机制")
    print("   4. 支持代理配置")
    print()
    print("🚀 使用建议:")
    print("   对于B站视频，建议使用:")
    print("   python scripts/video_to_summary.py \\")
    print("     --url 'B站URL' \\")
    print("     --cookies-browser chrome \\")
    print("     --referer 'https://www.bilibili.com'")

def demonstrate_workaround():
    """演示临时解决方案"""
    
    print("\n🔄 临时解决方案演示")
    print("=" * 60)
    
    print("如果所有方法都失败，可以考虑:")
    print()
    print("1. 使用公开的B站API:")
    print("   https://api.bilibili.com/x/web-interface/view?bvid=BV12CA1zhEmK")
    print()
    print("2. 手动获取视频信息:")
    print("   ```python")
    print("   import requests")
    print("   url = 'https://api.bilibili.com/x/web-interface/view'")
    print("   params = {'bvid': 'BV12CA1zhEmK'}")
    print("   response = requests.get(url, params=params)")
    print("   data = response.json()")
    print("   ```")
    print()
    print("3. 使用第三方工具或服务:")
    print("   • Bilibili-Evolved (浏览器插件)")
    print("   • you-get (命令行工具)")
    print("   • Lux (原annie)")
    print()
    print("4. 在工具中添加B站API支持:")
    print("   - 通过API获取视频信息")
    print("   - 获取下载链接")
    print("   - 集成到现有流程中")

if __name__ == "__main__":
    test_bilibili_solutions()
    demonstrate_workaround()
    
    print("\n🎯 结论:")
    print("✅ 问题已识别: B站412反爬机制")
    print("✅ 解决方案已提供: cookies、headers、代理等")
    print("✅ 工具已支持: 所有解决方案都可配置")
    print("❌ 无法保证100%成功: 取决于B站的检测策略")
    print()
    print("📞 需要时，我可以:")
    print("   1. 添加B站API支持到工具中")
    print("   2. 实现更复杂的反反爬策略")
    print("   3. 测试其他视频平台的兼容性")