from .ebody_loader import EBookBodyLoader, EImgBodyLoader
from .eindex_loader import EIndexLoader
from rule.rule import WebsiteRule


class EBookLoader:
    def __init__(self, list_confs):
        self.list_confs = list_confs
        self.cache = {}
        rule = WebsiteRule()
        
        self.body_loader = EBookBodyLoader(self.cache, rule.body_rule, rule)
        self.index_loader = EIndexLoader(self.cache, rule.index_rule, rule)
        self.rule = rule
                
    def set_url(self, url):
        self.url = url
        for i in self.list_confs['websites']:
            if i['url'] in url:
                conf = i
                break
        else:
            conf = None
        
        self.rule.set_rule(conf)
        self.body_loader.set_url(url)
        index_url = self.body_loader.get_index_url()
        self.index_loader.set_url(index_url)
        
    def get_next_bodydata(self):
        return self.body_loader.get_next_data()
        
    def get_next_indexdata(self):
        return self.index_loader.get_next_data()
                
            
class EImgLoader(EBookLoader):
    def __init__(self, list_confs):
        self.list_confs = list_confs
        self.cache = {}
        rule = WebsiteRule()
        
        self.body_loader = EImgBodyLoader(self.cache, rule.body_rule, rule)
        self.index_loader = EIndexLoader(self.cache, rule.index_rule, rule)
        self.rule = rule
        
