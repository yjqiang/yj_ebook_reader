from collections import deque
import ui
import console
from controller import Controller
from e_loader.e_loader import EBookLoader

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
# url = 'https://www.69shu.com/txt/1523/679709'
# url = 'https://m.00xs.cc/mxiaoshuo/3983/9480362/'

# url = 'https://m.snwx8.com/book/210/210159/45857682.html'
# url = 'http://www.xitxt.net/read/19533_12.html'
# url = 'https://www.piaotian.com/html/9/9275/6863827.html'
# url = 'http://m.176xsw.com/7/111/read/99575.html'
# url = 'https://novel.zhwenpg.com/r.php?id=264554'


class ReaderViewer:
    ITEM_H = 32
    LEN_LINE = 19
    LOADING = 'LOADING...'
        
    def __init__(self, controller):
        reader_view = ui.load_view('ebook_reader')
        scrollview = reader_view['scrollview']
        self.scrollview = scrollview
        self.reader_view = reader_view
        for i in range(19):
            scrollview.add_subview(reader_view[f'label{i}'])
        scrollview.delegate = self
        self.items = deque(self.scrollview.subviews)
        assert (len(self.items) - 1) * self.ITEM_H > scrollview.height
        self.cur_offset = 0
        self.controller = controller
        
    def req_data_bg(self):
        self.controller.req_data_bg()
    
    def req_data(self, init=False):
        self.controller.req_data(init)
        
    def set_navi_view_name(self, name):
        self.controller.set_navi_view_name(name)
                
    def load_data(self):
        element = self.controller.load_data()
        if element is None:
            return None
        if element[0] is None:
            # 到底之后不再复位self.has_sent_req
            console.hud_alert('已经阅读完毕')
            return None
        chapter, title, url, init = element
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
        return sum_num_lines
            
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
        
    def reset_view(self, i=0, j=0):
        scrollview = self.scrollview
        self.contents = []
        # (l, r, name)
        self.titles = []
        scrollview.content_size = (scrollview.width, 0)
        
        self.req_data(True)
        sum_num_lines = self.load_data()
        # 其实应该仿照img模块的，但是没必要，白白把逻辑弄麻烦了
        while sum_num_lines <= len(self.items):
            self.req_data()
            sum_num_lines += self.load_data()
        
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
        self.refresh_title()
        
    def get_offset(self):
        scrollview = self.scrollview
        off_set = scrollview.content_offset.y
        i = None
        for item in self.items:
            if item.y + item.height > off_set:
                i = item.i
                j = item.j
                break
        if i is None:
            return
        for l, r, name, url in self.titles:
            if l <= i < r:
                # 本页的i 相对段落数目
                new_bookmark = {
                    'i': i - l,
                    'j': j,
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
        # print('t')
        
        reader_h = scrollview.height
        # print('t')
        
        content_size = scrollview.content_size[1]
        # init的时候取消函数
        if not content_size:
            return
        # 预加载
        if content_size and content_size - self.cur_offset <= 5 * reader_h:
            self.req_data_bg()
        
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
                        self.req_data_bg()
                        i, j = None, None
                        
                    else:
                        text = self.contents[i][0][j: j + self.LEN_LINE]
                        
                    item_start.text = text
                    item_start.y = item_end.y + self.ITEM_H
                    item_start.i = i
                    item_start.j = j
                    self.items.rotate(-1)
                elif item_end.i is None and item_end.y <= offset + reader_h:
                    if self.load_data() is None:
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
                if item_start.y > offset:
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
        self.refresh_title()
    

# url = input('请输入:\n')


controller = Controller(EBookLoader, ReaderViewer)

controller.load_reader(url)
controller.navi_viewer.view.present('fullscreen')

