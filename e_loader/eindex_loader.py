from urllib.parse import urljoin
from .ebody_loader import EPageLoader
import zh_st


class EIndexLoader(EPageLoader):
    def get_next_data(self):
        if self.url is None:
            return None, None
        if self.cur_offset is None:
            self.fetch_page_with_captcha()
            self.contents = self.get_content()
            self.cur_offset = 0
        if self.cur_offset > 0:
            if not self.get_next_url():
                return None, None
            self.fetch_page_with_captcha()
            self.contents = self.get_content()
            self.cur_offset = 0
        # index [(index_url, index_name)]
        indexes = self.contents
        title = self.title
        indexes = [(urljoin(self.url, url), zh_st.t2s(name)) for url, name in indexes]
        title = zh_st.t2s(title)
        # print(indexes, len(indexes))
        self.cur_offset += 1
        return indexes, title
        
    def get_content(self):
        if self.url is None:
            return None
        rules = self.rule.content
        contents = []
        for rule in rules:
            name = rule['name']
            attrs = rule['attrs']
            string = rule['string']
            key = rule['key']
            labels = self.soups.find_all(name, attrs=attrs, string=string)
            contents += [(i[key], i.string) for i in labels]
        return contents
