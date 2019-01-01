from ereader import EBookReader
from e_loader.e_loader import EBookLoader
from controller import Controller


url = 'http://www.luoxia.com/doupo/20982.htm'
# url = 'https://www.xbookcn.com/book/chest/14.htm'
# url = 'http://www.mfxsydw.com/book/15811/9005.html'
# url = 'https://www.piaotian.com/html/9/9866/6782548.html'
# url = 'https://m.qu.la/book/5210/10639876.html'
# 网站挂了
# url = 'http://www.176novel.com/wapbook5713/3736669/'

# url = 'https://m.hunhun520.com/book/wuxianHchuanyue/15134674.html'
# url = 'http://www.luoqiu.com/read/1/373549.html'
# url = 'https://www.69shu.com/txt/1523/679709'
# url = 'https://m.00xs.cc/mxiaoshuo/3983/9480362/'

# url = 'https://m.snwx8.com/book/210/210159/45857682.html'
# url = 'http://www.xitxt.net/read/19533_12.html'
# url = 'http://m.176xsw.com/7/111/read/99575.html'
# url = 'https://novel.zhwenpg.com/r.php?id=1736'
# url = 'http://quanben-xiaoshuo.com/n/wuxiashijiedachuanyue/7.html'

        
controller = Controller(EBookLoader, EBookReader)

controller.load_reader(url)
controller.navi_viewer.view.present('fullscreen')



