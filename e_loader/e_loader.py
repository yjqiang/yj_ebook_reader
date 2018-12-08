import re
from urllib.parse import urljoin
import web
from bs4 import BeautifulSoup


class ELoader:
    def __init__(self, dict_conf):
        self.dict_conf = dict_conf
        user_agent = ('Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like'
                      'Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko)'
                      'CriOS/65.0.3325.152 Mobile/15D100 Safari/604.1')

        self.headers = {'User-Agent': user_agent}
        # 'url': text
        self.cache = {}

    def init_url(self, url):
        self.url = url
        for i in self.dict_conf['websites']:
            if i['url'] in url:
                self.conf = i
                break
        else:
            self.conf = None
        self.cur_offset = None
        
    def get_rule(self, dict_rule, def_key=None, def_name=None):
        name = dict_rule.get('name', def_name)
        attrs = dict_rule.get('attrs', {})
        string_pattern = dict_rule.get('string', None)
        string = None if string_pattern is None else re.compile(string_pattern)
        key = dict_rule.get('key', def_key)
        return name, attrs, string, key

    def get_url2next(self):
        rules = self.conf['next']
        for rule in rules:
            if 're_body' in rule:
                result = re.search(rule['re_body'], self.text)
                if result is None:
                    return False
                self.url = urljoin(self.url, result.group(1))
                print(self.url)
                return True
            name, attrs, string, key = self.get_rule(rule, 'href')
            # print(text)
            result = self.soups.find(name, attrs=attrs, string=string)
            # print(results)
            if result is not None:
                link = result[key]
                # print(results)
                # 防止j s (此时一般就是没了)
                if '/' in link or '.' in link:
                    self.url = urljoin(self.url, link)
                    return True
        return False

    def encoding_page(self, url=None):
        if url is None:
            url = self.url
        headers = {**self.headers, **self.conf.get('headers', {})}
        if url in self.cache:
            text, encoding = self.cache[url]
            soups = BeautifulSoup(text, 'html.parser')
            self.encoding = encoding
            self.soups = soups
            self.text = text
            return soups
        rsp = web.get(url, headers=headers)
        rsp.encoding = self.conf.get('encoding', rsp.encoding)
        self.encoding = rsp.encoding
        text = rsp.text
        soups = BeautifulSoup(text, 'html.parser')
        # print(soups.prettify())
        self.cache[url] = (text, self.encoding)
        self.text = text
        self.soups = soups
        return soups
    
    def get_title(self):
        rule = self.conf.get('title', {})
        # print(title_conf)
        name, attrs, string, _ = self.get_rule(rule, def_name='title')
        title = self.soups.find(name, attrs=attrs, string=string).string
        return str(title).strip()
        
    def get_content(self, extra_key=None):
        rules = self.conf['content']
        results = []
        if extra_key is None:
            for rule in rules:
                name, attrs, string, _ = self.get_rule(rule)
                tags = self.soups.find_all(name, attrs=attrs, string=string)
                results += tags
        else:
            for rule in rules:
                name, attrs, string, key = self.get_rule(rule, extra_key)
                tags = self.soups.find_all(name, attrs=attrs, string=string)
                results.append((tags, key))
        return results
