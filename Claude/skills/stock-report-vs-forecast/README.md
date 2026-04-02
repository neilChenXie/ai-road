# A股财报预期对比分析工具

自动获取A股公司发布的财报，对比机构预测数据，判断业绩是否符合预期。

## 功能特性

- 📊 **实时获取**：从东方财富获取当日发布的财报公告
- 🎯 **预期对比**：对比实际财报数据与机构预测
- 📈 **智能判断**：超预期/符合预期/不及预期
- 📝 **自动报告**：生成详细的分析报告

## 快速开始

```bash
cd scripts

# 分析今天发布的所有财报
python main.py

# 分析指定日期的财报
python main.py 20260402

# 分析指定股票
python main.py --stock 600684
python main.py --stock 600684 2025
```

## 输出示例

```
######################################################################
# 2026-04-02 财报分析
######################################################################

[步骤1] 获取当天发布财报的公司...
✓ 找到 31 家公司发布财报

[步骤2] 分析每只股票的预期对比...

============================================================
分析: 600684 珠江股份
============================================================
  报告期: 20251231
  EPS: 0.08 vs 预测 0.15
  判断: 📉 不及预期

...

######################################################################
# 汇总分析结果
######################################################################

统计:
  📈 超预期: 5 家
  ✅ 符合预期: 8 家
  📉 不及预期: 12 家
  ❓ 无预测: 6 家

【超预期】
  600104 上汽集团: EPS 0.89 vs 预测 0.75 (+18.7%)
  ...

【不及预期】
  600684 珠江股份: EPS 0.08 vs 预测 0.15 (-46.7%)
  ...

✓ 结果已保存到: analysis_20260402.json
```

## 项目结构

```
aearn-earnings-report/
├── SKILL.md              # Skill定义文档
├── README.md             # 本文件
├── references/           # 参考资料
│   ├── api_docs.md
│   └── data_fields.md
└── scripts/              # 核心脚本
    ├── main.py           # 主程序入口
    ├── fetch_today_reports.py    # 获取今日财报发布
    ├── fetch_recent_forecast.py  # 获取机构预测
    └── analyze_report_vs_forecast.py  # 预期对比分析
```

## 核心脚本

### main.py - 主程序

整合全流程的分析主程序。

```bash
# 分析今天
python main.py

# 分析指定日期
python main.py 20260402

# 分析指定股票
python main.py --stock 600684
```

### fetch_today_reports.py - 获取财报发布清单

从东方财富公告接口获取指定日期发布财报的公司列表。

```python
from fetch_today_reports import fetch_reports_by_date

# 获取今日发布财报的公司
df = fetch_reports_by_date('20260402')
print(df)
```

### fetch_recent_forecast.py - 获取机构预测

从研报数据中提取机构对股票的盈利预测。

```python
from fetch_recent_forecast import get_forecast_data

# 获取机构预测数据
forecast = get_forecast_data('600684')
print(forecast)
# {'forecast_count': 5, 'eps_forecast_avg': 0.15, ...}
```

### analyze_report_vs_forecast.py - 预期对比分析

对比实际财报与机构预测，计算差异率并判断是否符合预期。

```python
from analyze_report_vs_forecast import analyze_earnings_vs_forecast

# 分析单只股票
result = analyze_earnings_vs_forecast('600684', 2025)
print(result['judgment'])  # '不及预期'
```

## 数据来源

| 数据类型 | 来源 | 接口 |
|---------|------|------|
| 财报公告 | 东方财富 | `stock_notice_report` |
| 财务数据 | 东方财富 | `stock_financial_abstract` |
| 机构预测 | 东方财富研报 | `stock_research_report_em` |

## 判断标准

- 📈 **超预期**：实际值 > 预测值 + 5%
- ✅ **符合预期**：-5% ≤ 差异率 ≤ 5%
- 📉 **不及预期**：实际值 < 预测值 - 5%

## 依赖安装

```bash
pip install akshare pandas
```

## 在Claude Code中使用

直接对Claude说：

```
分析今天发布的A股财报
```

或

```
珠江股份的财报是否符合预期？
```

## 版本历史

- **v3.0** (2026-04-02)：重构版本，支持批量分析和单股分析
- **v2.0** (2026-04-02)：使用AKShare数据源
- **v1.0** (2026-04-02)：初始版本

## 免责声明

本工具仅供参考，不构成投资建议。投资有风险，入市需谨慎。