import ui


class MenuViewer:
    def __init__(self, controller):
        self.controller = controller
        self.view = ui.load_view('menu_viewer/menu')
        save_bm_btn = self.view['save_bm_btn']
        save_bm_btn.action = self.save_bm
        show_bm_btn = self.view['show_bm_btn']
        show_bm_btn.action = self.open_bm_viewer
        
    def save_bm(self, sender):
        self.controller.save_bm()
        
    def open_bm_viewer(self, sender=None):
        self.controller.pop2reader_viewer()
        self.controller.open_bm_viewer()
