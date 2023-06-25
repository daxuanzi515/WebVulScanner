from spider.spider import Spider
from xss.xsstrace import XssTrace
from csrf.csrftrace import Csrf
from bruteforce.brutetrace import BruteForce
from HTMLtoPDF.html_to_pdf import HTMLtoPDF
from phish.phish import PhishDetector


class interface(object):
    def __init__(self, config_ini):
        super(interface, self).__init__()
        self.config_ini = config_ini
        self.image_data = []

    def spider_interface(self, url):
        spi = Spider(url)
        url_list = spi.start(1)
        return url_list

    def xss_interface(self, url):
        xss = XssTrace(url, self.config_ini)
        xss_log, xss_warning = xss.execute_shell_command()
        return xss_log, xss_warning

    def phish_interface(self, url):
        phish_detector = PhishDetector(self.config_ini)
        phish_detector.from_screen_To_ocr_result(url=url)
        log_word, warning = phish_detector.level_judge_operator(url=url)
        self.image_data = phish_detector.image_data
        return log_word, warning

    def csrf_interface(self, url):
        csrf = Csrf(url, self.config_ini)
        csrf_log, csrf_warning = csrf.execute_shell_command()
        return csrf_log, csrf_warning

    def brute_interface(self, url):
        brute = BruteForce(url, self.config_ini)
        m, name, passw, others = brute.scan()
        brute_warning, brute_log = brute.brute(m, name, passw, others)
        return brute_log, brute_warning

    def download_interface(self, data):
        downloader = HTMLtoPDF(self.config_ini)
        for item_data in data:
            downloader.start(item_data)

    def draw_image_interface(self):
        from PIL import Image
        import time
        from paddleocr.tools.infer.utility import draw_ocr
        image_data = self.image_data
        if not image_data:
            # print('图片数据为空！')
            return "图片数据为空，请点击钓鱼网站检测之后再来查看图片!\n"
        else:
            # print('请耐心等待图片生成....\n')
            current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            for index, item in enumerate(image_data):
                image = Image.open(item[0]).convert('RGB')
                path = self.config_ini['main_project']['project_path'] + self.config_ini['phish']['phish_out_img'] \
                       + r'/ocr_screenshot_{}_{}.png'.format(current_time, index)
                im_show = draw_ocr(image, [line[0] for line in item[1]], [line[1][0] for line in item[1]],
                                   [line[1][1] for line in item[1]],
                                   font_path=self.config_ini['main_project']['project_path'] +
                                             self.config_ini['components']['tff'])
                ocr_img = Image.fromarray(im_show)
                ocr_img.save(path)
            # print('生成图片完毕!')
            return '~~生成图片完毕~~\n'
