from spider.spider import Spider
from xss.xsstrace import XssTrace
from HTMLtoPDF.html_to_pdf import HTMLtoPDF
class interface(object):
    def __init__(self):
        super(interface, self).__init__()
        self.xss_waring = []

    def spider_interface(self, url):
        spi = Spider(url)
        url_list = spi.start(1)
        return url_list

    def xss_interface(self, url):
        xss = XssTrace(url)
        xss_log, xss_warning = xss.execute_shell_command()
        # print(xss_warning)
        self.xss_waring = xss_warning
        return xss_log, xss_warning

    def download_interface(self, data):
        downloader = HTMLtoPDF()
        for item_data in data:
            downloader.start(item_data)

#
# if __name__ == "__main__":
#     test = interface()
#     data = [
#             ['http://127.0.0.1',
#              'description: this is an apple and a banana.</br>long long long long long long!</br> this is an apple and a banana.</br> this is an apple and a banana.</br>long long long long long long!</br>  this is an apple and a banana.</br>long long long long long long!</br>  this is an apple and a banana.</br>long long long long long long!</br>  this is an apple and a banana.</br>long long long long long long!</br>  this is an apple and a banana.</br>long long long long long long!</br>  this is an apple and a banana.</br>long long long long long long!',
#              '10'],
#             ['http://127.0.0.3', 'description: this is an apple and a banana.</br>I want to be a cat!', '1'],
#             ['http://127.0.0.2', 'description: this is an apple and a banana.</br>I hate everyone firmly.', '7']
#         ]
#     test.download_interface(data=data)