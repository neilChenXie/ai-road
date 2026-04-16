#!/usr/bin/env python3
"""
获取指定日期发布财报的A股公司清单（实时版）
使用东方财富公告接口
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import sys


def fetch_reports_by_date(date=None):
    """
    获取指定日期发布财报的公司清单

    Args:
        date: 日期字符串，格式 YYYYMMDD 或 YYYY-MM-DD，默认今天

    Returns:
        DataFrame: 发布年报的公司列表
    """

    # 处理日期格式
    if date is None:
        date = datetime.now().strftime('%Y%m%d')
    else:
        date = date.replace('-', '')

    display_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

    print(f"\n{'='*60}")
    print(f"获取 {display_date} 发布财报的A股公司清单")
    print(f"{'='*60}\n")

    try:
        # 获取公告数据
        print("正在获取公告数据...")
        df = ak.stock_notice_report(symbol='全部', date=date)

        print(f"✓ 获取到 {len(df)} 条公告\n")

        # 筛选年报相关公告
        annual_report = df[df['公告标题'].str.contains('年报|年度报告', na=False)].copy()

        if len(annual_report) == 0:
            print(f"❌ {display_date} 没有公司发布年报\n")
            return None

        # 提取发布年报的公司（去重）
        companies = annual_report[['代码', '名称']].drop_duplicates()
        print(f"✓ 找到 {len(companies)} 家公司发布年报\n")

        # 获取这些公司的详细财务数据
        print("正在获取财务数据...")
        result = []

        for idx, (_, row) in enumerate(companies.iterrows(), 1):
            code = row['代码']
            name = row['名称']
            print(f"  [{idx}/{len(companies)}] {code} {name}...", end='')

            try:
                # 获取财务摘要
                financial = get_financial_summary(code)
                if financial:
                    result.append({
                        '股票代码': code,
                        '股票简称': name,
                        '每股收益': financial.get('eps'),
                        '营业收入': financial.get('revenue'),
                        '营收同比增长(%)': financial.get('revenue_growth'),
                        '净利润': financial.get('net_profit'),
                        '净利同比增长(%)': financial.get('profit_growth'),
                        'ROE(%)': financial.get('roe'),
                    })
                    print(' ✓')
                else:
                    print(' 跳过')
            except Exception as e:
                print(f' 错误: {e}')

        if result:
            result_df = pd.DataFrame(result)
            result_df = result_df.sort_values('净利同比增长(%)', ascending=False)
            return result_df
        else:
            return None

    except Exception as e:
        print(f"获取数据错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_financial_summary(stock_code):
    """获取财务摘要"""

    try:
        df = ak.stock_financial_abstract(symbol=stock_code)

        # 转置数据
        df_transposed = df.set_index('指标').T

        # 移除"选项"行
        if '选项' in df_transposed.index:
            df_transposed = df_transposed.drop('选项')

        # 获取最新一期数据
        if len(df_transposed) == 0:
            return None

        row = df_transposed.iloc[0]

        # 安全转换函数
        def safe_float(value):
            if value is None:
                return None
            try:
                import pandas as pd
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

        # 提取数据
        data = {
            'eps': safe_float(row.get('基本每股收益', row.get('每股收益'))),
            'revenue': safe_float(row.get('营业总收入', row.get('营业收入'))),
            'net_profit': safe_float(row.get('净利润')),
            'roe': safe_float(row.get('净资产收益率(ROE)', row.get('净资产收益率'))),
        }

        # 计算同比增长
        if len(df_transposed) > 4:
            last_year_row = df_transposed.iloc[4]

            if data['revenue'] and safe_float(last_year_row.get('营业总收入', last_year_row.get('营业收入'))):
                last_revenue = safe_float(last_year_row.get('营业总收入', last_year_row.get('营业收入')))
                if last_revenue and last_revenue != 0:
                    data['revenue_growth'] = ((data['revenue'] - last_revenue) / abs(last_revenue)) * 100

            if data['net_profit'] and safe_float(last_year_row.get('净利润')):
                last_profit = safe_float(last_year_row.get('净利润'))
                if last_profit and last_profit != 0:
                    data['profit_growth'] = ((data['net_profit'] - last_profit) / abs(last_profit)) * 100

        return data

    except Exception as e:
        return None


def print_company_list(df):
    """打印公司清单"""

    if df is None or len(df) == 0:
        return

    print(f"\n{'='*60}")
    print("年报发布公司列表")
    print(f"{'='*60}\n")

    # 格式化显示
    display_df = df.copy()

    # 格式化数字
    def format_num(value, is_money=False):
        if value is None or pd.isna(value):
            return 'N/A'
        try:
            value = float(value)
            if is_money:
                if abs(value) >= 1e8:
                    return f'{value/1e8:.2f}亿'
                elif abs(value) >= 1e4:
                    return f'{value/1e4:.2f}万'
                else:
                    return f'{value:.2f}'
            else:
                return f'{value:.2f}'
        except:
            return 'N/A'

    display_df['每股收益'] = display_df['每股收益'].apply(lambda x: format_num(x))
    display_df['营业收入'] = display_df['营业收入'].apply(lambda x: format_num(x, True))
    display_df['净利润'] = display_df['净利润'].apply(lambda x: format_num(x, True))
    display_df['营收同比增长(%)'] = display_df['营收同比增长(%)'].apply(lambda x: format_num(x))
    display_df['净利同比增长(%)'] = display_df['净利同比增长(%)'].apply(lambda x: format_num(x))
    display_df['ROE(%)'] = display_df['ROE(%)'].apply(lambda x: format_num(x))

    print(display_df.to_string(index=False))

    # 统计信息
    print(f"\n{'='*60}")
    print("统计信息：")

    total = len(df)
    profit_positive = df[df['净利同比增长(%)'] > 0]
    profit_negative = df[df['净利同比增长(%)'] < 0]

    print(f"  总数：{total} 家")
    print(f"  净利润增长：{len(profit_positive)} 家 📈")
    print(f"  净利润下降：{len(profit_negative)} 家 📉")

    if len(profit_positive) > 0:
        print("\n净利润增长 TOP 5：")
        for idx, row in profit_positive.head(5).iterrows():
            growth = row['净利同比增长(%)']
            print(f"  {row['股票代码']} {row['股票简称']}: {growth:.2f}%")

    if len(profit_negative) > 0:
        print("\n净利润下降 TOP 5：")
        for idx, row in profit_negative.tail(5).iterrows():
            growth = row['净利同比增长(%)']
            print(f"  {row['股票代码']} {row['股票简称']}: {growth:.2f}%")

    print(f"\n{'='*60}\n")


def main():
    """主函数"""

    # 解析命令行参数
    date = sys.argv[1] if len(sys.argv) > 1 else None

    # 获取数据
    df = fetch_reports_by_date(date)

    # 打印结果
    if df is not None:
        print_company_list(df)

        # 保存到CSV
        if date:
            filename = f"reports_{date}.csv"
        else:
            filename = f"reports_{datetime.now().strftime('%Y%m%d')}.csv"

        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✓ 已保存到: {filename}\n")


if __name__ == '__main__':
    main()
