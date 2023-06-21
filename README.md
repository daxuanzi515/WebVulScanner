# README

基于 `python 3.8.0`

使用`pip install -r requirements.txt`安装依赖

修改config.config.py里的config.ini的绝对路径，并且在config.ini里编辑你的项目绝对路径

需要手动安装`wkhtmltopdf`应用 否则无法使用导出PDF文件功能

如果没有文件夹：
**手动建立文件夹：在main下建立log和pdf文件夹，在log里建立xss/csrf...等文件夹**

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

