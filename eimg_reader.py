from ereader import EImgReader
from e_loader.e_loader import EImgLoader
from controller import Controller

url = 'https://e-hentai.org/s/9962198a63/1300988-2'
# url = 'https://m.k886.net/look/name/SuperDick/cid/36391/id/339212/p/2'
# url = 'https://raws.mangazuki.co/manga/desire-king/81'
# url = 'http://www.177pic.info/html/2018/04/1999461.html/19'
# url = 'https://manhwahand.com/manhwa/desire-king/chapter-30?style=list'
# url = 'https://nhentai.net/g/249922/2/'
# url = 'https://mangapark.me/manga/love-parameter-kkun/s1/c104/2'
# url = 'https://www.taadd.com/chapter/HMate59/798722-21.html'
# url = 'https://original-work.simply-hentai.com/%E5%AE%B6%E6%97%8F%E3%81%AE%E3%81%9F%E3%82%81%E3%81%AB-%E5%89%8D%E7%B7%A8/page/6360412'
# url = 'https://manganelo.com/chapter/hcampus/chapter_55'
# url = 'https://www.wnacg.org/photos-view-id-4901546.html'
# url = 'https://manhwahentai.com/manhwa/the-sharehouse/chapter-31/?style=list'
     
        
controller = Controller(EImgLoader, EImgReader)

controller.load_reader(url)
controller.navi_viewer.view.present('fullscreen')


