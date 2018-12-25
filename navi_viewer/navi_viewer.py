import ui


class NaviViewer:
    def __init__(self, controller, reader_view):
        self.controller = controller
        nav_view = ui.NavigationView(reader_view)
        nav_view.navigation_bar_hidden = True
        
        return_btn_img = ui.Image.named('iob:arrow_return_left_24')
        return_btn_item = ui.ButtonItem(image=return_btn_img)
        return_btn_item.action = self.pop2reader_viewer
        
        menu_btn_img = ui.Image.named('iob:navicon_round_24')
        menu_btn_item = ui.ButtonItem(image=menu_btn_img)
        menu_btn_item.action = self.open_menu_viewer
        
        self.return_btn_items = [return_btn_item]
        self.menu_btn_items = [menu_btn_item]
        
        nav_view.right_button_items = self.menu_btn_items
        self.view = nav_view
        
    def open_menu_viewer(self, sender=None):
        self.controller.open_menu_viewer()
        
    def pop2reader_viewer(self, sender=None):
        self.controller.pop2reader_viewer()
     
    # 最多两层，push进去就肯定是覆盖了readerview
    def push_view(self, view):
        self.view.push_view(view)
        self.view.right_button_items = self.return_btn_items
    
    # 类似上面原因，pop之后肯定漏出reader_view,pop超了保持原样,api不会发生错误
    def pop_view(self):
        self.view.pop_view()
        self.view.right_button_items = self.menu_btn_items
