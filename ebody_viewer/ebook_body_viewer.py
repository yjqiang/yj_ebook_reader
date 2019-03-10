from collections import deque
import ui
import console


class EBookBodyViewer:
    ITEM_H = 32
    LEN_LINE = 19
    LOADING = 'LOADING...'
        
    def __init__(self, parent):
        view = ui.load_view('ebody_viewer/ebook_body')
        scrollview = view['scrollview']
        self.scrollview = scrollview
        view.right_btns_desc = 'menu'
        self.view = view
        for i in range(19):
            scrollview.add_subview(view[f'label{i}'])
        scrollview.delegate = self
        self.items = deque(self.scrollview.subviews)
        assert (len(self.items) - 1) * self.ITEM_H > scrollview.height
        self.cur_offset = 0
        self.parent = parent
        
    def req_data_bg(self):
        self.parent.req_data_bg(self)
    
    def req_data(self, init=False):
        self.parent.req_data(self, init)
        
    def set_navi_view_name(self, name):
        self.parent.set_navi_view_name(name)
                
    def load_data(self):
        element = self.parent.load_data(self)
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
