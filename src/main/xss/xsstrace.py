import os
import subprocess
import time

class XssTrace(object):
    def __init__(self, url, config_ini):
        super(XssTrace, self).__init__()
        self.url = url
<<<<<<< HEAD
        self.config_ini = config_ini

        self.path = self.config_ini['main_project']['project_path'] + self.config_ini['xss']['xss_py']
        self.output = self.config_ini['main_project']['project_path'] + self.config_ini['xss']['xss_log']


=======
        self.config_ini = config_ini

        self.path = self.config_ini['main_project']['project_path'] + self.config_ini['xss']['xss_py']
        self.output = self.config_ini['main_project']['project_path'] + self.config_ini['xss']['xss_log']


>>>>>>> upstream/cxx
    def execute_shell_command(self):
        command = ["python",
                   self.path,
                   "--single", self.url]
        # "./XSSCon/xsscon.py" 当前 但是要调用的时候 变成绝对路径
        current_time = time.localtime()
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", current_time)

        output_file = self.output.format(current_time)
        if not os.path.exists(output_file):
            open(output_file, 'w', encoding='utf-8').close()

        try:
            with open(output_file, "w", encoding='utf-8') as file:
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True,
                                                 encoding='utf-8')
                clean_data = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', output)
                split_text = clean_data.split("***************")

                if len(split_text) > 1:
                    extracted_content = split_text[1]
                else:
                    extracted_content = ""

                split_lines = extracted_content.split("\n")
                filtered_lines = [line for line in split_lines if line.strip()]  # 去掉空行
                result = "\n".join(filtered_lines)
                file.write(result)

                cutting_msg = self.data_extract(filtered_lines)
                warnings = '\n'.join(cutting_msg)
                return result, warnings

        except subprocess.CalledProcessError as e:
            print(e.output)

    def data_extract(self, msg):
        extract_operator = Filter(data=msg)
        extract_operator.start()
        result = extract_operator.result
        return result


import re
class Filter(object):
    def __init__(self, data):
        self.data = data
        self.filter_data = None
        self.dom_data = None
        self.result = None

    def dom_extract(self):
        endstr = '------------------------------------------------------------------------------------------------------------------------'
        ans = 0
        filter_data = []
        is_adding = False
        for item in self.data:
            if is_adding:
                filter_data.append(item)
                if item.strip() == endstr:
                    ans += 1
                    if ans == 1:
                        break
            elif item.strip() == endstr:
                is_adding = True
                filter_data.append(item)
        return filter_data

    def data_extract(self):
        keywords = ['Detected', '[WARNING]', '[CRITICAL]']
        filtered_list = []
        for item in self.data:
            for keyword in keywords:
                if keyword in item and item not in filtered_list:
                    filtered_list.append(item)
                    break
        return filtered_list

    def remove_timestamp(self, item):
        pattern = r'\[\d{2}:\d{2}:\d{2}\]'
        return re.sub(pattern, '', item)

    def remove_keywords(self, item):
        keywords = ['[CRITICAL]', '[WARNING]']
        for keyword in keywords:
            item = item.replace(keyword, '').strip()
        return item

    def start(self):
        self.dom_data = self.dom_extract()
        self.filter_data = self.data_extract()
        self.filter_data = [self.remove_timestamp(item) for item in self.filter_data]
        self.filter_data = [self.remove_keywords(item) for item in self.filter_data]
        self.filter_data = list(set(self.filter_data))  # 去重
        self.result = self.filter_data + self.dom_data
<<<<<<< HEAD
=======
>>>>>>> upstream/cxx

