import re
import console
from urllib.parse import urljoin
import web
from bs4 import BeautifulSoup


class EPageLoader:
    def __init__(self, page_rule, website_rule):
        self.rule = page_rule
        self.website_rule = website_rule

    def set_url(self, url):
        self.url = url
        self.cur_offset = None
        
    def get_title(self):
        rule = self.rule.title
        title = rule.find_raw(self.text, self.soups, with_string=True)
        return str(title).strip()
        
    def get_content(self):
        pass

    def get_next_url(self):
        rules = self.rule.next
        if rules is None:
            return False
        for rule in rules:
            link = rule.find_attr(self.text, self.soups)
            # 防止j s (此时一般就是没了)
            if link is not None and 'javascript' not in link and link != '#':
                self.url = urljoin(self.url, link)
                return True
        return False

    def fetch_page(self):
        # 验证页面的话,不要缓存
        rsp = web.get(self.url, headers=self.website_rule.headers, allow_cache=False)
        # encoding为None，requests模块会自己猜测
        
        rsp.encoding = self.website_rule.encoding
        # print(rsp.encoding)
        text = rsp.text
        soups = BeautifulSoup(text, 'html.parser')
        self.text = text
        self.soups = soups
            
    def fetch_page_with_captcha(self):
        re_safe_dog = re.compile('self.location="(.+)"')
        while True:
            self.fetch_page()
            title = self.get_title()
            if '服务器安全狗防护验证页面' in title:
                console.hud_alert('验证')
                js = self.soups.find('script').string
                link = re_safe_dog.search(js).group(1)
                self.url = urljoin(self.url, link)
                # print(link)
            else:
                break
        self.title = title
        return
