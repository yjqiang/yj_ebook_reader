import ui


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
        open_url_button = self.view['open_url_button']
        open_url_button.action = self.open_url
        self.url_textfield = self.view['url_textfield']
        
        
    def button_selected_look(self, btn):
        btn.background_color = 0.5
        
    def button_done_look(self, btn):
        btn.background_color = 0
         
    def save_bm(self, sender):
        self.controller.save_bm()
        
    def open_url(self, sender):
        url = self.url_textfield.text
        if url:
            self.controller.load_reader(url)
            
    def set_url_textfield_text(self, text):
        self.url_textfield.text = text
        
    def open_bm_viewer(self, sender=None):
        self.button_selected_look(sender)
        self.controller.pop2reader_viewer()
        self.controller.open_bm_viewer()
        
    def open_eindex_viewer(self, sender):
        self.controller.pop2reader_viewer()
        self.controller.open_eindex_viewer()
