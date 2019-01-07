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
            result = rule.find_attr(self.text, self.soups)
            url = urljoin(self.url, result.strip())
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
            
        if not self.contents:
            return None, None, None
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
            # 其实这里默认了不能re
            labels += rule.findall_raw(self.text, self.soups)
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
            while True:
                if not self.get_next_url():
                    return None, None, None
                self.fetch_page_with_captcha()
                self.contents = self.get_content()
                self.title = self.get_title()
                self.cur_offset = 0
                if self.contents:
                    break
        if not self.contents:
            return None, None, None
        
        img_url = self.contents[self.cur_offset]
        img = ui.Image.from_data(web.get(img_url).content)
        self.cur_offset += 1
        return [img], self.title, self.url
        
    def get_content(self):
        rules = self.rule.content
        urls = []
        for rule in rules:
            results = rule.findall_attr(self.text, self.soups)
            urls += [urljoin(self.url, result.strip()) for result in results]
        
        return urls
                
