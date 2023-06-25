import time
from selenium.webdriver.support import expected_conditions as ec
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

# 截图 存 src/main/phish/target/screenshot_{}-{}.png
# ocr 结果 存 src/main/phish//out/ocr_image_{}_{}.png
# 生成 log 存  src/log/phishing_log_{}.txt
class PhishDetector:
    def __init__(self, config_ini):
        super(PhishDetector, self).__init__()
        self.config_ini = config_ini
        self.target_img = self.config_ini['main_project']['project_path'] + self.config_ini['phish']['phish_target_img']
        self.out_img = self.config_ini['main_project']['project_path'] + self.config_ini['phish']['phish_out_img']
        self.phish_log = self.config_ini['main_project']['project_path'] + self.config_ini['phish']['phish_log']
        self.log_content = []
        self.codes = ''
        self.item_work = []
        self.ocr_result = {}
        self.warnings = []
        # chrome_driver 添加到环境变量！
        # self.chrome_driver = r'E:\formalFiles\Chrome_Driver\chromedriver_win32\chromedriver.exe'

    def check_and_create_directory(self, path):
        import os
        if not os.path.exists(path):
            os.makedirs(path)
            # print("文件夹已创建：", path)


    def get_screen_shot_invisible(self, url, img_path):
        # 隐式截图
        # chrome_options = Options()
        # chrome_options.add_argument("--headless")  # 使用无头模式
        # chrome_driver = webdriver.Chrome(options=chrome_options)
        chrome_driver = webdriver.Chrome()
        chrome_driver.get(url)
        chrome_driver.maximize_window()
        self.codes = chrome_driver.page_source
        wait = WebDriverWait(chrome_driver, 10)
        wait.until(ec.visibility_of_element_located((By.TAG_NAME, 'body')))

        chrome_driver.get_screenshot_as_file(img_path)
        chrome_driver.quit()


    def screenshot_ocr_operator(self, input_path, output_path):
        from paddleocr import PaddleOCR
        from paddleocr.tools.infer.utility import draw_ocr
        # Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
        # 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
        ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)  # need to run only once to download and load model into memory
        result = ocr.ocr(input_path, cls=True)

        # 显示结果
        # 如果本地没有simfang.ttf，可以在doc/fonts目录下下载
        from PIL import Image
        result = result[0]
        image = Image.open(input_path).convert('RGB')
        boxes = [line[0] for line in result]
        txts = [line[1][0] for line in result]
        scores = [line[1][1] for line in result]
        im_show = draw_ocr(image, boxes, txts, scores, font_path=r'C:\Windows\Fonts\simsun.ttc')
        im_show = Image.fromarray(im_show)
        im_show.save(output_path)
        return txts


    def from_screen_To_ocr_result(self, url):
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        log_time = time.strftime("%H:%M:%S", time.localtime())
        self.log_content.clear()
        self.log_content.append('Start Phishing Detect!!!\n')
        item_name = r'/screenshot_{}_.png'.format(current_time)
        out_path = self.out_img + item_name
        real_path = self.target_img + item_name
        self.get_screen_shot_invisible(url, real_path)
        self.log_content.append('[{}]: From {} gets screenshot successfully!\n'.format(log_time, url))
        # print('The image from: {} screenshot gets sucessfully~~'.format(url))

        self.ocr_result[url] = self.screenshot_ocr_operator(real_path, out_path)
        self.log_content.append('[{}]: From {} gets ocr_screenshot successfully!\n'.format(log_time, url))
        # print('The image from: {} ocr gets sucessfully~~'.format(url))


    def level_judge_operator(self, url):
        data = self.ocr_result
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        log_time = time.strftime("%H:%M:%S", time.localtime())

        level_judge_obj = LevelJudge()
        # code
        identify_url_code_info = level_judge_obj.identify_url_source(self.codes)
        self.warnings.clear()
        for item in identify_url_code_info:
            self.warnings.append(item)

        temp_content = ['[{}]: {}'.format(log_time, item) for item in identify_url_code_info]
        self.log_content += temp_content
        #
        # print('[{}]:{}'.format(log_time, identify_url_code_info))
        keyword_prop, keywords = level_judge_obj.keyword_container(text_item=data[url])

        # print('key_prop:{}, keywords:{}'.format(keyword_prop,keywords))

        if keyword_prop != 0.0:
            self.log_content.append('[{}]: Detect The [{}%] Keyword from: {} in {}\n'.format(log_time, keyword_prop, keywords, url))
            self.warnings.append('Detect The [{}%] Keyword from: {} in {}\n'.format(keyword_prop, keywords, url))
            # print('[{}]: Detect The [{}%] Keyword from: {} in {}\n'.format(log_time, keyword_prop, keywords, url))

        log_file = self.phish_log.format(current_time)

        log_string = ''.join(self.log_content)
        warning_string = ''.join(self.warnings)

        with open(log_file,'w',encoding='utf-8') as file:
            file.write(log_string)
        file.close()
        # print('write end.\n')
        return log_string, warning_string

class LevelJudge:
    def __init__(self):
        super(LevelJudge, self).__init__()
        self.keywords = ['登录', '密码', '邮箱', '电话号码', '助词','动词','账户','金钱','符号','认证','安装','企业']
        self.keywords_list = {
            # 登录
            '登录':['logging', 'login', 'log in','log','id','register','logging in','sign in','sign up','sign'],
            # 密码
            '密码':['password','keyword','secretword','pass','word','key','secret'],
            #邮箱
            '邮箱':['email','address','send','sending','contact'],
            # 电话号码
            '电话号码':['number','phone','call','mobile','phone number','calling'],
            # 助词
            '助词': ['success','successful','successfully','opportunity','congratulations','welcome','from'],
            # 动词
            '动词':['submit','enter','continue','next','connect','disconnect'],
            # 账户
            '账户':['account', 'freeze', 'activate', 'profile','details','virgin'],
            # 金钱
            '金钱':['money','bussiness','financial','finance'],
            # 特殊符号
            '符号':['$','￥','@','>>','*'],
            # 认证
            '认证':['identify','vertification','details','name','birth','country','postcode','indicates'],
            # 安装
            '安装':['launch','launching'],
            # 企业
            '企业':['facebook','twitter']
        }

    def convert_upper_to_lower(self, text_item):
        new_data = [item.lower() for item in text_item]
        return new_data

    def keyword_container(self, text_item):
        init_texts = self.convert_upper_to_lower(text_item=text_item)
        shot_count = 0
        shot_class = set()
        total_count = 0
        for text in init_texts:
            # print(text)
            for item in self.keywords:
                value_list = self.keywords_list[item]
                # print(value_list)
                for value in value_list:
                    if value in text:
                        shot_count += 1
                        shot_class.add(item)
            total_count += len(text.split())
        # 保留三位小数
        shot_pro = round(shot_count / total_count * 100, 3)
        # print('命中率:{},总词数:{}'.format(shot_pro,total_count))
        # print('命中类别:{}'.format(list(shot_class)))

        return shot_pro, list(shot_class)

    # 注意这里获取不到源代码只能用浏览器模拟
    def identify_url_source(self, codes):
        # source_code = self.url_response(url=url)
        source_code = codes
        form_warning = self.form_container(source_code=source_code)
        href_warning = self.herf_container(source_code=source_code)
        return form_warning + href_warning

    def form_container(self, source_code):
        import re
        pattern = r'<form.*?action="(.*?)".*?>'
        matches = re.findall(pattern, source_code)
        info = []
        if matches:
            # print("警告：网页中存在表单提交的 action！")
            for match in matches:
                # print(f"表单 action: {match}\n")
                info.append(f"Detect the FORM action in url: {match}\n")
        else:
            # print("网页中没有表单提交的 action。")
            info.append("Detect No form in url.\n")

        return info

    def herf_container(self, source_code):
        import re
        pattern = r'href=[\'"](.*?)[\'"]'
        matches = re.findall(pattern, source_code)
        info = []
        if matches:
            for match in matches:
                if match != '/' and match != '#' and match != '\\\\' and match != '':
                    if match.startswith(('http://', 'https://')) and not match.endswith(('.ico', '.css', '.js','.png','.jpeg','jpg')):
                        info.append(f"Detect the HERF in url: {match}\n")
        else:
            info.append("Detect No href in url.\n")
        return info
