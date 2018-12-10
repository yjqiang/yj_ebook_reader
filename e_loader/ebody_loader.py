import ui
from urllib.parse import urljoin
from bs4 import element
import web
import zh_st
from .ebase_loader import EPageLoader


class BodyLoader(EPageLoader):
    def get_index_url(self):
        rule = self.rule.index
        # print('测试index')
        if rule is None:
            return None
        else:
            self.fetch_page_with_captcha()
            name = rule['name']
            attrs = rule['attrs']
            string = rule['string']
            tag = self.soups.find(name, attrs=attrs, string=string)
            url = urljoin(self.url, tag[rule['key']])
            # print(url)
            return url
                        

class EBookBodyLoader(BodyLoader):
    def get_next_data(self):
        if self.cur_offset is None:
            self.fetch_page_with_captcha()
            self.contents = self.get_content()
            self.cur_offset = 0
        if self.cur_offset > 0:
            if not self.get_next_url():
                return None, None, None
            self.fetch_page_with_captcha()
            self.contents = self.get_content()
            self.cur_offset = 0
        words = self.contents
        title = self.title
        words = [zh_st.t2s(line) for line in words]
        title = zh_st.t2s(self.title)
        self.cur_offset += 1
        return words, title, self.url

    def get_content(self):
        rules = self.rule.content
        labels = []
        for rule in rules:
            name = rule['name']
            attrs = rule['attrs']
            string = rule['string']
            
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
        
        
class EImgBodyLoader(BodyLoader):
    def get_next_data(self):
        if self.cur_offset is None:
            self.fetch_page_with_captcha()
            self.contents = self.get_content()
            self.title = self.get_title()
            self.cur_offset = 0
        if self.cur_offset >= len(self.contents):
            if not self.get_next_url():
                return None, None, None
            self.fetch_page_with_captcha()
            self.contents = self.get_content()
            self.title = self.get_title()
            self.cur_offset = 0
        
        img_url = self.contents[self.cur_offset]
        if img_url in self.cache:
            img = self.cache[img_url]
        else:
            img = ui.Image.from_data(web.get(img_url).content)
            self.cache[img_url] = img
        self.cur_offset += 1
        return [img], self.title, self.url
        
    def get_content(self):
        rules = self.rule.content
        urls = []
        for rule in rules:
            name = rule['name']
            attrs = rule['attrs']
            string = rule['string']
            labels = self.soups.find_all(name, attrs=attrs, string=string)
            urls += [i[rule['key']] for i in labels]
        
        return urls
                
