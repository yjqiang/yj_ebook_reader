阅读一些在线小说或者漫画

1. 运行main.py
1. 配置文件和书签在conf文件夹里面
1. 解析不可能做到覆盖所有网站，但是除了有特别复杂的js的网站外，理论上都可以调整之后正常支持
1. 本项目的依赖包都写在requirements.txt里面。均可[stash](https://github.com/ywangd/stash)里面用pip安装
    - 此项目使用了beautifulsoup4,但是pythonista自带库比老旧。在安装用`pip install module_name`(stash命令, eg:`pip install beautifulsoup4`)安装之后，用`del sys.modules['module_name']`(py脚本, eg:`del sys.modules['bs4']` )来移除原有依赖(显示`KeyError: bs4`说明已经删除了预装的依赖)，之后重启pythonista会自动切换到新安装的包上,可以用`print(module_name.__file__)`(py脚本, eg: `print(bs4.__file__)`)测试是否正常移除了依赖。(beautifulsoup4缩写bs4，两者是同一个模块，但是上面不能通用）  
    - 本项目使用的requests模块同样已经预装在pythonista中，但是也是过于老旧。更新方法是一口气安装idna、chardet、urllib3、requests（使用pip），中间不得退出app