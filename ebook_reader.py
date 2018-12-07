import threading
from queue import Queue
from collections import deque
import ui
import console
from ui import Image
from config_loader import ConfigLoader
from e_loader.ebook_loader import EBookLoader


url = 'http://quanben-xiaoshuo.com/n/wuxiashijiedachuanyue/7.html'
# url = 'http://www.luoxia.com/doupo/20982.htm'
# url = 'https://www.xbookcn.com/book/chest/14.htm'
# url = 'http://www.mfxsydw.com/book/15811/9005.html'
# url = 'https://www.piaotian.com/html/9/9866/6782548.html'
# url = 'https://m.qu.la/book/5210/10639876.html'
# 网站挂了
# url = 'http://www.176novel.com/wapbook5713/3736669/'
# url = 'https://m.qu.la/book/3952/10578367.html'

# url = 'https://m.hunhun520.com/book/wuxianHchuanyue/15134674.html'
# url = 'http://www.luoqiu.com/read/1/373549.html'
# url = 'https://www.69shu.com/txt/1523/679709'
# url = 'https://m.00xs.cc/mxiaoshuo/3983/9480362/'

# url = 'https://m.snwx8.com/book/210/210159/45857682.html'
# url = 'http://www.xitxt.net/read/19533_12.html'
# url = 'https://www.piaotian.com/html/9/9275/6863827.html'
url = 'http://m.176xsw.com/7/111/read/99575.html'

conf_loader = ConfigLoader()

dict_conf = conf_loader.dict_conf
dict_bm = conf_loader.dict_bookmark


class Reader:
    ITEM_H = 32
    LEN_LINE = 19
    LOADING = 'LOADING...'
        
    def __init__(self, scrollview, tableview):
        self.var_ebook_loader = EBookLoader(dict_conf)
        self.has_sent_req = False
        self.scrollview = scrollview
        self.tableview = tableview
        self.queue = Queue()
        self.items = deque(self.scrollview.subviews)
        assert (len(self.items) - 1) * self.ITEM_H > scrollview.height
        self.init_subviews(url)
        
    def load_chapter(self, init=False):
        chapter, title, url = self.var_ebook_loader.get_one_chapter()
        self.queue.put((chapter, title, url, init))
        # print('执行')
        
    def check_title(self):
        off_set = self.cur_offset
        for item in self.items:
            if item.y + item.height >= off_set:
                i = item.i
                if i is None:
                    continue
                
                for l, r, name, url in self.titles:
                    if l <= i < r:
                        nav_view.name = name
                return
        
    def add2contents(self):
        if not self.queue.empty():
            chapter, title, url, init = self.queue.get()
            l = len(self.contents)
            sum_num_lines = 0 if init else 1
            for para in chapter:
                num_lines = int((len(para) - 1) / self.LEN_LINE) + 1
                sum_num_lines += num_lines
                self.contents.append((para, num_lines))
            
            split_contents = '—' * self.LEN_LINE
            self.contents.append((split_contents, 1))
            
            r = len(self.contents)
            self.titles.append((l, r, title, url))
            self.scrollview.content_size += (0, sum_num_lines * self.ITEM_H)
            self.has_sent_req = False
            return sum_num_lines
        return None
        
    def load_chapter_bg(self):
        if not self.has_sent_req:
            self.has_sent_req = True
            self.t = threading.Thread(target=self.load_chapter)
            self.t.start()
        
    def init_subviews(self, url, i=0, j=0):
        if self.has_sent_req:
            self.t.join()
        self.has_sent_req = False
        # self.queue.clear()
        self.queue = Queue()
        scrollview = self.scrollview
        # 这里把offset归零了,并调用了函数
        scrollview.content_size = (scrollview.width, 0)
        
        self.cur_offset = 0
            
        self.contents = []
        # (l, r, name)
        self.titles = []
        self.var_ebook_loader.set_url(url)
        self.load_chapter(True)
        sum_num_lines = self.add2contents()
        # 其实应该仿照img模块的，但是没必要，白白把逻辑弄麻烦了
        while sum_num_lines <= len(self.items):
            self.load_chapter()
            sum_num_lines += self.add2contents()
        
        i_wanted = i
        j_wanted = j
        i, j = 0, 0
        y = 0
        for item in self.items:
            if len(self.contents[i][0]) <= j:
                i, j = i + 1, 0
            item.text = self.contents[i][0][j: j + self.LEN_LINE]
            # i代表段落index，j代表了段落里面具体的文字起始下标
            item.i = i
            item.j = j
            item.y = y
            y += self.ITEM_H
            j += self.LEN_LINE
            
        sum_num_lines = 0
        for para, num_lines in self.contents[:i_wanted]:
            sum_num_lines += num_lines
        sum_num_lines += int(j_wanted / self.LEN_LINE)
        # 这个破玩意儿改了之后会自动调用监听函数
        scrollview.content_offset = (0, sum_num_lines*self.ITEM_H)
        self.check_title()
        
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
        # print('t')
        
        reader_h = scrollview.height
        # print('t')
        
        content_size = scrollview.content_size[1]
        # 预加载
        if content_size and content_size - self.cur_offset <= 3.5 * reader_h:
            self.load_chapter_bg()
        
        # 滚动条下移
        if is_scroll_down:
            while True:
                item_end = self.items[-1]
                item_start = self.items[0]
                if item_end.y + self.ITEM_H -reader_h < offset and item_end.i is not None:
                    i, j = item_end.i, item_end.j + self.LEN_LINE
                    if len(self.contents[i][0]) <= j:
                        i, j = i + 1, 0
                    if i >= len(self.contents):
                        text = self.LOADING
                        self.load_chapter_bg()
                        i, j = None, None
                        
                    else:
                        text = self.contents[i][0][j: j + self.LEN_LINE]
                        
                    item_start.text = text
                    item_start.y = item_end.y + self.ITEM_H
                    item_start.i = i
                    item_start.j = j
                    self.items.rotate(-1)
                elif item_end.i is None and item_end.y <= offset + reader_h:
                    if self.add2contents() is None:
                        break
                                    
                    item = self.items[-2]
                    i = item.i + 1
                    j = 0
            
                    # 由于一定会补足间隔行，所以这里i一定不越界
                    text = self.contents[i][0][j: j + self.LEN_LINE]
                    
                    item_end.text = text
                    item_end.y = item.y + self.ITEM_H
                    item_end.i = i
                    item_end.j = j
                    
                else:
                    break
        else:
            while True:
                item_end = self.items[-1]
                item_start = self.items[0]
                
                if item_start.y >= offset:
                    i = item_start.i
                    j = item_start.j - self.LEN_LINE
                    if i is None:
                        break
                    if j < 0:
                        para, lines = self.contents[i-1]
                        i, j = i - 1, (lines - 1) * self.LEN_LINE
                    
                    if i < 0:
                        break
                    
                    text = self.contents[i][0][j: j + self.LEN_LINE]
                    item_end.text = text
                    
                    item_end.y = item_start.y - self.ITEM_H
                    item_end.i = i
                    item_end.j = j
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
        scrollview = self.reader.scrollview
        off_set = scrollview.content_offset.y
        i = None
        for item in self.reader.items:
            if item.y + item.height > off_set:
                i = item.i
                j = item.j
                break
        if i is None:
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
