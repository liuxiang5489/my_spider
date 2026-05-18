# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3308,
    'user': 'username',
    'password': 'password',
    'database': 'py_spider'
}

# 爬虫配置
SPIDER_CONFIG = {
    'url': 'https://quote.eastmoney.com/center/gridlist.html#hs_a_board',
    'api': '/api/qt/clist/get',
    'start_page': 1,
    'scroll_range': (380, 500),
    'page_sleep': (2.2, 5.5),
    'scroll_sleep': (0.1, 0.5)
}
