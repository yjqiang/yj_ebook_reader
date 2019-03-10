from index_viewer.index_viewer import IndexViewer
from ebody_viewer.ebook_body_viewer import EBookBodyViewer
from ebody_viewer.eimg_body_viewer import EImgBodyViewer


class EReader:
    def __init__(self, EBodyViewer, controller):
        self.var_ebody_viewer = EBodyViewer(self)
        self.var_index_viewer = IndexViewer(self)
        self.controller = controller
        
    def req_data_bg(self, var):
        if var is self.var_ebody_viewer:
            self.controller.req_ebody_data_bg()
        elif var is self.var_index_viewer:
            self.controller.req_eindex_data_bg()
    
    def req_data(self, var, init=False):
        if var is self.var_ebody_viewer:
            self.controller.req_ebody_data(init)
        elif var is self.var_index_viewer:
            self.controller.req_eindex_data(init)
            
    def load_data(self, var):
        if var is self.var_ebody_viewer:
            return self.controller.load_ebody_data()
        elif var is self.var_index_viewer:
            return self.controller.load_eindex_data()
            
    def open_url(self, url):
        
        self.controller.load_reader(url, is_init=False)
        
    def set_navi_view_name(self, name):
        self.controller.set_navi_view_name(name)
        
    def reset_view(self, i, j):
        # 先后顺序不能反，因为两个都会调用set_navi_view_name这个api,会覆盖
        self.var_index_viewer.reset_view(i, j)
        self.var_ebody_viewer.reset_view(i, j)
    
    def reset_scrollbar(self):
        self.var_ebody_viewer.reset_scrollbar()
        
    def get_offset(self):
        return self.var_ebody_viewer.get_offset()

                
class EImgReader(EReader):
    def __init__(self, controller):
        super().__init__(EImgBodyViewer, controller)

                
class EBookReader(EReader):
    def __init__(self, controller):
        super().__init__(EBookBodyViewer, controller)
        

