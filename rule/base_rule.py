class ReRule:
    def __init__(self, string):
        self.string = string
    
    # None / result
    def _find(self, text):
        return self.string.search(text)
   
    # 非list,是iter
    def _findall(self, text):
        return self.string.finditer(text)
        
    def find_raw(self, text, soup, with_string=False):
        result = self._find(text)
        if result is None:
            return None
        return result.group()
        
    # re这里attr不具有实际字面意思，仅仅是为了统一
    def find_attr(self, text, soup, with_string=False):
        result = self._find(text)
        if result is None:
            return None
        return result.group(1)
        
    def findall_raw(self, text, soup, with_string=False):
        results = self._findall(text)
        return [result.group() for result in results]
     
    # 同上
    def findall_attr(self, text, soup, with_string=False):
        results = self._findall(text)
        return [result.group(1) for result in results]

                
class TagRule:
    # None / result
    def _find(self, soup):
        return None
     
    # [] / [result0, …]
    def _findall(self, soup):
        return []
        
    def find_raw(self, text, soup, with_string=False):
        result = self._find(soup)
        if result is None:
            return None
        if not with_string:
            return result
        return result.string
        
    def find_attr(self, text, soup, with_string=False):
        result = self._find(soup)
        if result is None:
            return None
        if not with_string:
            return result[self.attr]
        return result[self.attr], result.string
        
    def findall_raw(self, text, soup, with_string=False):
        results = self._findall(soup)
        if not with_string:
            return results
        return [result.string for result in results]
        
    def findall_attr(self, text, soup, with_string=False):
        results = self._findall(soup)
        if not with_string:
            return [result[self.attr] for result in results]
        return [(result[self.attr], result.string) for result in results]
        
    
class BsRule(TagRule):
    def __init__(self, name, attrs, string, attr):
        self.name = name
        self.attrs = attrs
        self.string = string
        self.attr = attr
        
    # None / result
    def _find(self, soup):
        return soup.find(name=self.name, attrs=self.attrs, string=self.string)
     
    # [] / [result0, …]
    def _findall(self, soup):
        return soup.find_all(name=self.name, attrs=self.attrs, string=self.string)

                                
class CssSelectorRule(TagRule):
    def __init__(self, css_selector, attr):
        self.css_selector = css_selector
        self.attr = attr
    
    # None / result
    def _find(self, soup):
        return soup.select_one(self.css_selector)
   
    # list
    def _findall(self, soup):
        return soup.select(self.css_selector)
