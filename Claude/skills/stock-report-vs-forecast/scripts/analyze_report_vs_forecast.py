#!/usr/bin/env python3
"""
A股财报预期对比分析
对比财报实际数据与机构预测数据，判断是否符合预期
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import sys


def analyze_earnings_vs_forecast(stock_code, report_year=None):
    """
    分析财报数据与机构预测的对比

    Args:
        stock_code: 股票代码（6位数字）
        report_year: 报告年份，默认最新

    Returns:
        dict: 包含实际数据、预测数据和对比结果
    """

    print(f"\n{'='*60}")
    print(f"分析 {stock_code} 财报预期对比")
    print(f"{'='*60}\n")

    # 第一步：获取实际财报数据
    print("[1/3] 获取实际财报数据...")
    actual_data = get_actual_financial_data(stock_code)

    if not actual_data:
        print(f"❌ 无法获取 {stock_code} 的财报数据")
        return None

    print(f"✓ 获取到 {actual_data['report_date']} 的财报数据")

    # 第二步：获取机构预测数据
    print("\n[2/3] 获取机构预测数据...")
    forecast_data = get_forecast_data(stock_code, report_year)

    if not forecast_data or forecast_data.get('forecast_count', 0) == 0:
        print(f"⚠️  该股票暂无机构预测数据")
        forecast_data = {'forecast_count': 0}

    # 第三步：对比分析
    print("\n[3/3] 进行预期对比分析...")
    comparison = compare_actual_vs_forecast(actual_data, forecast_data)

    # 打印结果
    print_comparison_result(comparison)

    return comparison


def get_actual_financial_data(stock_code):
    """
    获取实际财报数据

    使用财务摘要接口获取最新发布的财报数据
    """

    try:
        # 获取财务摘要
        df = ak.stock_financial_abstract(symbol=stock_code)

        if df is None or len(df) == 0:
            return None

        # 转置数据
        df_transposed = df.set_index('指标').T

        # 移除"选项"行
        if '选项' in df_transposed.index:
            df_transposed = df_transposed.drop('选项')

        # 获取最新一期数据（最近发布的财报）
        latest_period = df_transposed.index[0]
        row = df_transposed.loc[latest_period]

        # 提取关键指标
        def safe_float(value):
            if value is None:
                return None
            try:
                if isinstance(value, pd.Series):
                    value = value.iloc[0] if len(value) > 0 else None
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    return None
                if isinstance(value, str):
                    if value == '' or value == '-':
                        return None
                    value = value.replace('%', '').replace(',', '')
                return float(value)
            except:
                return None

        actual_data = {
            'stock_code': stock_code,
            'report_date': latest_period,
            'eps': safe_float(row.get('基本每股收益', row.get('每股收益'))),
            'revenue': safe_float(row.get('营业总收入', row.get('营业收入'))),
            'net_profit': safe_float(row.get('净利润')),
            'roe': safe_float(row.get('净资产收益率(ROE)', row.get('净资产收益率'))),
            'gross_margin': safe_float(row.get('毛利率', row.get('销售毛利率'))),
        }

        # 计算同比增长率
        periods = df_transposed.index.tolist()
        if len(periods) > 4:
            last_year_row = df_transposed.iloc[4]

            if actual_data['revenue'] and safe_float(last_year_row.get('营业总收入', last_year_row.get('营业收入'))):
                last_revenue = safe_float(last_year_row.get('营业总收入', last_year_row.get('营业收入')))
                if last_revenue and last_revenue != 0:
                    actual_data['revenue_growth'] = ((actual_data['revenue'] - last_revenue) / abs(last_revenue)) * 100

            if actual_data['net_profit'] and safe_float(last_year_row.get('净利润')):
                last_profit = safe_float(last_year_row.get('净利润'))
                if last_profit and last_profit != 0:
                    actual_data['profit_growth'] = ((actual_data['net_profit'] - last_profit) / abs(last_profit)) * 100

        return actual_data

    except Exception as e:
        print(f"获取财报数据错误: {e}")
        return None


def get_forecast_data(stock_code, report_year=None):
    """
    获取机构预测数据

    Args:
        stock_code: 股票代码
        report_year: 预测年份，默认当前年份

    Returns:
        dict: 预测数据
    """

    if report_year is None:
        report_year = datetime.now().year

    try:
        # 获取研报数据
        df = ak.stock_research_report_em(symbol=stock_code)

        if df is None or len(df) == 0:
            return None

        # 查找盈利预测列
        forecast_col = f'{report_year}-盈利预测-收益'
        next_year_col = f'{report_year + 1}-盈利预测-收益'

        forecast_col_used = None
        actual_year = report_year

        if forecast_col in df.columns:
            forecast_col_used = forecast_col
        elif next_year_col in df.columns:
            forecast_col_used = next_year_col
            actual_year = report_year + 1

        if forecast_col_used is None:
            return None

        eps_forecasts = pd.to_numeric(df[forecast_col_used], errors='coerce').dropna()

        if len(eps_forecasts) == 0:
            return None

        return {
            'forecast_count': int(len(eps_forecasts)),
            'forecast_year': actual_year,
            'eps_forecast_avg': float(eps_forecasts.mean()),
            'eps_forecast_min': float(eps_forecasts.min()),
            'eps_forecast_max': float(eps_forecasts.max()),
            'latest_forecast_date': str(df['日期'].max()),
        }

    except Exception as e:
        print(f"获取机构预测错误: {e}")
        return None


def compare_actual_vs_forecast(actual_data, forecast_data):
    """
    对比实际数据与预测数据

    Args:
        actual_data: 实际财报数据
        forecast_data: 机构预测数据

    Returns:
        dict: 对比结果
    """

    result = {
        'stock_code': actual_data.get('stock_code'),
        'report_date': actual_data.get('report_date'),
        'actual': actual_data,
        'forecast': forecast_data,
        'comparison': {},
        'judgment': '数据不足'
    }

    # EPS对比
    actual_eps = actual_data.get('eps')
    forecast_eps = forecast_data.get('eps_forecast_avg')

    if actual_eps is not None and forecast_eps is not None and forecast_eps != 0:
        eps_diff_rate = ((actual_eps - forecast_eps) / abs(forecast_eps)) * 100

        result['comparison']['eps'] = {
            'actual': actual_eps,
            'forecast': forecast_eps,
            'diff_rate': eps_diff_rate,
            'judgment': get_judgment(eps_diff_rate)
        }

    # 综合判断
    if result['comparison']:
        judgments = [c['judgment'] for c in result['comparison'].values()]

        if '超预期' in judgments:
            result['judgment'] = '超预期'
        elif '不及预期' in judgments:
            result['judgment'] = '不及预期'
        else:
            result['judgment'] = '符合预期'

    return result


def get_judgment(diff_rate, threshold=5.0):
    """根据差异率判断预期"""
    if diff_rate > threshold:
        return '超预期'
    elif diff_rate < -threshold:
        return '不及预期'
    else:
        return '符合预期'


def print_comparison_result(comparison):
    """打印对比结果"""

    print(f"\n{'='*60}")
    print("财报预期对比分析结果")
    print(f"{'='*60}\n")

    # 基本信息
    print(f"股票代码: {comparison['stock_code']}")
    print(f"报告期: {comparison['report_date']}")
    print(f"\n综合判断: {get_judgment_emoji(comparison['judgment'])} {comparison['judgment']}")

    # 实际数据
    actual = comparison['actual']
    print(f"\n【实际财报数据】")
    print(f"  每股收益(EPS): {format_number(actual.get('eps'))} 元")
    print(f"  营业收入: {format_number(actual.get('revenue'), is_yuan=True)}")
    print(f"  净利润: {format_number(actual.get('net_profit'), is_yuan=True)}")
    print(f"  净利润同比增长: {format_percent(actual.get('profit_growth'))}")
    print(f"  净资产收益率(ROE): {format_percent(actual.get('roe'))}")

    # 预测数据
    forecast = comparison['forecast']
    if forecast.get('forecast_count', 0) > 0:
        print(f"\n【机构预测数据】")
        print(f"  预测年份: {forecast.get('forecast_year', 'N/A')}")
        print(f"  预测机构数: {forecast['forecast_count']} 家")
        print(f"  EPS预测均值: {forecast.get('eps_forecast_avg', 0):.4f} 元")
        print(f"  EPS预测区间: {forecast.get('eps_forecast_min', 0):.4f} - {forecast.get('eps_forecast_max', 0):.4f} 元")
        print(f"  最新预测日期: {forecast.get('latest_forecast_date', 'N/A')}")

    # 对比结果
    if comparison['comparison']:
        print(f"\n【预期对比】")
        for metric, data in comparison['comparison'].items():
            print(f"  {metric.upper()}:")
            print(f"    实际值: {data['actual']:.4f}")
            print(f"    预测值: {data['forecast']:.4f}")
            print(f"    差异率: {data['diff_rate']:+.2f}%")
            print(f"    判断: {get_judgment_emoji(data['judgment'])} {data['judgment']}")

    print(f"\n{'='*60}\n")


def get_judgment_emoji(judgment):
    """获取判断的emoji"""
    return {
        '超预期': '📈',
        '符合预期': '✅',
        '不及预期': '📉',
        '数据不足': '❓'
    }.get(judgment, '')


def format_number(value, is_yuan=False):
    """格式化数字"""
    if value is None:
        return 'N/A'

    try:
        value = float(value)
        if is_yuan:
            if abs(value) >= 1e8:
                return f'{value/1e8:.2f}亿元'
            elif abs(value) >= 1e4:
                return f'{value/1e4:.2f}万元'
            else:
                return f'{value:.2f}元'
        else:
            return f'{value:.4f}'
    except:
        return str(value)


def format_percent(value):
    """格式化百分比"""
    if value is None:
        return 'N/A'
    return f'{value:.2f}%'


def analyze_single_stock(stock_code, report_year=None):
    """
    分析单只股票的函数接口（供main.py调用）

    Args:
        stock_code: 股票代码
        report_year: 报告年份

    Returns:
        dict: 分析结果
    """
    return analyze_earnings_vs_forecast(stock_code, report_year)


def main():
    """主函数"""

    if len(sys.argv) < 2:
        print("使用方法: python analyze_report_vs_forecast.py <股票代码> [年份]")
        print("示例: python analyze_report_vs_forecast.py 000001 2025")
        sys.exit(1)

    stock_code = sys.argv[1]
    report_year = int(sys.argv[2]) if len(sys.argv) > 2 else None

    # 执行分析
    result = analyze_earnings_vs_forecast(stock_code, report_year)

    # 返回JSON格式（供其他脚本调用）
    if result:
        import json
        print("\n" + "="*60)
        print("JSON输出：")
        print("="*60)
        # 转换不可JSON序列化的数据
        output = {
            'stock_code': result['stock_code'],
            'report_date': result['report_date'],
            'judgment': result['judgment'],
            'actual': result['actual'],
            'forecast': result['forecast'],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
