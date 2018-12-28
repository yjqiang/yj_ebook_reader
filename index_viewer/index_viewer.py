from collections import deque
import ui
import console


class IndexViewer:
    ITEM_H = 32
    LEN_LINE = 19
    LOADING = 'LOADING...'
        
    def __init__(self, parent):
        reader_view = ui.load_view('index_viewer/index')
        scrollview = reader_view['scrollview']
        
        for i in range(19):
            button = reader_view[f'button{i}']
            scrollview.add_subview(button)
            button.action = self.open_url
        self.has_sent_req = False
        self.scrollview = scrollview
        self.reader_view = reader_view
        scrollview.delegate = self
        self.items = deque(self.scrollview.subviews)
        assert (len(self.items) - 1) * self.ITEM_H > scrollview.height
        self.parent = parent
        
    def open_url(self, sender):
        if sender.url is not None:
            self.parent.open_url(sender.url)
            console.hud_alert(sender.url)
        
    def req_data_bg(self):
        self.parent.req_data_bg(self)
    
    def req_data(self, init=False):
        self.parent.req_data(self, init)
        
    def set_navi_view_name(self, name):
        self.parent.set_navi_view_name(name)
        
    def refresh_title(self):
        pass
             
    def load_data(self):
        element = self.parent.load_data(self)
        if element is None:
            return None
        if element[0] is None:
            if not element[2]:
                # 到底之后不再复位self.has_sent_req
                console.hud_alert('已经阅读完毕')
            return None
        chapter, title, init = element
        sum_num_lines = 0 if init else 1
        if init:
            self.set_navi_view_name(title)
        for para in chapter:
            sum_num_lines += 1
            self.contents.append((para))
        
        split_contents = '—' * self.LEN_LINE
        self.contents.append((None, split_contents))
        
        self.scrollview.content_size += (0, sum_num_lines * self.ITEM_H)
        self.has_sent_req = False
        return sum_num_lines
        
    def reset_view(self, i=0, j=0):
        scrollview = self.scrollview
        # 这里把offset归零了,并调用了函数
        scrollview.content_size = (scrollview.width, 0)
        
        self.cur_offset = 0
            
        self.contents = []

        self.req_data(True)
        sum_num_lines = self.load_data()
        if sum_num_lines is None:
            for item in self.items:
                item.title = ''
                item.url = None
                
            self.items[0].title = '无目录'
            self.items[0].y = 0
            
            return
        # 其实应该仿照img模块的，但是没必要，白白把逻辑弄麻烦了
        while sum_num_lines <= len(self.items):
            self.req_data()
            sum_num_lines += self.load_data()
        
        i = 0
        y = 0
        for item in self.items:
            item.url, item.title = self.contents[i]
            # i代表段落index，j代表了段落里面具体的文字起始下标
            item.i = i
            item.j = j
            item.y = y
            i += 1
            y += self.ITEM_H
            
    def reset_scrollbar(self):
        pass
        
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
            self.req_data_bg()
        
        # 滚动条下移
        if is_scroll_down:
            while True:
                item_end = self.items[-1]
                item_start = self.items[0]
                if item_end.y + self.ITEM_H -reader_h < offset and item_end.i is not None:
                    i = item_end.i + 1
                    if i >= len(self.contents):
                        title = self.LOADING
                        self.req_data_bg()
                        i = None
                        url = None
                        
                    else:
                        url, title = self.contents[i]
                        
                    item_start.title = title
                    item_start.y = item_end.y + self.ITEM_H
                    item_start.i = i
                    item_start.url = url
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
                
                if item_start.y >= offset:
                    i = item_start.i
                    if i is None or i <= 0:
                        break
                    
                    i = i - 1
                    url, text = self.contents[i]
                    item_end.title = text
                    
                    item_end.y = item_start.y - self.ITEM_H
                    item_end.i = i
                    item_end.url = url
                    self.items.rotate(1)
                    
                else:
                    break
        self.refresh_title()

'''

controller = Controller(EBookLoader, IndexViewer)

controller.load_reader(url)
controller.navi_viewer.view.present('fullscreen')
'''
