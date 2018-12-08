from e_loader.e_loader import ELoader
import web
import ui


class EImgLoader(ELoader):
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
        contents = []       
        results = super().get_content('src')
        for tags, key in results:
            contents += [tag[key] for tag in tags]
        return contents
        
