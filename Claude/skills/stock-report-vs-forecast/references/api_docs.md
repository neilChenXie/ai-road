# 东方财富网API文档

## 概述

本文档描述了skill使用的东方财富网公开数据接口。

**注意**：这些接口是东方财富网前端使用的公开接口，可能会随时变更。使用时需要注意：
1. 添加适当的User-Agent
2. 控制请求频率，避免被封IP
3. 接口可能随时变化，需要定期验证

## 1. 年报日历接口

### 接口地址
```
https://datacenter-web.eastmoney.com/api/data/v1/get
```

### 请求方法
GET

### 请求参数

| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| reportName | string | 报表名称 | RPT_LICO_FN_CALENDAR |
| columns | string | 返回字段 | ALL |
| filter | string | 过滤条件 | (REPORT_DATE='2024-12-31') |
| pageSize | int | 每页数量 | 500 |
| pageNumber | int | 页码 | 1 |

### 返回示例
```json
{
  "result": {
    "data": [
      {
        "SECURITY_CODE": "600000",
        "SECURITY_NAME_ABBR": "浦发银行",
        "REPORT_DATE": "2024-12-31",
        "REPORT_TYPE": "年报"
      }
    ]
  }
}
```

## 2. 财务数据接口

### 接口地址
```
https://emweb.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ZYZBAjaxNew
```

### 请求方法
GET

### 请求参数

| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| companyType | string | 公司类型 | 4 |
| reportDateType | string | 报告日期类型 | 0 |
| code | string | 股票代码（带市场前缀） | 1.600000 |

### 市场代码
- 上交所：1.xxx（如：1.600000）
- 深交所：0.xxx（如：0.000001）

### 返回示例
```json
{
  "data": {
    "main": [
      {
        "yysr": "150000000000",
        "jlr": "50000000000",
        "yysrtbzz": "5.5",
        "jlrtbzz": "8.2",
        "mgjlr": "2.5",
        "roe": "12.5"
      }
    ]
  }
}
```

## 3. 机构预测接口

### 接口地址
```
https://datacenter-web.eastmoney.com/api/data/v1/get
```

### 请求方法
GET

### 请求参数

| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| reportName | string | 报表名称 | RPT_RESEARCH_PREDICT |
| columns | string | 返回字段 | ALL |
| filter | string | 过滤条件 | (SECURITY_CODE="600000") |
| pageSize | int | 每页数量 | 20 |
| pageNumber | int | 页码 | 1 |
| sortColumns | string | 排序字段 | REPORT_DATE |
| sortTypes | string | 排序方式 | -1（降序）|

### 返回示例
```json
{
  "result": {
    "data": [
      {
        "SECURITY_CODE": "600000",
        "REVENUE_FORECAST": "155000000000",
        "NET_PROFIT_FORECAST": "52000000000",
        "EPS_FORECAST": "2.6",
        "REPORT_DATE": "2024-12-01",
        "RESEARCH_INST": "某证券公司"
      }
    ]
  }
}
```

## 使用建议

### 请求频率控制
```python
import time

# 每次请求间隔0.5秒
time.sleep(0.5)
```

### 错误处理
```python
try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
    # 重试或跳过
```

### User-Agent设置
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
response = requests.get(url, params=params, headers=headers)
```

## 替代数据源

如果东方财富网接口不可用，可考虑以下替代方案：

1. **Tushare**（需要token）
   - 提供稳定的财务数据API
   - 网址：https://tushare.pro/

2. **AkShare**
   - 开源财经数据接口库
   - GitHub：https://github.com/akfamily/akshare

3. **同花顺**
   - 类似东方财富网的公开数据

## 更新日志

- 2026-04-02：初始版本，基于东方财富网页版API
