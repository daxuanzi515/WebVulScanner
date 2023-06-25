from bs4 import BeautifulSoup
import urllib.request
import http.cookiejar
import time
import os
from src.main.bruteforce.loadkey.loadkey import Loadkey


class BruteForce:
    def __init__(self, url, config_ini) -> None:
        self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.url = url
        self.headers = {'User-Agent': self.user_agent}
        self.log = ""
        self.config_ini = config_ini
        self.output = self.config_ini['main_project']['project_path'] + self.config_ini['brute']['brute_log']
        # self.output='D:/AAtestplaceforcode/WebVulScanner/src/log/brute/brute_log_{}.txt'

    def scan(self):
        request = urllib.request.Request(self.url, None, self.headers)  # The assembled request
        # response = urllib.request.urlopen(request)
        cookiejar = http.cookiejar.CookieJar()

        handler = urllib.request.HTTPCookieProcessor(cookiejar)
        opener = urllib.request.build_opener(handler)
        response = opener.open(request)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        cookieStr = ''
        for item in cookiejar:
            cookieStr = cookieStr + item.name + "=" + item.value + ";"
        self.headers['Cookie'] = cookieStr[:-1]

        pageurls = soup.find('form')
        m = pageurls.get('method')
        account = []
        passw = []
        others = {}
        if m is None:
            m = "get"

        self.log = self.log + "find method: " + m.upper() + '\n'

        inputs = soup.find_all('input')
        for i in inputs:
            self.log = self.log + "find input label: " + str(i) + '\n'
            if i.get('value'):
                others[i.get('name')] = i.get('value')
            elif i.get('type') == 'password':
                passw.append(i.get('name'))
            else:
                account.append(i.get('name'))
        return m, account, passw, others

    def brute(self, m, account, passw, others):

        loadpass = Loadkey(self.config_ini['main_project']['project_path'] + self.config_ini['brute']['brute_pass'])
        loadacc = Loadkey(self.config_ini['main_project']['project_path'] + self.config_ini['brute']['brute_acc'])

        results = []
        self.log = self.log + "use headers: " + str(self.headers) + '\n'
        dict = {}
        print("yes")
        valpassws = loadpass.load()
        valacc = loadacc.load()
        print("load")
        print(valacc)
        print(valpassws)
        for valp in valpassws:
            for vala in valacc:
                result = []
                for acc in account:
                    dict[acc] = vala
                    result.append(vala)
                for p in passw:
                    dict[p] = valp
                    result.append(valp)
                dict.update(others)
                # print(dict)
                self.log = self.log + "try: " + str(dict) + '\n'
                data = urllib.parse.urlencode(dict).encode('utf-8')
                request = urllib.request.Request(self.url, data, self.headers, method=m.upper())
                response = urllib.request.urlopen(request)
                html = response.read()

                result.append(len(html))
                # result =[vala, valp, len(html)]
                results.append(result)

                soup = BeautifulSoup(html, 'html.parser')
                inputs = soup.find_all('input')
                for i in inputs:
                    if i.get('value'):
                        others[i.get('name')] = i.get('value')
                # print(len(html))

        current_time = time.localtime()
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", current_time)
        output_file = self.output.format(current_time)

        if not os.path.exists(output_file):
            open(output_file, 'w', encoding='utf-8').close()
        with open(output_file, "w", encoding='utf-8') as file:
            file.write(self.log)

        result = self.check(results)
        return result, self.log

    def check(self, results):
        lens = [results[i][-1] for i in range(len(results))]
        for i in range(len(lens)):
            if lens.count(lens[i]) == 1:
                return results[i][:-1]

