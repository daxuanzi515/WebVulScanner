# README

基于 `python 3.8.0`

使用`pip install -r requirements.txt`安装依赖

修改config.config.py里的config.ini的绝对路径，并且在config.ini里编辑你的项目绝对路径

需要手动安装`wkhtmltopdf`应用 否则无法使用导出PDF文件功能

如果没有文件夹：
**手动建立文件夹：在main下建立log和pdf文件夹，在log里建立xss文件夹**

```python
self.table_data=
[
    [item_data0],
    [item_data1],
    ...,
    [item_dataN]
]
# 检测单元的子项
item_dataN =
[
    ['web0','description0','level0'],
    ...,
    ['webN','descriptionN','levelN']
]

example:
    # xss检测
    item_xss =
    [
        ['http://127.0.0.1','Your Description:XXXXX','7'],
        ['http://127.0.2.1','Your Description:XXXXX','9'],
        ['http://127.0.1.1','Your Description:XXXXX','8'],
        ['http://192.0.9.1','Your Description:XXXXX','7'],
        ...,
        ['http://192.0.9.1','Your Description:XXXXX','7']
    ]
```

你需要把你的`item_data`组装成上述模式，否则无法嵌入项目的数据显示功能



`XSS`漏洞检测：

```python
# xss 反射型
# GET
http://localhost:8080/pikachu/vul/xss/xss_reflected_get.php
# POST
http://localhost:8080/pikachu/vul/xss/xsspost/post_login.php?username=admin&password=123456&submit=submit

# xss DOM型
http://localhost:8080/pikachu/vul/xss/xss_dom.php
http://localhost:8080/pikachu/vul/xss/xss_dom_x.php
http://localhost:8080/dvwa/vulnerabilities/xss_d/?default=Spanish
        
# xss 存储型
http://localhost:8080/pikachu/vul/xss/xss_stored.php
http://localhost:8080/dvwa/vulnerabilities/xss_s/
        
# xss 盲打
http://localhost:8080/pikachu/vul/xss/xssblind/xss_blind.php

# xss 带参
# xss 过滤
http://localhost:8080/pikachu/vul/xss/xss_01.php?message=1111111&submit=submit
# xss js输出
http://localhost:8080/pikachu/vul/xss/xss_04.php?message=kobe&submit=submit
```



`Phish`思路

```python
# 查询总站
https://phishtank.org

# 存活的钓鱼链接
url_list = [
        'http://myvirgin-mobile-login.com/',# 手机购买表单 需要事先人机验证
        'http://myvirgin-mobile-login.com/profile.php', # 手机购买个人信息 需要事先人机验证
        'https://freefireevent2023.github.io/spin/', # 登录ID表单
        'https://systemcesure.buzz/portalserver/bancanetempresarial/index/public/', # 伪造公司介绍面
        'https://login.busiinesshellp.click/',# facebook 登录界面
        'http://192.168.43.135/',# 本机kali的twitter 登录界面
        'https://psyopclaim.space/' # ape币 猿币交易
    ]

# 字典列表
keywords = ['登录', '邮箱', '钱包', '密码', '注册', '电话号码', ..., '助词']
```



`A.` 文字识别

自动化工具`selenium`后台打开网页截屏

你需要一个助推器 `chrome_driver.exe` [下载](http://chromedriver.storage.googleapis.com/index.html) 根据自己的浏览器版本下载并加入环境变量

截屏内容放入`ocr`识别模型, 得到文字列表`word_list`

根据敏感词字典匹配文字，计算占比

`B.` 分析源码

向浏览器获取网址源码

探测是否存在表单或者跳转链接

`C.` 根据规则判定钓鱼危险等级

规则....
