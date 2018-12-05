import ui
# import time
from config_loader import ConfigLoader
from ebook_loader import EBookLoader
import threading
from queue import Queue
import console
from ui import Image
from collections import deque


url = 'http://quanben-xiaoshuo.com/n/wuxiashijiedachuanyue/7.html'
url = 'http://www.luoxia.com/doupo/20982.htm'
url = 'https://www.xbookcn.com/book/chest/14.htm'
url = 'http://www.mfxsydw.com/book/15811/9005.html'
url = 'https://www.piaotian.com/html/9/9866/6782548.html'
url = 'https://m.qu.la/book/5210/10639876.html'
# 网站挂了
url = 'http://www.176novel.com/wapbook5713/3736669/'
url = 'https://m.qu.la/book/3952/10578367.html'

url = 'https://m.hunhun520.com/book/wuxianHchuanyue/15134674.html'
url = 'http://www.luoqiu.com/read/1/373549.html'
url = 'https://www.69shu.com/txt/1523/679709'
url = 'https://m.00xs.cc/mxiaoshuo/3983/9480362/'

url = 'https://m.snwx8.com/book/210/210159/45857682.html'
url = 'http://www.xitxt.net/read/19533_12.html'

conf_loader = ConfigLoader()

dict_conf = conf_loader.dict_conf
dict_bm = conf_loader.dict_bookmark


class Reader:
    ITEM_H = 32
    LEN_LINE = 19
        
    def __init__(self, scrollview, tableview):
        self.var_ebook_loader = EBookLoader(dict_conf)
        self.has_sent_req = False
        self.scrollview = scrollview
        self.tableview = tableview
        self.queue = Queue()
        self.items = deque(self.scrollview.subviews)
        assert (len(self.items) - 1) * self.ITEM_H > scrollview.height
        self.init_subviews(url)
        
    def load_page(self, init=False):
        self.var_ebook_loader.encoding_page()
        contents, title, url = self.var_ebook_loader.get_text_with_check()
        rows = 0
        for line in contents:
            len_contents = len(line)
            rows += int((len_contents - 1) / self.LEN_LINE) + 1
        
        split_contents = '—' * self.LEN_LINE
        contents.append(split_contents)
        if not init:
            rows = rows + 1
        self.queue.put((contents, rows, title, url))
        # print('执行')
        
    def check_title(self):
        i = self.items[0].i
        for l, r, name, url in self.titles:
            if l <= i < r:
                nav_view.name = name
        
    def add2contents(self):
        if not self.queue.empty():
            contents, rows, title, url = self.queue.get()
            l = len(self.contents)
            self.contents = self.contents + contents
            r = len(self.contents)
            self.titles.append((l, r, title, url))
            self.scrollview.content_size += (0, rows * self.ITEM_H)
            self.has_sent_req = False
            return rows
        
    def load_next_page_bg(self):
        if not self.has_sent_req:
            self.has_sent_req = True
            self.t = threading.Thread(target=self.load_next_page)
            self.t.start()
            
    def load_next_page(self):
        self.var_ebook_loader.get_url2next()
        self.load_page()
        
    def init_subviews(self, url, i=0, j=0):
        if self.has_sent_req:
            self.t.join()
        self.has_sent_req = False
        # self.queue.clear()
        self.queue = Queue()
        scrollview = self.scrollview
        print(1, scrollview.content_offset)
        # 这里把offset归零了,并调用了函数
        scrollview.content_size = (scrollview.width, 0)
        print(0, scrollview.content_offset)
        
        self.cur_offset = 0
            
        self.contents = []
        # (l, r, name)
        self.titles = []
        self.var_ebook_loader.set_url(url)
        self.load_page(True)
        rows = self.add2contents()
        while rows <= len(self.items):
            self.load_next_page()
            rows += self.add2contents()
        
        rows = 0
        for line in self.contents[:i]:
            rows += int((len(line) - 1) / self.LEN_LINE) + 1
        rows += int(j / self.LEN_LINE)
        
        i, j = 0, 0
        y = 0
        for item in self.items:
            if len(self.contents[i]) <= j:
                i, j = i + 1, 0
            item.text = self.contents[i][j: j + self.LEN_LINE]
            item.i = i
            item.j = j
            item.y = y
            y += self.ITEM_H
            j += self.LEN_LINE
        # print(self.items)
        self.check_title()
        # print(rows, i, j)
        # 这个破玩意儿改了之后会自动调用监听函数
        scrollview.content_offset = (0, rows*self.ITEM_H)
        
    def reset_scrollbar(self):
        scrollview = self.scrollview
        max_offset = scrollview.content_size.y - scrollview.height
        cur_offset = scrollview.content_offset.y
        min_offset = min(cur_offset, max_offset)
        scrollview.content_offset = (scrollview.content_offset.x, min_offset)
        
    def scrollview_did_scroll(self, scrollview):
        offset = scrollview.content_offset.y
        is_scroll_down = True if offset > self.cur_offset else False
        self.cur_offset = offset
        # print('t')
        
        # 滚动条下移
        if is_scroll_down:
            y = self.scrollview.content_size[1]
            if y and self.cur_offset / y >= 0.8:
                pass
                # self.load_next_page_bg()
            while True:
                item = self.items[0]
                if item.y + self.ITEM_H < offset and self.items[-1].j is not None:
                    item_end = self.items[-1]
                    i, j = item_end.i, item_end.j + self.LEN_LINE
                    if len(self.contents[i]) <= j:
                        i, j = i + 1, 0
                    if i >= len(self.contents):
                        text = 'LOADING...'
                        self.load_next_page_bg()
                        i, j = None, None
                        
                    else:
                        text = self.contents[i][j: j + self.LEN_LINE]
                        
                    item.text = text
                    item.y = item_end.y + self.ITEM_H
                    item.i = i
                    item.j = j
                    self.items.rotate(-1)
                else:
                    break
        else:
            while True:
                item = self.items[-1]
                if item.y > offset + scrollview.height:
                    item_start = self.items[0]
                    i = item_start.i
                    j = item_start.j - self.LEN_LINE
                    if j < 0:
                        len_paragraph = len(self.contents[i-1])
                        num_line = int((len_paragraph-1) / self.LEN_LINE) + 1
                        i, j = i - 1, (num_line - 1) * self.LEN_LINE
                
                    self.add2contents()
                    # 待定！！！！
                    
                    if i < 0:
                        break
                    
                    text = self.contents[i][j: j + self.LEN_LINE]
                    item.text = text
                    
                    item.y = item_start.y - self.ITEM_H
                    item.i = i
                    item.j = j
                    self.items.rotate(1)
                    
                else:
                    break
        self.check_title()
        

class BMTableViewer:
    def __init__(self, reader):
        self.reader = reader
        
    def tableview_did_select(self, tableview, section, row):
        bm = tableview.data_source.items[row]
        tableview.reload()
        self.reader.init_subviews(bm['url'], bm['i'], bm['j'])
        nav_view.pop_view()
        ui.animate(self.reader.reset_scrollbar, 0.5)
        # nav_view.right_button_items = main_button_items
                    
    def save_bm(self, sender):
        item = self.reader.items[0]
        i = item.i
        j = item.j
        # print(i, j)
        if i < 0:
            return
        for l, r, name, url in self.reader.titles:
            if l <= i < r:
                # 本页的i 相对段落数目
                new_bookmark = {
                    'i': i - l,
                    'j': j,
                    'url': url,
                    'title': name
                }
                        
        is_duplicated = conf_loader.check_bookmark(new_bookmark)
        
        if not is_duplicated:
            self.reader.tableview.data_source.items.append(new_bookmark)
            conf_loader.refresh_file(self.reader.tableview.data_source)
            console.hud_alert(f'已经保存')
        else:
            console.hud_alert('重复操作')
    

# url = input('请输入:\n')
reader_view = ui.load_view('reader')
sc = reader_view['scrollview']
bm_view = ui.load_view('bookmark')
nav_view = ui.NavigationView(reader_view)
tb = bm_view['tableview']

tb.data_source.items = dict_bm['bookmarks']
tb.data_source.edit_action = conf_loader.refresh_file

for i in range(18):
    sc.add_subview(reader_view[f'label{i}'])

var = Reader(sc, tb)
var_bm_table_viewer = BMTableViewer(var)

sc.delegate = var
tb.delegate = var_bm_table_viewer

reader_view['button_save_bm'].action = var_bm_table_viewer.save_bm

nav_view.navigation_bar_hidden = True
nav_view.present('fullscreen')
return_button_item = ui.ButtonItem(image=Image.named('iob:arrow_return_left_24'))
bm_button_items = [return_button_item]
nav_view.right_button_items = bm_button_items
return_button_item.action = nav_view.pop_view
reader_view['button_show_bm'].action = lambda _: nav_view.push_view(bm_view)

menu_button_item = ui.ButtonItem(image=Image.named('iob:navicon_round_24'))
main_button_items = [menu_button_item]
menu_button_item.action = nav_view.pop_view
