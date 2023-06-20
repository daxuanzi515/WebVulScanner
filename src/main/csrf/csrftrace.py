import os
import re
import subprocess
import time

class Csrf(object):
    def __init__(self, url):
        super(Csrf, self).__init__()
        self.url = url
        self.bolt_path="./bolt/bolt.py"

    def get_absolute_path(self, relative_path):
        absolute_path = os.path.abspath(relative_path)
        return absolute_path

    def execute_shell_command(self):
        command = ["python",
                   r"D:\AAtestplaceforcode\WebVulScanner\src\main\csrf\bolt\bolt.py",
                   "-u", self.url,
                   "-l", "1"]
        current_time = time.localtime()
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", current_time)
        output_file = "D:\AAtestplaceforcode\WebVulScanner\src\log\csrf\csrf_log_{}.txt".format(current_time)

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
        # if find==[]:
        #     print("none")
        if find:
            find.sort()
            for flag in range(0, len(find)-1):
                for i in range(find[flag], find[flag+1]):
                    warning.append(relog[i])
                    # print(relog[i])
                # warring.append(delimiter)
            # for i in range(find[-1], len(relog)):
            #     warring.append(relog[i])
        warnings = '\n'.join(warning)
        return warnings


# if __name__ == '__main__':
#     url = 'http://8.130.8.193/pikachu/vul/burteforce/bf_form.php'
#     crfs = Csrf(url)
#     log, warring = crfs.execute_shell_command()
#     print(log)
#     print(warring)
#     check = [" Weak token(s) found",
#              " Insecure form(s) found",
#              " Potential Replay Attack condition found",
#              " No CSRF protection to test",
#              " Token matches the pattern of following hash type(s):",
#              " Common substring found",
#              " 100 simultaneous requests are being made, please wait."]
#     find =[]
#     for i in check:
#         if i in relog:
#             find.append(relog.index(i))
#     if find==[]:
#         print("none")
#     else:
#         find.sort()
#         for flag in range(0, len(find)-1):
#             for i in range(find[flag], find[flag+1]):
#                 print(relog[i])
#             print("")
#         for i in range(find[-1], len(relog)):
#             print(relog[i])
    
    
    
    
    
    
    
    
    
    
    
    

