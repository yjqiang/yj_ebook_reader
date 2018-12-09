from e_loader.e_loader import ELoader
import web
import ui


class EImgLoader(ELoader):
    def get_one_img(self):
        if self.cur_offset is None:
            self.encoding_page()
            self.contents = self.get_content()
            self.title = self.get_title()
            self.cur_offset = 0
        if self.cur_offset >= len(self.contents):
            if not self.get_url2next():
                return None, None, None
            self.encoding_page()
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
        rules = self.conf['content']
        urls = []
        for rule in rules:
            name, attrs, string, key = self.get_rule(rule, def_key='src')
            labels = self.soups.find_all(name, attrs=attrs, string=string)
            urls += [i[key] for i in labels]
        
        return urls
        
