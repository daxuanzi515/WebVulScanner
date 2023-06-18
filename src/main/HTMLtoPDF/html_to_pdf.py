import os
import time
import pdfkit


class HTMLtoPDF:
    def __init__(self):
        super(HTMLtoPDF, self).__init__()
        # 填写你自己安装 wkhtmltopdf.exe的地址
        self.path = r"E:\formalFiles\wkhtmltopdf\bin\wkhtmltopdf.exe"
        self.options = {
            'enable-local-file-access': None,
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': 'UTF-8',
            'page-width': '250mm',
            'page-height': '320mm',
            'zoom': 1
        }
        # cover_html是 webscannerbook.html-封皮 的内容
        # new_html是生成的新的网页 用于转pdf
        # new_pdf 是转成的pdf
        self.new_html = r'D:\PyCharmTest\PyCharmPackets\Models\WebScannerProject\reference\pythonProject\src\main\HTMLtoPDF\html\out\webscanner_report_html_{}.html'
        self.new_pdf = r'D:\PyCharmTest\PyCharmPackets\Models\WebScannerProject\reference\pythonProject\src\pdf\webscanner_report_{}.pdf'
        self.cover_file = r'D:\PyCharmTest\PyCharmPackets\Models\WebScannerProject\reference\pythonProject\src\main\HTMLtoPDF\html\out\webscannerbook.html'
        # self.cover_html = ['<!DOCTYPE html>\n', '<html>\n', '<head>\n', '    <meta charset="UTF-8">\n', '    <title>Cover Page</title>\n', '    <link rel="stylesheet" href="cover.css">\n', '</head>\n', '<body>\n', '    <div class="cover">\n', '        <img src="images/spider.png" alt="Cover Image">\n', '        <h1>WEB SCANNER REPORT</h1>\n', '    </div>\n', '</body>\n', '</html>\n']
        self.cover_html = []

    # 组装封面和数据格式
    def connect_htmlformat(self, data):
        html_strings = []
        resource_data = data
        # web, warning, level 组装格式 :
        # < div style="page-break-before: always; page-break-after: always;"> {web0}</br>{warning0}</br>{level0}</br> </div>
        # < div style = "page-break-before: always; page-break-after: always;" > {web1}</br>{warning1}</br>{level1}</br> < / div >
        for item in resource_data:
            # 替换\n为</br>
            web, warning, level = item  # item 中的数据
            warning = warning.replace('\n', '</br>')
            # 加格式和拼接数据
            html_string = '<div style="page-break-before: always; page-break-after: always; position: relative;">'
            html_string += f'<div style="color: green; position: relative; top: 100px; left: 70px; font-size: 20px;">目标网址: {web}</div>'
            html_string += f'<div style="color: blue; position: relative; top: 150px; left: 70px; font-size:20px;">网址漏洞: {warning}</div>'
            html_string += f'<div style="color: red; position: relative; top: 200px; left: 70px; font-size: 20px;">漏洞等级: {level}</div>'
            html_string += '</div>'
            html_strings.append(html_string)

        with open(self.cover_file, 'r', encoding='utf-8') as file:
            self.cover_html = file.readlines()
        file.close()

        insert_index = None
        for i, line in enumerate(self.cover_html):
            if line.strip() == '</div>':
                insert_index = i + 1
                break
        # 插入处理好的字符串
        self.cover_html[insert_index:insert_index] = html_strings
        # print(self.cover_html)

    def write_pdf(self):
        current_time = time.localtime()
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", current_time)
        self.new_pdf = self.new_pdf.format(current_time)
        self.new_html = self.new_html.format(current_time)
        # 写html
        with open(self.new_html, 'w', encoding='utf-8') as file:
            file.writelines(self.cover_html)
        file.close()
        pdfkit.from_file(self.new_html, self.new_pdf,
                         configuration=pdfkit.configuration(wkhtmltopdf=self.path), options=self.options)
        # 删除生成的html/或者有人想保留？
        os.remove(self.new_html)

    def start(self, data):
        self.connect_htmlformat(data=data)
        self.write_pdf()
        print('~~~PDF生成成功~~~')
