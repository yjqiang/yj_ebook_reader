import toml
    
    
class ConfigLoader():
    def __init__(self):
        self.file_conf = 'conf/parser.toml'
        self.dict_conf = self.read_conf()
        self.file_bookmark = 'conf/bookmarks.toml'
        self.dict_bookmark = self.read_bookmark()
        # print(self.dict_conf)
            
    def read_conf(self):
        with open(self.file_conf, encoding="utf-8") as f:
            dict_conf = toml.load(f)
        return dict_conf
        
    def read_bookmark(self):
        with open(self.file_bookmark, encoding="utf-8") as f:
            dict_bookmark = toml.load(f)
        if not dict_bookmark:
            dict_bookmark = {'bookmarks': []}
        return dict_bookmark
        
    def check_bookmark(self, new_bm):
        return new_bm in self.dict_bookmark['bookmarks']
            
    def refresh_file(self, bmview):
        self.dict_bookmark['bookmarks'] = bmview.items
        with open(self.file_bookmark, 'w', encoding="utf-8") as f:
            toml.dump(self.dict_bookmark, f)
        
