from itertools import islice
from collections import deque
import ui
import console
from ui import Image
from controller import Controller
from e_loader.e_loader import EImgLoader

url = 'https://e-hentai.org/s/9962198a63/1300988-2'
url = 'https://m.k886.net/look/name/SuperDick/cid/36391/id/339212/p/2'
# url = 'https://raws.mangazuki.co/manga/desire-king/81'
# url = 'http://www.177pic.info/html/2018/04/1999461.html/19'
url = 'https://manhwahand.com/manhwa/desire-king/chapter-30?style=list'
# url = 'https://nhentai.net/g/249922/2/'
# url = 'https://mangapark.me/manga/love-parameter-kkun/s1/c104/2'
# url = 'https://www.taadd.com/chapter/HMate59/798722-21.html'
# url = 'https://manganelo.com/chapter/hcampus/chapter_55'
# url = 'https://www.wnacg.org/photos-view-id-4901546.html'


class ReaderViewer:
    ITEM_H = 70
    WIDTH_LINE = 337
    LOADING = Image.named('iob:load_d_32')
    LOADING_HEIGHT = WIDTH_LINE / LOADING.size.x * LOADING.size.y
        
    def __init__(self, controller):
        reader_view = ui.load_view('eimg_reader')
        scrollview = reader_view['scrollview']
        for i in range(9):
            # print(reader_view[f'imageview{i}'])
            scrollview.add_subview(reader_view[f'imageview{i}'])
        scrollview.delegate = self
        self.has_sent_req = False
        self.scrollview = scrollview
        self.reader_view = reader_view
        self.items = deque(self.scrollview.subviews)
        assert (len(self.items) - 1) * self.ITEM_H > scrollview.height
        self.controller = controller
        
    def req_data_bg(self):
        self.controller.req_data_bg()
    
    def req_data(self, init=False):
        self.controller.req_data(init)
        
    def set_navi_view_name(self, name):
        self.controller.set_navi_view_name(name)
        
    def refresh_title(self):
        off_set = self.cur_offset
        for item in self.items:
            if item.y + item.height >= off_set:
                i = item.i
                if i is None:
                    continue
                
                for l, r, name, url in self.titles:
                    if l <= i < r:
                        self.set_navi_view_name(name)
                return
        
    def load_data(self):
        element = self.controller.load_data()
        if element is None:
            return False
        if element[0] is None:
            # 到底之后不再复位self.has_sent_req
            console.hud_alert('已经阅读完毕')
            return False
        l = len(self.contents)
        imgs, title, url, init = element
        
        # 保证进度条不会完全到底
        sum_height = -10 if init else 0
        for img in imgs:
            resized_height = self.WIDTH_LINE / img.size.x * img.size.y
            sum_height += resized_height
        
            self.contents.append((img, resized_height))
            
        r = len(self.contents)
        if self.titles:
            # merge 当一个页面多个图片
            last_title = self.titles[-1]
            if last_title[3] == url:
                self.titles[-1] = (last_title[0], r, title, url)
            else:
                self.titles.append((l, r, title, url))
        else:
            self.titles.append((l, r, title, url))
            
        self.scrollview.content_size += (0, sum_height)
        self.has_sent_req = False
        return True
        
    def reset_view(self, i=0, j=0):
        scrollview = self.scrollview
        # [(image, resized_height),]
        self.contents = []
        # (l, r, name)
        self.titles = []
    
        scrollview.content_size = (scrollview.width, 0)
        
        self.cur_offset = 0

        self.req_data(True)
        self.load_data()
        # 条件应该是把一页填充满而且书签模式下尽量加载
        while scrollview.content_size.y <= scrollview.height or len(self.contents) <= i:
            self.req_data()
            self.load_data()
        # print(scrollview.content_size)
        
        rows = i
        len_content = len(self.contents)
        len_items = len(self.items)
        y = 0
        start = max(0, len_items - len_content)
        remain = islice(self.items, start, len_items)
        for i, (item, content) in enumerate(zip(remain, self.contents)):
            img, resize_height = content
            item.height = resize_height
            item.image = img
            item.i = i
            item.y = y
            y += resize_height
            
        # 未使用的item往上放
        y = 0
        if len_content < len_items:
            end = len_items - len_content - 1
            for i in range(end, -1, -1):
                item = self.items[i]
                item.i = None
                item.image = None
                y -= item.height
                item.y = y
         
        # 书签偏移量
        h = 0
        for content in self.contents[:rows]:
            img, resize_height = content
            h += resize_height

        # 这个破玩意儿改了之后会自动调用监听函数
        scrollview.content_offset = (0, h+j)
        self.refresh_title()
        
    def get_offset(self):
        scrollview = self.scrollview
        off_set = scrollview.content_offset.y
        i = None
        for item in self.items:
            if item.y + item.height >= off_set:
                i = item.i
                j = off_set - item.y
                break
        if i is None:
            return
        for l, r, name, url in self.titles:
            if l <= i < r:
                # 本页的i 相对段落数目
                new_bookmark = {
                    'i': i - l,
                    'j': int(j),
                    'url': url,
                    'title': name
                }
                return new_bookmark
                
    def reset_scrollbar(self):
        scrollview = self.scrollview
        offset_x, offset_y = scrollview.content_offset
        max_offset = scrollview.content_size.y - scrollview.height
        cur_offset = offset_y
        min_offset = min(cur_offset, max_offset)
        scrollview.content_offset = (offset_x, min_offset)
        
    def scrollview_did_scroll(self, scrollview):
        offset = scrollview.content_offset.y
        is_scroll_down = True if offset > self.cur_offset else False
        self.cur_offset = offset
        
        reader_h = scrollview.height
        # print('t')
        
        content_size = scrollview.content_size[1]
        if not content_size:
            return
        # 预加载
        if content_size - self.cur_offset <= 4 * reader_h:
            self.req_data_bg()
            
        # 滚动条下移
        if is_scroll_down:
            while True:
                item_end = self.items[-1]
                item_start = self.items[0]
                if (item_end.y + item_end.height - reader_h <= offset and item_end.i is not None):
                    # console.hud_alert('应该load')
                    i = item_end.i + 1
            
                    if i >= len(self.contents):
                        img = self.LOADING
                        resized_height = self.LOADING_HEIGHT
                        self.req_data_bg()
                        i = None
                        
                    else:
                        img, resized_height = self.contents[i]
                        
                    item_start.image = img
                    item_start.y = item_end.y + item_end.height
                    item_start.height = resized_height
                    item_start.i = i
                    self.items.rotate(-1)
                elif item_end.i is None and item_end.y <= offset + reader_h:
                    # console.hud_alert(f'应该refresh')
                    if not self.load_data():
                        break
                                    
                    item = self.items[-2]
                    i = item.i + 1
            
                    if i < len(self.contents):
                        img, resized_height = self.contents[i]
                        
                        item_end.image = img
                        item_end.y = item.y + item.height
                        item_end.height = resized_height
                        item_end.i = i
                    # 这个防止空白页吧……会有吗？
                    else:
                        break
                else:
                    break
        else:
            while True:
                item_end = self.items[-1]
                item_start = self.items[0]
                if item_start.y >= offset:
                    # None的时候仅仅是初始化设计导致的
                    if item_start.i is None or item_start.i <= 0:
                        break
                    i = item_start.i - 1
                    img, resized_height = self.contents[i]
                    item_end.image = img
                    item_end.height = resized_height
                    item_end.y = item_start.y - resized_height
                    item_end.i = i
                    self.items.rotate(1)
                    
                else:
                    break
        self.refresh_title()
        
        
controller = Controller(EImgLoader, ReaderViewer)

controller.load_reader(url)
controller.navi_viewer.view.present('fullscreen')

