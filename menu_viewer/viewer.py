import ui
import dialogs


class MenuViewer:
    def __init__(self, controller):
        self.controller = controller
        view = ui.load_view('menu_viewer/menu')
        
        btn_save_bm = view['btn_save_bm']
        btn_save_bm.action = self.save_bm
        
        btn_go_home = view['btn_go_home']
        btn_go_home.action = self.go_home
        
        btn_show_index = view['btn_show_index']
        btn_show_index.action = self.show_index
        
        btn_get_url = view['btn_get_url']
        btn_get_url.action = self.get_url
        
        view.right_btns_desc = 'return'
        self.view = view
    
    def save_bm(self, *args):
        self.controller.save_bm()
        
    def go_home(self, *args):
        self.controller.pop_all_view()
        self.controller.set_navi_view_name('')
        
    def show_index(self, *args):
        self.controller.pop_1_view()
        self.controller.push_index_viewer()
        
    def get_url(self, *args):
        url = self.controller.get_url()
        dialogs.share_url(url)
