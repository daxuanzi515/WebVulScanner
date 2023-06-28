






class interface(object):
    def __init__(self, config_ini):
        super(interface, self).__init__()
        self.config_ini = config_ini
        self.image_data = []

    def spider_interface(self, url):
        from spider.spider import Spider
        spi = Spider(url)
        url_list = spi.start(1)
        return url_list

    def xss_interface(self, url):
        from xss.xsstrace import XssTrace
        xss = XssTrace(url, self.config_ini)
        xss_log, xss_warning = xss.execute_shell_command()
        return xss_log, xss_warning

    def csrf_interface(self, url):
        from csrf.csrftrace import Csrf
        csrf = Csrf(url, self.config_ini)
        csrf_log, csrf_warning = csrf.execute_shell_command()
        return csrf_log, csrf_warning

    def phish_interface(self, url):
        from phish.phish import PhishDetector
        phish_detector = PhishDetector(self.config_ini)
        phish_detector.from_screen_To_ocr_result(url=url)
        log_word, warning = phish_detector.level_judge_operator(url=url)
        self.image_data.append(phish_detector.image_data)
        return log_word, warning

    def brute_interface(self, url):
        from bruteforce.brutetrace import BruteForce
        brute = BruteForce(url, self.config_ini)
        m, name, passw, others = brute.scan()
        brute_warning, brute_log = brute.brute(m, name, passw, others)
        return brute_log, brute_warning

    def sql_interface(self, url):
        from sql.sqlinject import SqlInject
        sql = SqlInject(url, self.config_ini)
        sql_log, sql_warning = sql.detect()
        return sql_log, sql_warning

    def bypass_interface(self, url):
        from bypass.formbypass import formBypass
        bypass = formBypass(url, self.config_ini)
        bypass_log, bypass_warning = bypass.bypassDetect()
        return bypass_log, bypass_warning

    def fileinclu_interface(self, url):
        from fileinclu.fileinclude import fileInclude
        fileinclu = fileInclude(url, self.config_ini)
        fileinclu_log, fileinclu_warning = fileinclu.fileInclusionDetect()
        return fileinclu_log, fileinclu_warning

    def download_interface(self, data):
        from HTMLtoPDF.html_to_pdf import HTMLtoPDF
        downloader = HTMLtoPDF(self.config_ini)
        for item_data in data:
            downloader.start(item_data)

    def draw_image_interface(self):
        from PIL import Image
        import time
        from paddleocr.tools.infer.utility import draw_ocr
        image_data = self.image_data
        if not image_data:
            print('图片数据为空！')
            return "图片数据为空，请点击钓鱼网站检测之后再来查看图片!\n"
        else:
            print('请耐心等待图片生成....\n')
            current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            for index, per_data in enumerate(image_data):
                input_path, data = per_data
                print('data:', data)
                output_path = self.config_ini['main_project']['project_path'] + self.config_ini['phish'][
                    'phish_out_img'] + \
                              r'/ocr_screenshot_{}_{}.png'.format(current_time, index)
                image = Image.open(input_path).convert('RGB')
                img_show = draw_ocr(image, [line[0] for line in data], [line[1][0] for line in data],
                                    [line[1][1] for line in data],
                                    font_path=self.config_ini['main_project']['project_path'] +
                                              self.config_ini['components']['tff'])
                ocr_img = Image.fromarray(img_show)
                ocr_img.save(output_path)
            print('生成图片完毕!')
            return '~~生成图片完毕~~\n'
