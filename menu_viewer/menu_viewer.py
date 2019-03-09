import ui
import console


class MenuViewer:
    def __init__(self, controller):
        self.controller = controller
        self.view = ui.load_view('menu_viewer/menu')
        save_bm_btn = self.view['save_bm_btn']
        save_bm_btn.action = self.save_bm
        show_bm_btn = self.view['show_bm_btn']
        show_bm_btn.action = self.open_bm_viewer
        show_eindex_btn = self.view['show_index_btn']
        show_eindex_btn.action = self.open_eindex_viewer
        open_url_btn = self.view['open_url_btn']
        self.open_url_btn = open_url_btn
        open_url_btn.action = self.open_url
        zs_search_btn = self.view['zs_search_btn']
        self.zs_search_btn = zs_search_btn
        zs_search_btn.action = self.zs_search
                
    def button_selected_look(self, btn):
        btn.background_color = 0.5
        
    def button_done_look(self, btn):
        btn.background_color = 0
         
    def zs_search(self, btn):
        self.controller.zs_search()
    
    def save_bm(self, sender):
        self.controller.save_bm()
        
    def open_url(self, sender):
        try:
            url = console.input_alert(f'请输入url', '', self.controller.get_url())
        
            if url and url != self.controller.get_url():
                
                self.controller.load_e(url)
        except KeyboardInterrupt:
            pass
        
    def open_bm_viewer(self, sender=None):
        self.button_selected_look(sender)
        self.controller.pop2reader_viewer()
        self.controller.open_bm_viewer()
        
    def open_eindex_viewer(self, sender):
        self.controller.pop2reader_viewer()
        self.controller.open_eindex_viewer()
