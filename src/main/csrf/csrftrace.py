import os
import re
import subprocess
import time

class Csrf(object):
    def __init__(self, url, config_ini):
        super(Csrf, self).__init__()
        self.url = url
        self.config_ini = config_ini

        self.path = self.config_ini['main_project']['project_path'] + self.config_ini['csrf']['csrf_py']
        self.output = self.config_ini['main_project']['project_path'] + self.config_ini['csrf']['csrf_log']

    def execute_shell_command(self):
        command = ["python",
                   self.path,
                   "-u", self.url,
                   "-l", "1"]
        current_time = time.localtime()
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", current_time)
        output_file = self.output.format(current_time)

        if not os.path.exists(output_file):
            open(output_file, 'w', encoding='utf-8').close()

        try:
            with open(output_file, "w", encoding='utf-8') as file:
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True,
                                                 errors='ignore')
                print("yes")
                clean_data = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', output)
                split_lines = clean_data.split("\n")
                
                filtered_lines = [line for line in split_lines if line.strip()]  
                result = "\n".join(filtered_lines)
                warning = self.fliter(filtered_lines)
                file.write(result)

                self.fliter(filtered_lines)
                print("Success!")
                return result, warning

        except subprocess.CalledProcessError as e:
            print(e.output)

    def fliter(self, relog):
        check = [" Weak token(s) found",
                 " Insecure form(s) found",
                 " Potential Replay Attack condition found",
                 " No CSRF protection to test",
                 " Token matches the pattern of following hash type(s):",
                 " Common substring found",
                 " 100 simultaneous requests are being made, please wait."]
        find = []
        warning = []
        for i in check:
            if i in relog:
                find.append(relog.index(i))
        if find:
            find.sort()
            for flag in range(0, len(find)-1):
                for i in range(find[flag], find[flag+1]):
                    warning.append(relog[i])
        warnings = '\n'.join(warning)
        return warnings

    
    
    
    
    
    
    
    
    
    

