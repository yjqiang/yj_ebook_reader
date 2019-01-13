import web


class ZSIndexLoader:
    def __init__(self, root):
        self.root = root
        self.url = None
        
    def set_url(self, src_id):
        self.src_id = src_id
        self.url = f'http://api.zhuishushenqi.com/toc/{src_id}?view=chapters'
        self.cur_offset = None
        self.all_contents = []
        
    def get_next_data(self, is_for_body_next=False):
        if self.cur_offset is None:
            self.cur_offset = 0
            self.all_contents += self.get_content()
        if self.cur_offset >= len(self.all_contents) and self.cur_offset:
            if not self.get_next_url():
                return None, None
            self.all_contents += self.get_content()
        # index [(index_url, index_name)]
        indexes = []
        for i, content in enumerate(self.all_contents[self.cur_offset:]):
            indexes.append((f'{self.src_id}#{i+self.cur_offset}', content[1]))
        title = ''
        # print(indexes, len(indexes))
        if not is_for_body_next:
            self.cur_offset = len(self.all_contents)
        return indexes, title
        
    def get_content(self):
        json_rsp = web.get(self.url).json()
        list_chapters = json_rsp['chapters']
        chapters = [(chapter['link'], chapter['title']) for chapter in list_chapters]
        # 反序
        # chapters_list = chapterslist[::-1]
        return chapters
            
    def get_chapter_info(self, offset):
        if offset >= len(self.all_contents):
            self.get_next_data(is_for_body_next=True)
        if offset >= len(self.all_contents):
            return None
        return self.all_contents[offset]
        
    # 追书index api不分页
    def get_next_url(self):
        return False
        
    def get_srcid(self):
        return self.src_id
