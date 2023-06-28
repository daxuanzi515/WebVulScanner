import requests
from bs4 import BeautifulSoup

class fileInclude(object):
    def __init__(self, url, config_ini):
        super(fileInclude, self).__init__()
        self.url = url
        self.config_ini = config_ini

        self.path = self.config_ini['main_project']['project_path'] + self.config_ini['fileinclu']['fileinclu_py']
        self.output = self.config_ini['main_project']['project_path'] + self.config_ini['fileinclu']['fileinclu_log']

    def fileInclusionDetect(self):
        # 构造包含漏洞的文件路径
        # payload = f"{url}?file={file_path}"

        my_response = requests.get(self.url)
        my_html_content = my_response.text
        # print(my_html_content)
        my_soup = BeautifulSoup(my_html_content, 'html.parser')
        logtext = ""
        warningtext = ""

        form_tags = my_soup.find_all('form')
        select_tags = my_soup.find_all('select')
        input_tags = my_soup.find_all('input')
        p_tags = my_soup.find_all('p')
        textarea = my_soup.find_all('textarea')
        for form_tag in form_tags:
            p_tags = form_tag.find_all('p')
            select_tags = form_tag.find_all('select')
            textarea_tags = form_tag.find_all('textarea')
        method = ''
        for form in form_tags:
            method = form.get('method')

        params = {}
        if select_tags:
            for selTag in select_tags:
                argName = selTag.get('name')
                params[argName] = "1.php"

        for tag in input_tags:
            argName = tag.get('name')
            if tag.get('value') != None:
                argVal = tag.get('value')
            else:
                argVal = "提交"
            params[argName] = argVal

        print(params)
        method = form.get('method')
        if method == 'get':
            my_response_1 = requests.get(self.url, params=params)
            print("已发送get请求")
            logtext = logtext + "[已发送GET请求]  " + my_response_1.url + "\n"
        elif method == 'post':
            my_response_1 = requests.post(self.url, data=params)
            print("已发送post请求")
            logtext = logtext + "[已发送POST请求]  " + my_response_1.url + "\n"

        # 检查响应中是否包含了预期的文件内容或系统错误信息
        # print(my_response_1.text)
        if "File content" in my_response_1.text or "No such file or directory" in my_response_1.text or "include(): Failed opening" in my_response_1.text:
            print("文件包含漏洞存在")
            warningtext = "未对一句话木马文件包含漏洞进行限制，存在文件包含漏洞"
        elif "System error" in my_response_1.text:
            print("可能存在文件包含漏洞，系统错误信息暴露")
            warningtext = "可能存在文件包含漏洞，系统错误信息暴露"
        else:
            print("文件包含漏洞不存在")
            warningtext = "文件包含漏洞不存在"

        return logtext, warningtext