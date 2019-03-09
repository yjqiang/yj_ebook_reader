import ui
import console
import threading
from queue import Queue
from config_loader import ConfigLoader
from menu_viewer.menu_viewer import MenuViewer
from bm_viewer.bm_viewer import BmViewer
from navi_viewer.navi_viewer import NaviViewer
from zs_search_viewer.zs_search_viewer import ZSSearchViewer
from zs_loader.zs_loader import ZSLoader


class Controller:
    def __init__(self, ELoader, ReaderViewer):
        conf_loader = ConfigLoader()
        dict_conf = conf_loader.dict_conf
        dict_bm = conf_loader.dict_bookmark
        
        self.reader_viewer = ReaderViewer(self)
        self.bm_viewer = BmViewer(self, dict_bm['bookmarks'])
        self.menu_viewer = MenuViewer(self)
        self.var_eloader = ELoader(dict_conf)
        self.navi_viewer = NaviViewer(self, self.reader_viewer.var_ebody_viewer.reader_view)
        self.zs_search_viewer = ZSSearchViewer(self)
        self.var_zsloader = ZSLoader()
        
        self.conf_loader = conf_loader
        self.queue_ebody = Queue()
        self.queue_eindex = Queue()
        self.has_sent_req = False
        self.has_sent_eindex_req = False
        
        self.var_loader = self.var_eloader
        
    def pop2reader_viewer(self):
        self.navi_viewer.pop_view()
        
    def zs_search(self):
        book_id = self.zs_search_viewer.search_books(self.var_zsloader)
        print('最终结果', book_id)

        if book_id is not None:
            self.pop2reader_viewer()
            self.zs_search_viewer.fetch_srcs(self.var_zsloader, book_id)
            self.open_zs_srcs_viewer()
            
        
    def open_menu_viewer(self):
        self.navi_viewer.push_view(self.menu_viewer.view)
        
    def open_bm_viewer(self):
        self.navi_viewer.push_view(self.bm_viewer.view)
        
    def open_zs_srcs_viewer(self):
        self.navi_viewer.push_view(self.zs_search_viewer.view)
        
    def load_zs(self, src_id, i=0, j=0):
        self.var_loader = self.var_zsloader
        self.load_reader(src_id, i, j)
        
    def load_e(self, url, i=0, j=0):
        self.var_loader = self.var_eloader
        self.load_reader(url, i, j)
        
    def open_eindex_viewer(self):
        self.navi_viewer.push_view(self.reader_viewer.var_index_viewer.reader_view)
        
    def set_navi_view_name(self, name):
        self.navi_viewer.view.name = name
        
    def del_bm(self, new_data_src):
        self.conf_loader.refresh_file(new_data_src)
        
    def get_url(self):
        new_bookmark = self.reader_viewer.get_offset()
        if new_bookmark is not None:
            return new_bookmark['url']
        return ''
        
    def load_reader(self, url, i=0, j=0):
        if self.has_sent_req:
            self.t_ebody.join()
        if self.has_sent_eindex_req:
            self.t_eindex.join()
        self.has_sent_req = False
        self.has_sent_eindex_req = False
        # self.queue.clean 之后考虑优雅点
        self.queue_ebody = Queue()
        self.queue_eindex = Queue()
        self.var_loader.set_url(url)
        
        self.reader_viewer.reset_view(i, j)
        
        
        self.pop2reader_viewer()
        ui.animate(self.reader_viewer.reset_scrollbar, 0.5)
     
    def save_bm(self):
        new_bookmark = self.reader_viewer.get_offset()
                        
        is_duplicate = self.conf_loader.check_bookmark(new_bookmark)
        
        if not is_duplicate:
            self.conf_loader.refresh_file(self.bm_viewer.add_new_bm(new_bookmark))
            console.hud_alert(f'已经保存')
        else:
            console.hud_alert('重复操作或者无效书签')
        self.pop2reader_viewer()
            
    def req_ebody_data(self, init=False):
        data = self.var_loader.get_next_bodydata()
        self.queue_ebody.put((*data, init))
        # print('执行')
            
    def req_ebody_data_bg(self):
        if not self.has_sent_req:
            self.has_sent_req = True
            self.t_ebody = threading.Thread(target=self.req_ebody_data)
            self.t_ebody.start()
            
    def req_eindex_data(self, init=False):
        data = self.var_loader.get_next_indexdata()
        self.queue_eindex.put((*data, init))
        # print('执行')
            
    def req_eindex_data_bg(self):
        if not self.has_sent_eindex_req:
            self.has_sent_eindex_req = True
            self.t_eindex = threading.Thread(target=self.req_eindex_data)
            self.t_eindex.start()
            
    def load_ebody_data(self):
        if not self.queue_ebody.empty():
            element = self.queue_ebody.get()
            if element[0] is not None:
                self.has_sent_req = False
            return element
        return None
        
    def load_eindex_data(self):
        if not self.queue_eindex.empty():
            element = self.queue_eindex.get()
            if element[0] is not None:
                self.has_sent_eindex_req = False
            return element
        return None
