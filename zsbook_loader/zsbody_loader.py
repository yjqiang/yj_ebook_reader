from urllib import parse
import web


class ZSBodyLoader:
    def __init__(self, root):
        self.root = root
        self.url = None
        self.cur_offset = None
        self.headers = {
            "User-Agent": "YouShaQi/4.1.0 (iPhone; iOS 12.1.2; Scale/2.00)",
            "X-User-Agent": "YouShaQi/4.1.0 (iPhone; iOS 12.1.2; Scale/2.00)"
            }
            
    def set_url(self, offset):
        self.cur_offset = offset
            
    # 存取bm用的是index url(格式: src_id!offset),因为api不提供next功能
    # 追书api不分页
    def get_next_data(self):
        if self.cur_offset is None:
            self.cur_offset = 0
        if self.cur_offset >= 0:
            while True:
                # 这里next与ebook里面有区别，set_url其实什么也没做
                if not self.get_next_url():
                    return None, None, None
                self.contents = self.get_content()
                if self.contents:
                    break
                self.cur_offset += 1
            
        if not self.contents:
            return None, None, None
        words = self.contents
        title = self.title
        self.cur_offset += 1
        return words, title, f'{self.root.get_srcid()}#{self.cur_offset-1}'

    def get_content(self):
        
        json_rsp = web.get(self.url, headers=self.headers).json()
        # print(json_rsp)
        if not json_rsp['ok']:
            return []
        chapter = json_rsp['chapter']
        # self.title = chapter['title']
        words = []
        for para in chapter['body'].split('\n'):
            para = para.strip()
            if para:
                para = '　　' + para
                words.append(para)
        return words
        
    def get_next_url(self):
        result = self.root.get_chapter_info(self.cur_offset)
        if result is None:
            return False
        url, self.title = result
        encode_url = parse.quote_plus(url)
        self.url = f'http://chapter2.zhuishushenqi.com/chapter/{encode_url}'
        return True
        
