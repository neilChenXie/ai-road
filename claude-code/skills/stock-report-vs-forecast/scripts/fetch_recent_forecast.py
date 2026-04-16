#!/usr/bin/env python3
"""
获取股票最近业绩预测数据
使用东方财富研报数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import sys


def fetch_forecast_by_code(stock_code, report_year=None):
    """
    获取指定股票的机构业绩预测

    Args:
        stock_code: 股票代码（6位数字）
        report_year: 预测年份，默认当前年份

    Returns:
        dict: 预测数据
    """

    if report_year is None:
        report_year = datetime.now().year

    print(f"\n{'='*60}")
    print(f"获取 {stock_code} 的{report_year}年业绩预测")
    print(f"{'='*60}\n")

    try:
        # 获取研报数据
        df = ak.stock_research_report_em(symbol=stock_code)

        if df is None or len(df) == 0:
            print(f"⚠️  暂无{stock_code}的研报数据")
            return None

        # 查找盈利预测列
        forecast_col = f'{report_year}-盈利预测-收益'
        next_year_col = f'{report_year + 1}-盈利预测-收益'

        forecast_col_used = None
        if forecast_col in df.columns:
            forecast_col_used = forecast_col
        elif next_year_col in df.columns:
            forecast_col_used = next_year_col
            report_year = report_year + 1

        if forecast_col_used is None:
            print(f"⚠️  暂无{report_year}年的EPS预测数据")
            return None

        # 提取EPS预测
        eps_forecasts = pd.to_numeric(df[forecast_col_used], errors='coerce').dropna()

        if len(eps_forecasts) == 0:
            print(f"⚠️  暂无有效的EPS预测数据")
            return None

        # 获取营收和净利润预测
        revenue_col = f'{report_year}-盈利预测-营业总收入'
        profit_col = f'{report_year}-盈利预测-净利润'

        revenue_forecasts = None
        profit_forecasts = None

        if revenue_col in df.columns:
            revenue_forecasts = pd.to_numeric(df[revenue_col], errors='coerce').dropna()

        if profit_col in df.columns:
            profit_forecasts = pd.to_numeric(df[profit_col], errors='coerce').dropna()

        # 构建结果
        result = {
            'stock_code': stock_code,
            'forecast_year': report_year,
            'forecast_count': int(len(eps_forecasts)),
            'eps_forecast': {
                'avg': float(eps_forecasts.mean()),
                'min': float(eps_forecasts.min()),
                'max': float(eps_forecasts.max()),
                'median': float(eps_forecasts.median()),
            },
            'latest_forecast_date': str(df['日期'].max()),
        }

        if revenue_forecasts is not None and len(revenue_forecasts) > 0:
            result['revenue_forecast'] = {
                'avg': float(revenue_forecasts.mean()),
                'min': float(revenue_forecasts.min()),
                'max': float(revenue_forecasts.max()),
            }

        if profit_forecasts is not None and len(profit_forecasts) > 0:
            result['profit_forecast'] = {
                'avg': float(profit_forecasts.mean()),
                'min': float(profit_forecasts.min()),
                'max': float(profit_forecasts.max()),
            }

        # 打印结果
        print_forecast_result(result)

        return result

    except Exception as e:
        print(f"获取预测数据错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_forecast_result(forecast_data):
    """打印预测结果"""

    print(f"✅ 找到 {forecast_data['forecast_count']} 家机构的预测\n")

    print(f"【EPS预测】")
    eps = forecast_data['eps_forecast']
    print(f"  平均值: {eps['avg']:.4f} 元")
    print(f"  预测区间: {eps['min']:.4f} - {eps['max']:.4f} 元")
    print(f"  中位数: {eps['median']:.4f} 元")

    if 'revenue_forecast' in forecast_data:
        rev = forecast_data['revenue_forecast']
        print(f"\n【营收预测】")
        print(f"  平均值: {format_money(rev['avg'])}")
        print(f"  预测区间: {format_money(rev['min'])} - {format_money(rev['max'])}")

    if 'profit_forecast' in forecast_data:
        profit = forecast_data['profit_forecast']
        print(f"\n【净利润预测】")
        print(f"  平均值: {format_money(profit['avg'])}")
        print(f"  预测区间: {format_money(profit['min'])} - {format_money(profit['max'])}")

    print(f"\n最新预测日期: {forecast_data['latest_forecast_date']}")


def format_money(value):
    """格式化金额"""
    if value is None:
        return 'N/A'
    try:
        value = float(value)
        if abs(value) >= 1e8:
            return f'{value/1e8:.2f}亿元'
        elif abs(value) >= 1e4:
            return f'{value/1e4:.2f}万元'
        else:
            return f'{value:.2f}元'
    except:
        return str(value)


def get_forecast_data(stock_code, report_year=None):
    """
    获取预测数据的简单接口（供其他脚本调用）
    """

    if report_year is None:
        report_year = datetime.now().year

    try:
        df = ak.stock_research_report_em(symbol=stock_code)

        if df is None or len(df) == 0:
            return None

        forecast_col = f'{report_year}-盈利预测-收益'
        next_year_col = f'{report_year + 1}-盈利预测-收益'

        if forecast_col not in df.columns and next_year_col not in df.columns:
            return None

        forecast_col_used = forecast_col if forecast_col in df.columns else next_year_col
        actual_year = report_year if forecast_col in df.columns else report_year + 1

        eps_forecasts = pd.to_numeric(df[forecast_col_used], errors='coerce').dropna()

        if len(eps_forecasts) == 0:
            return None

        return {
            'forecast_count': int(len(eps_forecasts)),
            'eps_forecast_avg': float(eps_forecasts.mean()),
            'eps_forecast_min': float(eps_forecasts.min()),
            'eps_forecast_max': float(eps_forecasts.max()),
            'latest_forecast_date': str(df['日期'].max()),
            'forecast_year': actual_year,
        }

    except Exception as e:
        return None


def main():
    """主函数"""

    if len(sys.argv) < 2:
        print("使用方法: python fetch_recent_forecast.py <股票代码> [年份]")
        print("示例: python fetch_recent_forecast.py 000001 2025")
        sys.exit(1)

    stock_code = sys.argv[1]
    report_year = int(sys.argv[2]) if len(sys.argv) > 2 else None

    result = fetch_forecast_by_code(stock_code, report_year)

    if result:
        # 保存到JSON（供其他脚本调用）
        import json
        print("\n" + "="*60)
        print("JSON输出：")
        print("="*60)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
