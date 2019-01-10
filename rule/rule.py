from .base_rule import ReRule, CssSelectorRule, BsRule
        
        
class PageRule:
    def get_rule(self, dict_rule, def_key=None, def_name=None):
        if 're' in dict_rule:
            string = dict_rule['re']
            return ReRule(string)
        elif 'css_selector' in dict_rule:
            css_selector = dict_rule['css_selector']
            attr = dict_rule.get('key', def_key)
            return CssSelectorRule(css_selector, attr)
        else:
            name = dict_rule.get('name', def_name)
            attrs = dict_rule.get('attrs', {})
            if 'string' in dict_rule:
                string = dict_rule['string']
            else:
                string = None
            attr = dict_rule.get('key', def_key)
            return BsRule(name, attrs, string, attr)
        
    def set_title_rule(self, conf):
        dict_rule = conf.get('title', {})
        self.title = self.get_rule(dict_rule, def_name='title')
        
    def set_next_rule(self, conf):
        # 没有表示只有一页,比如某些index页
        list_rules = conf.get('next', None)
        if list_rules is None:
            self.next = None
        else:
            self.next = []
            for dict_rule in list_rules:
                self.next.append(self.get_rule(dict_rule, def_key='href'))
    
    def set_content_rule(self, conf):
        list_rules = conf['content']
        self.content = []
        for dict_rule in list_rules:
            self.content.append(self.get_rule(dict_rule, def_key='src'))
            
    def set_index_rule(self, conf):
        # 没有表示无法连通index
        dict_rule = conf.get('index', None)
        if dict_rule is None:
            self.index = None
        else:
            self.index = self.get_rule(dict_rule, def_key='href')
        
        
class BodyRule(PageRule):
    def set_rule(self, conf):
        self.set_title_rule(conf)
        self.set_content_rule(conf)
        self.set_next_rule(conf)
        self.set_index_rule(conf)

                
class IndexRule(PageRule):
    def set_rule(self, conf):
        # 没有rule的里面一定没有body.index参数，所以无所谓
        if conf is None:
            return
        self.set_title_rule(conf)
        self.set_content_rule(conf)
        self.set_next_rule(conf)
        
    
class WebsiteRule:
    def __init__(self):
        user_agent = ('Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like'
                      'Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko)'
                      'CriOS/65.0.3325.152 Mobile/15D100 Safari/604.1')

        self.ori_headers = {'User-Agent': user_agent}
        self.body_rule = BodyRule()
        self.index_rule = IndexRule()
        
    def set_rule(self, conf):
        self.url = conf['url']
        self.encoding = conf.get('encoding', None)
        self.headers = {**self.ori_headers, **conf.get('headers', {})}
        self.body_rule.set_rule(conf['body'])
        self.index_rule.set_rule(conf.get('index', None))
