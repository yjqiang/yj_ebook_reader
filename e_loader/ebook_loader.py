import re
from urllib.parse import urljoin
import console
from bs4 import element
import zh_st
from e_loader.e_loader import ELoader


class EBookLoader(ELoader):
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
            if not self.get_url2next():
                return None, None, None
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

    def get_content(self):
        rules = self.conf['content']
        labels = []
        for rule in rules:
            name, attrs, string, _ = self.get_rule(rule)
            
            labels += self.soups.find_all(name, attrs=attrs, string=string)
        words = []
        for i in labels:
            for row in i.childGenerator():
                if isinstance(row, element.Comment):
                    continue
                para = row.string

                if para is not None:
                    para = para.strip()
                    if para:
                        if para[0] != '　':
                            para = '　　' + para
                        words.append(para)
        return words
    
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
                
