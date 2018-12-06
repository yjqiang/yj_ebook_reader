import re
from urllib.parse import urljoin
import web
import console
from bs4 import BeautifulSoup, UnicodeDammit, element
import zh_st


class EBookLoader:
    def __init__(self, dict_conf):
        self.dict_conf = dict_conf
        user_agent = ('Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like'
                      'Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko)'
                      'CriOS/65.0.3325.152 Mobile/15D100 Safari/604.1')

        self.headers = {'User-Agent': user_agent}
        # 'url': text
        self.cache = {}

    def set_url(self, url):
        self.url = url
        for i in self.dict_conf['websites']:
            if i['url'] in url:
                self.conf = i
                break
        else:
            self.conf = None
        self.encoding_with_captcha()
        self.contents = self.get_content()
        self.cur_offset = 0
        
    def get_one_chapter(self):
        if self.cur_offset > 0:
            self.get_url2next()
            self.encoding_with_captcha()
            self.contents = self.get_content()
            self.cur_offset = 0
        words = self.contents
        title = self.title
        if self.encoding == 'big5':
            words = [zh_st.t2s(line) for line in words]
            title = zh_st.t2s(self.title)
        self.cur_offset += 1
        return words, title, self.url
        
        
        
    def get_criteria(self, dict_criteria):
        name = dict_criteria.get('name', None)
        attrs = dict_criteria.get('attrs', {})
        string_pattern = dict_criteria.get('string', None)
        string = None if string_pattern is None else re.compile(string_pattern)
        return name, attrs, string

    def get_url2next(self):
        next_tags = self.conf['next']
        for next_tag in next_tags:
            if 're_body' in next_tag:
                results = re.findall(re.compile(next_tag['re_body']), self.text)
                link = results[0]
                self.url = urljoin(self.url, link)
                print(self.url)
                return
            name, attrs, string = self.get_criteria(next_tag)
            # print(text)
            results = self.soups.find_all(name, attrs=attrs, string=string)
            # print(results)
            if results:
                link = results[0]['href']
                # print(results)
                # 防止j s (此时一般就是没了)
                if '/' in link or '.' in link:
                    self.url = urljoin(self.url, link)
                    return

    def encoding_page(self):
        if self.url in self.cache:
            text = self.cache[self.url]
            soups = BeautifulSoup(text, 'html.parser')
            self.soups = soups
            return soups
        rsp = web.get(self.url, headers=self.headers)
        binary = rsp.content
        text = rsp.text
        soups = BeautifulSoup(text, 'html.parser')

        encoding = self.conf['encoding']
        func_type = self.conf['encoding_func']
        if encoding:
            pass
        elif func_type:
            if func_type == 'content':
                tag = soups.find(
                    'meta',
                    attrs={
                        'http-equiv': re.compile('content-type', re.IGNORECASE)
                    })
                content = tag['content']
                encoding = re.search('charset=([^;]*)', content).group(1)
            elif func_type == 'charset':
                tag = soups.find('meta', charset=True)
                encoding = tag['charset']
            elif func_type == 'dammit':
                encoding = UnicodeDammit(binary).original_encoding
        else:
            encoding = None
        self.encoding = encoding if encoding else rsp.encoding
        print('encoding', self.encoding)
        if encoding is not None:
            text = binary.decode(encoding)
            soups = BeautifulSoup(text, 'html.parser')
        # print(soups.prettify())
        self.cache[self.url] = text
        self.text = text
        self.soups = soups
        return soups

    def get_content(self):
        tag_words = self.conf['content']
        labels = []
        for i in tag_words:
            name, attrs, string = self.get_criteria(i)
            
            labels += self.soups.find_all(name, attrs=attrs, string=string)
        words = []
        for i in labels:
            for row in i.childGenerator():
                if isinstance(row, element.Comment):
                    continue
                line = row.string

                if line is not None:
                    line = line.strip()
                    if line:
                        if line[0] != '　':
                            line = '　　' + line
                        words.append(line)
        return words
    
    def get_title(self):
        title_func = self.conf['title']
        if title_func:
            title = self.soups.find(title_func).string
        else:
            title = self.soups.find('title').string
        return str(title).strip()
        
    def encoding_with_captcha(self):
        re_safe_dog = re.compile('self.location="(.+)"')
        while True:
            self.encoding_page()
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
                
