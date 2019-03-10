import ui


class BmViewer:
    def __init__(self, controller, bms):
        view = ui.load_view('bm_viewer/bookmark')
        tb = view['tableview']

        tb.data_source.items = bms
        tb.data_source.edit_action = controller.del_bm
        self.bm_view = tb
        view.right_btns_desc = 'return'
        self.view = view
        tb.delegate = self
        self.controller = controller
        
    def tableview_did_select(self, bm_view, section, row):
        bm = bm_view.data_source.items[row]
        bm_view.reload()
        if bm['type'] == 'zsbook':
            self.controller.load_zsbook(bm['url'], bm['i'], bm['j'])
        elif bm['type'] == 'ebook':
            self.controller.load_ebook(bm['url'], bm['i'], bm['j'])
        elif bm['type'] == 'eimg':
            self.controller.load_eimg(bm['url'], bm['i'], bm['j'])
        
    def add_new_bm(self, new_bm):
        data_source = self.bm_view.data_source
        data_source.items.append(new_bm)
        return data_source
