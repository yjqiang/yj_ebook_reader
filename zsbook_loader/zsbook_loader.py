import web
from .zsindex_loader import ZSIndexLoader
from .zsbody_loader import ZSBodyLoader


class ZSBookLoader:
    def __init__(self):
        self.body_loader = ZSBodyLoader(self)
        self.index_loader = ZSIndexLoader(self)
                
    def set_url(self, orig):
        # src_id#offset / src_id
        if '#' in orig:
            src_id, offset = orig.split('#')
            offset = int(offset)
        else:
            src_id = orig
            offset = None
        self.index_loader.set_url(src_id)
        self.body_loader.set_url(offset)
        
    def search_books(self, keywords):
        url = f'http://api.zhuishushenqi.com/book/fuzzy-search?query={keywords}&start=0&limit=40'
        json_rsp = web.get(url).json()
        books = json_rsp['books']
        list_books = [(book['_id'], book['author'], book['title']) for book in books]
        return list_books
    
    def fetch_srcs(self, book_id):
        url = f'http://api.zhuishushenqi.com/toc?view=summary&book={book_id}'
        json_rsp = web.get(url).json()
        srcs = []
        for src in json_rsp:
            if src['source'] != 'zhuishuvip':
                srcs.append((src['_id'], src['name'], src['lastChapter'], src['updated']))
        return srcs
        
    def get_chapter_info(self, offset):
        return self.index_loader.get_chapter_info(offset)
        
    def get_srcid(self):
        return self.index_loader.get_srcid()
                
    def get_next_bodydata(self):
        return self.body_loader.get_next_data()
        
    def get_next_indexdata(self):
        return self.index_loader.get_next_data()
