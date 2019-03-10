import threading
from queue import Queue

import ui
import console

from home_viewer.viewer import HomeViewer
from zsbook_loader.zsbook_loader import ZSBookLoader
from zsbook_search_viewer.viewer import ZSBookSearchViewer
from menu_viewer.viewer import MenuViewer
from bm_viewer.bm_viewer import BmViewer
from e_loader.e_loader import EBookLoader, EImgLoader
from ereader import EBookReader, EImgReader
from config_loader import ConfigLoader


class Controller:
    def __init__(self):
        conf_loader = ConfigLoader()
        dict_conf = conf_loader.dict_conf
        dict_bm = conf_loader.dict_bookmark
        self.conf_loader = conf_loader
        
        self.bm_viewer = BmViewer(self, dict_bm['bookmarks'])
        
        # init viewers
        self.var_zsbook_search_viewer = ZSBookSearchViewer(self)
        
        self.var_menu_viewer = MenuViewer(self)
        
        self.var_book_viewer = EBookReader(self)
        self.var_img_viewer = EImgReader(self)
        self.reader_viewer = None
                
        self.var_zsbook_loader = ZSBookLoader()
        self.var_ebook_loader = EBookLoader(dict_conf)
        self.var_eing_loader = EImgLoader(dict_conf)
        self.var_loader = None
        self.curr_type = None
                
        bottom_view = HomeViewer(self).view
        view = ui.NavigationView(bottom_view)
        self.stack_views = [bottom_view]  # 额外保存，用于读取navigation view栈内信息
        
        view.navigation_bar_hidden = True
        
        btn_item_pop = ui.ButtonItem(
            image=ui.Image.named('iob:arrow_return_left_24'))
        btn_item_pop.action = self.pop_1_view
        
        btn_item_push_menu = ui.ButtonItem(
            image=ui.Image.named('iob:navicon_round_24'))
        btn_item_push_menu.action = self.push_menu_view
        
        self.btn_items_pop = [btn_item_pop]
        self.btn_items_push_menu = [btn_item_push_menu]
        
        self.view = view
        self.set_right_button_items(bottom_view.right_btns_desc)
        
        self.queue_body = None
        self.queue_index = None
        self.is_req_body = False
        self.is_req_index = False
        
    def set_navi_view_name(self, name):
        self.view.name = name
                    
    # 设置navigation view的右上角的图标群
    def set_right_button_items(self, right_btns_desc):
        if right_btns_desc is None:
            return
        if right_btns_desc == 'return':
            self.view.right_button_items = self.btn_items_pop
        elif right_btns_desc == 'menu':
            self.view.right_button_items = self.btn_items_push_menu
        elif right_btns_desc == 'empty':
            self.view.right_button_items = []
               
    # 和push_1_view+push_menu_view对应，不需要view，所以就合并了
    def pop_1_view(self, *args):
        if len(self.stack_views) > 1:  # 如果栈非最底的时候
            self.view.pop_view()
            self.stack_views.pop()
            view = self.stack_views[-1]
            self.set_right_button_items(view.right_btns_desc)
        
    def pop_all_view(self):  # 这个sb有bug，连着pop会失效？我佛了
        if len(self.stack_views) >= 4:
            return False
        while len(self.stack_views) > 1:
            self.pop_1_view()
            
    def push_1_view(self, view):
        self.view.push_view(view)
        self.stack_views.append(view)
        self.set_right_button_items(view.right_btns_desc)
        
    def push_menu_view(self, *args):
        self.push_1_view(self.var_menu_viewer.view)
        
    def push_index_viewer(self):
        self.push_1_view(self.reader_viewer.var_index_viewer.view)
        
    def push_bm_viewer(self):
        self.push_1_view(self.bm_viewer.view)
        
    def search_zsbook(self, keywords):
        book_id = self.var_zsbook_search_viewer.search_books(
            self.var_zsbook_loader, keywords)
        print('最终结果', book_id)

        if book_id is not None:
            self.var_zsbook_search_viewer.fetch_srcs(
                self.var_zsbook_loader, book_id)
            self.push_1_view(self.var_zsbook_search_viewer.view)
            
    def load_zsbook(self, src_id, i=0, j=0):
        self.var_loader = self.var_zsbook_loader
        self.curr_type = 'zsbook'
        self.reader_viewer = self.var_book_viewer
        self.pop_all_view()
        self.load_reader(src_id, i, j)
        
    def load_ebook(self, url, i=0, j=0):
        self.var_loader = self.var_ebook_loader
        self.curr_type = 'ebook'
        self.reader_viewer = self.var_book_viewer
        self.pop_all_view()
        self.load_reader(url, i, j)
        
    def load_eimg(self, url, i=0, j=0):
        self.var_loader = self.var_eing_loader
        self.curr_type = 'eimg'
        self.reader_viewer = self.var_img_viewer
        self.pop_all_view()
        self.load_reader(url, i, j)
        
    def load_reader(self, url, i=0, j=0, is_init=True):
        if self.is_req_body:
            self.thread_req_body.join()
        if self.is_req_index:
            self.thread_req_index.join()
        self.is_req_body = False
        self.is_req_index = False
        # self.queue.clean
        self.queue_body = Queue()
        self.queue_index = Queue()
        self.var_loader.set_url(url)
        
        self.reader_viewer.reset_view(i, j)
        if is_init:  # 如果是初始化那么需要pu sh
            self.push_1_view(self.reader_viewer.var_ebody_viewer.view)
        else:
            self.pop_1_view()
        ui.animate(self.reader_viewer.reset_scrollbar, 0.5)
  
    def save_bm(self):
        new_bm = self.reader_viewer.get_offset()
                        
        is_duplicate = self.conf_loader.check_bookmark(new_bm)
        
        if not is_duplicate:
            new_bm = {**new_bm, 'type': self.curr_type}
            self.conf_loader.refresh_file(self.bm_viewer.add_new_bm(new_bm))
            console.hud_alert(f'已经保存')
        else:
            console.hud_alert('重复操作或者无效书签')
        self.pop_1_view()
        
    def get_url(self):
        new_bm = self.reader_viewer.get_offset()
        if new_bm is not None:
            return new_bm['url']
        return ''
    
    def del_bm(self, new_data_src):
        self.conf_loader.refresh_file(new_data_src)
            
    def req_ebody_data(self, init=False):
        data = self.var_loader.get_next_bodydata()
        self.queue_body.put((*data, init))
        # print('执行')
            
    def req_ebody_data_bg(self):
        if not self.is_req_body:
            self.is_req_body = True
            self.thread_req_body = threading.Thread(target=self.req_ebody_data)
            self.thread_req_body.start()
            
    def req_eindex_data(self, init=False):
        data = self.var_loader.get_next_indexdata()
        self.queue_index.put((*data, init))
        # print('执行')
            
    def req_eindex_data_bg(self):
        if not self.is_req_index:
            self.is_req_index = True
            self.thread_req_index = threading.Thread(
                target=self.req_eindex_data)
            self.thread_req_index.start()
            
    def load_ebody_data(self):
        if not self.queue_body.empty():
            element = self.queue_body.get()
            if element[0] is not None:
                self.is_req_body = False
            return element
        return None
        
    def load_eindex_data(self):
        if not self.queue_index.empty():
            element = self.queue_index.get()
            if element[0] is not None:
                self.is_req_index = False
            return element
        return None
        
        
Controller().view.present('fullscreen')
