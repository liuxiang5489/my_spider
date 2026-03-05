import time
import json
# import redis
import random
import pymysql

# import hashlib
from DrissionPage import WebPage
from DrissionPage.common import By
from DrissionPage import ChromiumPage, ChromiumOptions

class DongFang:
    def __init__(self):
        co = ChromiumOptions()
        co.auto_port()
        self.browser = ChromiumPage(co)
        self.url = 'https://quote.eastmoney.com/center/gridlist.html#hs_a_board'
        self.api = '/api/qt/clist/get'
        self.db = pymysql.connect(host='localhost', port=3308, user='username', passwd='password', db='py_spider')
        self.cursor = self.db.cursor()
        # self.redis_client = redis.Redis()
        self.page_num = 1

    # @staticmethod
    # def get_md5(response):
    #     md5_hash = hashlib.md5(str(response).encode('utf-8')).hexdigest()
    #     return md5_hash
    # 名称、代码、最新价、成交量、成交额
    def create_table(self):
        # noinspection SqlNoDataSourceInspection,SqlDialectInspection
        sql = """
            create table if not exists east_money(
                id int primary key auto_increment,
                name varchar(50) not null,
                code float not null,  
                price varchar(50) not null,
                volume varchar(50) not null,
                amount varchar(50) not null
            );
        """
        try:
            self.cursor.execute(sql)
            print("创建表成功")
        except Exception as e:
            print("创建失败",e)

    def save_work_info(self, *args):
        """
        *args是不定长字段，把数据库表中的信息打包成一个元组
        """
        sql = """
              insert into east_money values (%s, %s, %s, %s, %s, %s) 
              """
        try:
            self.cursor.execute(sql, args)
            self.db.commit()
            print("保存成功", args)
        except Exception as e:
            print("保存失败", e)
            self.db.rollback()


    def down_page(self):
        a = random.randint(380, 500)
        self.browser.scroll.down(a)
        time.sleep(random.uniform(0.1, 0.5))
        time.sleep(random.uniform(0.2, 0.5))


    def parse_info(self, res):
        data = res.response.body
        data = data.split('(', 1)[1]
        data = data.rsplit(')', 1)[0]
        json_info = json.loads(data)
        data = json_info["data"]["diff"]
        return data

    def format_number(self, num):
        num = float(num)
        if num >= 100000000:
            return f"{num / 100000000:.2f}亿"
        elif num >= 10000:
            return f"{num / 10000:.2f}万"
        else:
            return f"{num:.2f}"

    def close_spider(self):
        self.cursor.close()
        self.db.close()
        print("爬虫结束")


    def main(self):
        # self.create_table()
        self.browser.listen.start(self.api)
        self.browser.get(self.url)
        self.browser.set.window.max()
        self.browser.ele((By.XPATH, '/html/body/div[5]/img[1]')).click()
        self.down_page()
        max_page = self.browser.ele('xpath://*[@id="mainc"]/div/div/div[4]/div/a[4]').text
        for i in range(137, int(max_page) + 1):
            print("--" * 30)
            print(f'当前是第{i}页')
            time.sleep(random.uniform(2.2, 5.5))

            res = self.browser.listen.wait(timeout=1)
            info_list = self.parse_info(res)
            for info in info_list:
                name = info['f14'] if info['f14'] != '-' else '暂无数据'
                code = int(info['f12']) if info['f12'] != '-' else '暂无数据'
                price = float(info['f2'])/100 if info['f2'] != '-' else '暂无数据'
                volume = self.format_number(int(info['f5'])) if info['f5'] != '-' else '暂无数据'
                amount = self.format_number(int(info['f6'])) if info['f6'] != '-' else '暂无数据'

                self.save_work_info(None, name, code, price, volume, amount)

            self.down_page()
            time.sleep(random.uniform(0.5, 1.5))
            self.browser.ele('xpath://*[@id="mainc"]/div/div/div[4]/div/form/input[1]').input(i + 1)
            time.sleep(random.uniform(0.5, 1.0))
            self.browser.ele('xpath://*[@id="mainc"]/div/div/div[4]/div/form/input[2]').click()
        time.sleep(1000)
        self.close_spider()

if __name__ == '__main__':
    dongfang = DongFang()
    dongfang.main()

