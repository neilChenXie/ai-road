#!/usr/bin/env python3
"""
A股财报分析主程序
整合获取财报、获取预测、对比分析的全流程

用法:
    python main.py                    # 获取今天发布的财报并分析
    python main.py 20250401            # 获取指定日期的财报并分析
    python main.py --stock 000001      # 分析指定股票
    python main.py --stock 000001 2025 # 分析指定股票指定年份
"""

import sys
import json
from datetime import datetime

# 导入各模块
from fetch_today_reports import fetch_reports_by_date
from fetch_recent_forecast import get_forecast_data
from analyze_report_vs_forecast import (
    analyze_earnings_vs_forecast,
    get_actual_financial_data,
    compare_actual_vs_forecast
)


def analyze_reports_for_date(date=None):
    """
    分析指定日期发布的所有财报

    Args:
        date: 日期字符串，格式 YYYYMMDD 或 YYYY-MM-DD，默认今天
    """

    # 处理日期格式
    if date is None:
        date = datetime.now().strftime('%Y%m%d')
    else:
        date = date.replace('-', '')

    display_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

    print(f"\n{'#'*70}")
    print(f"# {display_date} 财报分析")
    print(f"{'#'*70}\n")

    # 第一步：获取当天发布财报的公司
    print("[步骤1] 获取当天发布财报的公司...")
    reports_df = fetch_reports_by_date(date)

    if reports_df is None or len(reports_df) == 0:
        print(f"\n❌ {display_date} 没有公司发布财报\n")
        return

    print(f"\n✓ 找到 {len(reports_df)} 家公司发布财报\n")

    # 第二步：逐个获取预测数据并分析
    print("[步骤2] 分析每只股票的预期对比...\n")

    results = []

    for idx, row in reports_df.iterrows():
        stock_code = row['股票代码']
        stock_name = row['股票简称']

        print(f"{'='*60}")
        print(f"分析: {stock_code} {stock_name}")
        print(f"{'='*60}")

        # 获取预测数据
        forecast_data = get_forecast_data(stock_code)

        # 获取实际财报数据
        actual_data = get_actual_financial_data(stock_code)

        if not actual_data:
            print(f"  ⚠️  无法获取财报数据，跳过\n")
            continue

        # 进行对比分析
        if forecast_data and forecast_data.get('forecast_count', 0) > 0:
            comparison = compare_actual_vs_forecast(actual_data, forecast_data)

            results.append({
                'stock_code': stock_code,
                'stock_name': stock_name,
                'judgment': comparison['judgment'],
                'actual': actual_data,
                'forecast': forecast_data,
            })

            # 打印简要结果
            print(f"  报告期: {actual_data.get('report_date')}")
            print(f"  EPS: {actual_data.get('eps')} vs 预测 {forecast_data.get('eps_forecast_avg')}")
            print(f"  判断: {comparison['judgment']}\n")
        else:
            print(f"  ⚠️  暂无机构预测数据，仅记录实际数据\n")
            results.append({
                'stock_code': stock_code,
                'stock_name': stock_name,
                'judgment': '无预测',
                'actual': actual_data,
                'forecast': None,
            })

    # 第三步：汇总结果
    print(f"\n{'#'*70}")
    print(f"# 汇总分析结果")
    print(f"{'#'*70}\n")

    # 统计
    judgments = {}
    for r in results:
        j = r['judgment']
        judgments[j] = judgments.get(j, 0) + 1

    print("统计:")
    for j, count in judgments.items():
        emoji = {'超预期': '📈', '符合预期': '✅', '不及预期': '📉', '无预测': '❓'}.get(j, '')
        print(f"  {emoji} {j}: {count} 家")

    # 打印超预期和不及预期的公司
    print("\n【超预期】")
    for r in results:
        if r['judgment'] == '超预期':
            actual = r['actual']
            forecast = r['forecast']
            diff = ((actual['eps'] - forecast['eps_forecast_avg']) / abs(forecast['eps_forecast_avg'])) * 100
            print(f"  {r['stock_code']} {r['stock_name']}: EPS {actual['eps']:.4f} vs 预测 {forecast['eps_forecast_avg']:.4f} ({diff:+.1f}%)")

    print("\n【不及预期】")
    for r in results:
        if r['judgment'] == '不及预期':
            actual = r['actual']
            forecast = r['forecast']
            diff = ((actual['eps'] - forecast['eps_forecast_avg']) / abs(forecast['eps_forecast_avg'])) * 100
            print(f"  {r['stock_code']} {r['stock_name']}: EPS {actual['eps']:.4f} vs 预测 {forecast['eps_forecast_avg']:.4f} ({diff:+.1f}%)")

    print(f"\n{'#'*70}\n")

    # 保存结果到JSON
    output_file = f"analysis_{date}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"✓ 结果已保存到: {output_file}\n")


def analyze_single_stock(stock_code, report_year=None):
    """
    分析单只股票

    Args:
        stock_code: 股票代码
        report_year: 报告年份
    """

    print(f"\n{'#'*70}")
    print(f"# 股票分析: {stock_code}")
    print(f"{'#'*70}\n")

    result = analyze_earnings_vs_forecast(stock_code, report_year)

    if result:
        # 保存到JSON
        output_file = f"analysis_{stock_code}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n✓ 结果已保存到: {output_file}\n")


def get_actual_financial_data(stock_code):
    """获取实际财报数据的包装函数"""
    from analyze_report_vs_forecast import get_actual_financial_data as _get_data
    return _get_data(stock_code)


def main():
    """主函数入口"""

    if len(sys.argv) < 2:
        # 默认获取今天的数据
        analyze_reports_for_date()
        return

    # 解析命令行参数
    if sys.argv[1] == '--stock':
        # 分析指定股票
        if len(sys.argv) < 3:
            print("错误: 请提供股票代码")
            print("用法: python main.py --stock <股票代码> [年份]")
            sys.exit(1)

        stock_code = sys.argv[2]
        report_year = int(sys.argv[3]) if len(sys.argv) > 3 else None
        analyze_single_stock(stock_code, report_year)

    elif sys.argv[1].startswith('--'):
        print(f"未知参数: {sys.argv[1]}")
        print("用法:")
        print("  python main.py                    # 分析今天发布的财报")
        print("  python main.py 20250401           # 分析指定日期发布的财报")
        print("  python main.py --stock 000001     # 分析指定股票")
        print("  python main.py --stock 000001 2025 # 分析指定股票指定年份")
        sys.exit(1)

    else:
        # 视为日期参数
        date = sys.argv[1]
        analyze_reports_for_date(date)


if __name__ == '__main__':
    main()
