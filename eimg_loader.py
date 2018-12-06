from ebook_loader import EBookLoader
import web
import ui


class EImgLoader(EBookLoader):
    def set_url(self, url):
        self.url = url
        for i in self.dict_conf['websites']:
            if i['url'] in url:
                self.conf = i
                break
        else:
            self.conf = None
        self.encoding_page()
        self.contents = self.get_content()
        self.title = self.get_title()
        self.cur_offset = 0
        
    def get_one_img(self):
        if self.cur_offset >= len(self.contents):
            self.get_url2next()
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
        img_tags = self.conf['content']
        urls = []
        for img_tag in img_tags:
            name, attrs, string = self.get_criteria(img_tag)
            labels = self.soups.find_all(name, attrs=attrs, string=string)
            urls += [i[img_tag['key']] for i in labels]
        
        return urls
        
