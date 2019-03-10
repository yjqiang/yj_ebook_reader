import console
import ui


class ZSBookSearchViewer:
    def __init__(self, controller):
        self.controller = controller
        view = ui.load_view('zsbook_search_viewer/src_index')
        tb = view['tableview']

        tb.data_source.items = []
        self.tb = tb
        view.right_btns_desc = 'return'
        self.view = view
        tb.delegate = self
        
    def tableview_did_select(self, bm_view, section, row):
        src_id = self.srcs[row][0]
        print(src_id)
        self.controller.load_zsbook(src_id)
        return src_id
        
    # 返回bookid
    def search_books(self, zs_loader, keywords):
        list_books = zs_loader.search_books(keywords)
        list_msg = []
        for i, values in enumerate(list_books):
            _, author, title = values
            list_msg.append(f'{i}.{author}：《{title}》')
        str_msg = '\n'.join(reversed(list_msg))
        try:
            i = int(console.input_alert('请输入index的号码', str_msg, hide_cancel_button=True))
        except KeyboardInterrupt:
            return
        except ValueError:
            return
        return list_books[i][0]
        
    def tableview_accessory_button_tapped(self, tb_view, _, row):
        # section datasrc为single的
        src = self.srcs[row]
        msg = f'最新章节{src[2]}({src[3]})'
        console.hud_alert(msg)
        
    def fetch_srcs(self, zs_loader, book_id):
        srcs = zs_loader.fetch_srcs(book_id)
        items = [{'title': src[1], 'accessory_type': 'detail_button'} for src in srcs]
        self.srcs = srcs
        self.tb.data_source.items = items
        return True
        
    
        
