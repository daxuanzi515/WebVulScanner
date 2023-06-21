import time
from selenium.webdriver.support import expected_conditions as ec
from selenium import webdriver

# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


# 截图 存 fish_detect/phish/imgs/target/screenshot_{}-{}.png
# ocr 结果 存 fish_detect/phish/imgs/out/ocr_image_{}_{}.png
# 生成 log 存  fish_detect/phish/log/phishing_log_{}.txt
class PhishDetector:
    def __init__(self, config_ini):
        super(PhishDetector, self).__init__()
        self.config_ini = config_ini
        self.target_img = self.config_ini['main_project']['project_path'] + self.config_ini['phish']['phish_target_img']
        self.out_img = self.config_ini['main_project']['project_path'] + self.config_ini['phish']['phish_out_img']
        self.phish_log = self.config_ini['main_project']['project_path'] + self.config_ini['phish']['phish_log']
        self.log_content = []
        self.item_work = []
        self.txts_content = []

        self.log_content.append('Start Phishing Detect!!!\n')

        self.keywords = ['登录', '', '', '', '']
        self.keywords_list = {
            # 登录
            '登录':['logging', 'login', 'log in','log','id','register','logging in','sign in','sign up','sign'],
            # 密码
            '密码':['password','keyword','secretword'],
            #邮箱
            '邮箱':['email','address','send','sending','contact'],
            # 电话号码
            '电话号码':['number','phone','call','mobile','virgin','phone number','calling'],
            # token
            'token':['token'],
            # 助词
            '助词': ['success','successful','successfully','opportunity','congratulations','welcome'],
            # 动词
            '动词':['submit','enter','continue','next','connect','disconnect'],
            # 账户
            '账户':['account', 'freeze', 'activate', 'profile','details'],
            # 钱包
            '金钱':['money','bussiness','financial',''],
            # 特殊符号
            '符号':['$','￥','@']
        }
        # chrome_driver 添加到环境变量！
        # self.chrome_driver = r'E:\formalFiles\Chrome_Driver\chromedriver_win32\chromedriver.exe'

    def get_screen_shot_invisible(self, url, img_path):
        # 隐式截图
        # chrome_options = Options()
        # chrome_options.add_argument("--headless")  # 使用无头模式
        # chrome_driver = webdriver.Chrome(options=chrome_options)
        chrome_driver = webdriver.Chrome()
        chrome_driver.get(url)
        chrome_driver.maximize_window()

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
        self.txts_content.append(txts)
        scores = [line[1][1] for line in result]
        im_show = draw_ocr(image, boxes, txts, scores, font_path=r'C:\Windows\Fonts\simsun.ttc')
        im_show = Image.fromarray(im_show)
        im_show.save(output_path)

    # per url
    def from_screen_To_ocr_result(self, url):
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        log_time = time.strftime("%H:%M:%S", time.localtime())

        item_name = r'/screenshot_{}_.png'.format(current_time)
        out_path = self.out_img + item_name
        real_path = self.target_img + item_name
        self.get_screen_shot_invisible(url, real_path)
        self.log_content.append('[]: From {} gets screenshot successfully!\n'.format(log_time, url))
        print('The image from: {} screenshot gets sucessfully~~'.format(url))

        self.screenshot_ocr_operator(real_path, out_path)
        self.log_content.append('[]: From {} gets screenshot successfully!\n'.format(log_time, url))
        print('The image from: {} ocr gets sucessfully~~'.format(url))

        return 'loading', 'loading'



    def recognizer_text_content(self):
        for item in self.txts_content:
            for word in item:
                pass





# if __name__ == '__main__':
#     config_obj = Config()
#     config_ini = config_obj.read_config()
#     phish_detector = PhishDetector(config_ini)
#     url_list = [
#         # 'http://myvirgin-mobile-login.com/',# 手机购买表单 需要事先人机验证
#         # 'http://myvirgin-mobile-login.com/profile.php', # 手机购买个人信息 需要事先人机验证
#         # 'https://freefireevent2023.github.io/spin/', # 登录ID表单
#         'https://number-six-4684b.web.app/login.html',# 邮件登录
#         # 'https://systemcesure.buzz/portalserver/bancanetempresarial/index/public/', # 伪造公司介绍面
#         # 'https://login.busiinesshellp.click/',# facebook 登录界面
#         # 'http://192.168.43.135/',# kali的twitter 登录
#         # 'https://psyopclaim.space/' # ape币 猿币交易
#     ]
#     phish_detector.from_screen_To_ocr_result(url)
#
