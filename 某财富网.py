import time
import json
import random
import pymysql
from DrissionPage import WebPage
from DrissionPage.common import By
from DrissionPage import ChromiumPage, ChromiumOptions
from config import DB_CONFIG, SPIDER_CONFIG

class DongFang:
    def __init__(self):
        co = ChromiumOptions()
        co.auto_port()
        self.browser = ChromiumPage(co)
        self.url = SPIDER_CONFIG['url']
        self.api = SPIDER_CONFIG['api']
        self.db = pymysql.connect(**DB_CONFIG)
        self.cursor = self.db.cursor()
        self.page_num = SPIDER_CONFIG['start_page']

    def create_table(self):
        sql = """
            create table if not exists east_money(
                id int primary key auto_increment,
                name varchar(50) not null,
                code varchar(10) not null unique,
                price varchar(50) not null,
                volume varchar(50) not null,
                amount varchar(50) not null
            );
        """
        try:
            self.cursor.execute(sql)
            self.db.commit()
            print("创建表成功")
        except pymysql.Error as e:
            print("创建失败:", e)

    def save_work_info(self, *args):
        sql = """
              insert ignore into east_money values (%s, %s, %s, %s, %s, %s)
              """
        try:
            self.cursor.execute(sql, args)
            self.db.commit()
            if self.cursor.rowcount > 0:
                print("保存成功", args)
        except pymysql.Error as e:
            print("保存失败:", e)
            self.db.rollback()

    def down_page(self):
        a = random.randint(*SPIDER_CONFIG['scroll_range'])
        self.browser.scroll.down(a)
        time.sleep(random.uniform(*SPIDER_CONFIG['scroll_sleep']))

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
        self.create_table()
        self.browser.listen.start(self.api)
        self.browser.get(self.url)
        self.browser.set.window.max()
        self.browser.ele((By.XPATH, '/html/body/div[5]/img[1]')).click()
        self.down_page()
        max_page = self.browser.ele('xpath://*[@id="mainc"]/div/div/div[4]/div/a[4]').text
        for i in range(self.page_num, int(max_page) + 1):
            print("--" * 30)
            print(f'当前是第{i}页')
            time.sleep(random.uniform(*SPIDER_CONFIG['page_sleep']))

            res = self.browser.listen.wait(timeout=1)
            info_list = self.parse_info(res)
            for info in info_list:
                name = info['f14'] if info['f14'] != '-' else '暂无数据'
                code = str(info['f12']) if info['f12'] != '-' else '暂无数据'
                price = float(info['f2'])/100 if info['f2'] != '-' else '暂无数据'
                volume = self.format_number(int(info['f5'])) if info['f5'] != '-' else '暂无数据'
                amount = self.format_number(int(info['f6'])) if info['f6'] != '-' else '暂无数据'

                self.save_work_info(None, name, code, price, volume, amount)

            self.down_page()
            time.sleep(random.uniform(0.5, 1.5))
            self.browser.ele('xpath://*[@id="mainc"]/div/div/div[4]/div/form/input[1]').input(i + 1)
            time.sleep(random.uniform(0.5, 1.0))
            self.browser.ele('xpath://*[@id="mainc"]/div/div/div[4]/div/form/input[2]').click()
        self.close_spider()

if __name__ == '__main__':
    dongfang = DongFang()
    dongfang.main()
