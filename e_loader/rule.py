import re
        

class PageRule:
    def get_rule(self, dict_rule, def_key=None, def_name=None):
        re_body = dict_rule.get('re_body', None)
        if re_body is not None:
            result = {
                're_body': re_body
            }
        else:
            name = dict_rule.get('name', def_name)
            
            attrs = dict_rule.get('attrs', {})
            
            string_pattern = dict_rule.get('string', None)
            if string_pattern is None:
                string = None
            else:
                string = re.compile(string_pattern)
                
            key = dict_rule.get('key', def_key)
            
            result = {
                'name': name,
                'attrs': attrs,
                'string': string,
                'key': key
            }
        return result
        
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
        self.print_rule()
        
    def print_rule(self):
        print('url', self.url)
        print('encoding', self.encoding)
        print('body.title', self.body_rule.title)
        print('body.content', self.body_rule.content)
        print('body.next', self.body_rule.next)
        print('body.index', self.body_rule.index)
        
