# 东方财富A股数据爬虫

一个基于DrissionPage的自动化数据抓取脚本。

通过监听数据接口，相较于Selenium大幅度提升了效率。
只需要把点击轨迹和数据接口部分略微改动就能通用大部分网页。

## 安装

```bash
pip install -r requirements.txt
```

## 配置

修改 `config.py` 中的数据库连接信息。

## 运行

```bash
python 某财富网.py
```

## 数据字段

- name: 股票名称
- code: 股票代码
- price: 最新价
- volume: 成交量
- amount: 成交额
