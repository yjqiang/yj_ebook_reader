import re
import console
from urllib.parse import urljoin
import web
from bs4 import BeautifulSoup


class EPageLoader:
    def __init__(self, cache, page_rule, website_rule):
        # 'url': text
        self.cache = cache
        self.rule = page_rule
        self.website_rule = website_rule

    def set_url(self, url):
        self.url = url
        self.cur_offset = None
        
    def get_title(self):
        rule = self.rule.title
        name = rule['name']
        attrs = rule['attrs']
        string = rule['string']
        title = self.soups.find(name, attrs=attrs, string=string).string
        return str(title).strip()
        
    def get_content(self):
        pass

    def get_next_url(self):
        rules = self.rule.next
        if rules is None:
            return False
        for rule in rules:
            if 're' in rule:
                result = rule['re'].search(self.text)
                if result is None:
                    return False
                self.url = urljoin(self.url, result.group(1))
                return True
            name = rule['name']
            attrs = rule['attrs']
            string = rule['string']
            # print(text)
            result = self.soups.find(name, attrs=attrs, string=string)
            # print(results)
            if result is not None:
                link = result[rule['key']]
                # print(results)
                # 防止j s (此时一般就是没了)
                if 'javascript' not in link and link != '#':
                    self.url = urljoin(self.url, link)
                    return True
        return False

    def fetch_page(self):
        if self.url in self.cache:
            text = self.cache[self.url]
            soups = BeautifulSoup(text, 'html.parser')
            self.text = text
            self.soups = soups
        else:
            rsp = web.get(self.url, headers=self.website_rule.headers)
            # encoding为None，requests模块会自己猜测
            
            rsp.encoding = self.website_rule.encoding
            # print(rsp.encoding)
            text = rsp.text
            soups = BeautifulSoup(text, 'html.parser')
            self.cache[self.url] = text
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
                link = re.findall(re_safe_dog, js)[0]
                self.url = urljoin(self.url, link)
                # print(link)
            else:
                break
        self.title = title
        return
