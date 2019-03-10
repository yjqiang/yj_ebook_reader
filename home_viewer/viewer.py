import ui
import console


class HomeViewer:
    def __init__(self, controller):
        self.controller = controller
        view = ui.load_view('home_viewer/home')
        btn_open_bm = view['btn_open_bm']
        btn_open_bm.action = self._open_bm
        
        btn_search_eimg = view['btn_search_eimg']
        btn_search_eimg.action = self._search_eimg
        
        btn_search_ebook = view['btn_search_ebook']
        btn_search_ebook.action = self._search_ebook
        
        btn_search_zsbook = view['btn_search_zsbook']
        btn_search_zsbook.action = self._search_zsbook
        
        view.right_btns_desc = 'empty'
        self.view = view
        
    def _open_bm(self, *args):
        self.controller.pop_1_view()
        self.controller.push_bm_viewer()
        
    def _input_alert(self, title, inputted=None):
        if inputted is None:
            inputted = ''
        try:
            text = console.input_alert(title, '', inputted)
        
            if text:
                return text
        except KeyboardInterrupt:
            return None
        return None
        
    def _search_eimg(self, *args):
        url = self._input_alert('请输入在线漫画的网址')
        if url is not None:
            self.controller.load_eimg(url)

    def _search_ebook(self, *args):
        url = self._input_alert('请输入在线小说的网址')
        if url is not None:
            self.controller.load_ebook(url)
        
    def _search_zsbook(self, *args):
        keywords = self._input_alert('请输入要搜索的书目的关键词')
        if keywords is not None:
            self.controller.search_zsbook(keywords)
        
        
    


