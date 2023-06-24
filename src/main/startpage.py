import random
import qdarkstyle
from PyQt5 import uic
from PyQt5.QtCore import QRegularExpression, Qt, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QRegularExpressionValidator, QValidator, QCursor, QStandardItem, \
    QDesktopServices
from PyQt5.QtWidgets import QInputDialog, QMessageBox, qApp
from pyqt5_plugins.examplebutton import QtWidgets
from qdarkstyle import LightPalette

from interface import interface
from ui.py.tools import Tools, TableView
from config.config import Config

# 加载 .ui 文件
ui_path = "ui/index.ui"
Ui_MainWindow, _ = uic.loadUiType(ui_path)
ui_icon = 'ui/img/spider.png'
ui_pointer = 'ui/img/finger.png'


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(ui_icon))
        self.pixmap = QPixmap(ui_pointer)
        self.smaller_pixmap = self.pixmap.scaled(24, 24)  # 将图像调整为24*24的尺寸
        # 设置鼠标跟踪
        self.setMouseTracking(True)

        # 读取配置文件
        self.Config = Config()
        self.config_ini = self.Config.read_config()

        # 初始化数据
        self.scanner_data = []
        self.file_data = []
        self.interface = interface(self.config_ini)
        self.Tools = Tools()
        self.log_data = []
        self.light_theme = qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette())
        self.dark_theme = qdarkstyle.load_stylesheet(qt_api='pyqt5')
        self.wintheme = self.light_theme

        # 表
        self.Table = TableView(self.ui.result)
        self.Table.setGeometry(0, 0, self.ui.result.width(), self.ui.result.height())
        self.table_data = []

        # 槽函数 功能
        self.ui.start.clicked.connect(self.crawl_web)
        self.ui.open.clicked.connect(self.open_file)
        self.ui.xss.stateChanged.connect(self.xss_trace)
        self.ui.csrf.stateChanged.connect(self.csrf_trace)
        self.ui.force.stateChanged.connect(self.brute_trace)
        self.ui.webattack.stateChanged.connect(self.phish_trace)


        self.ui.findlog.clicked.connect(self.find_log)
        self.ui.clearlog.clicked.connect(self.clear_log)
        self.ui.theme.stateChanged.connect(self.change_theme)
        self.ui.report.clicked.connect(self.download_report)

        self.ui.scanner.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.scanner.customContextMenuRequested.connect(self.showContextMenu)

    def crawl_web(self):
        validator = QRegularExpressionValidator(QRegularExpression(r'[a-zA-z]+://[^\s]*'), self)
        url, ok = QInputDialog.getText(self, "爬取网址", "请输入网址:")

        if validator.validate(url, 0)[0] == QValidator.Acceptable:
            self.scanner_data = self.interface.spider_interface(url)
        else:
            QMessageBox.warning(self, "输入错误", "请输入有效的网址！", QMessageBox.Ok)
        self.Tools.addFilesToScanner(data=self.scanner_data, component=self.ui.scanner)

    def open_file(self):
        self.file_data = self.Tools.handleHeaderClicked()
        self.Tools.addFilesToWebfile(data=self.file_data, component=self.ui.webfile)

    def xss_trace(self):
        # 网址列表
        target_list = self.Tools.scanner_model.getCheckedItems()
        xss_logs = []
        xss_warnings = []
        xss_msg = []
        level = str(random.randint(4, 7))
        for item in target_list:
            xss_per_log, xss_warning = self.interface.xss_interface(item)
            self.ui.log.append(xss_per_log)
            xss_msg.append([item, xss_warning, level])
            xss_warnings.append(xss_warning)
            xss_logs.append(xss_per_log)
        self.table_data.append(xss_msg)
        print(self.table_data)

        for row_data in self.table_data:
            for item_data in row_data:
                self.Table.add_row(item_data)

    def csrf_trace(self):
        target_list = self.Tools.scanner_model.getCheckedItems()
        # csrf_logs = []
        # csrf_warnings = []
        csrf_msg = []
        level = '6'
        for item in target_list:
            csrf_per_log, csrf_per_warning = self.interface.csrf_interface(item)
            self.ui.log.append(csrf_per_log)
            csrf_msg.append([item, csrf_per_warning, level])

        self.table_data.append(csrf_msg)
        for row_data in self.table_data:
            for item_data in row_data:
                self.Table.add_row(item_data)


    def brute_trace(self):
        # target_list = self.Tools.scanner_model.getCheckedItems()
        target_list = self.Tools.scanner_model.getCheckedItems()
        # target_list = self.Tools.scanner_model.getCheckedItems()
        brute_msg = []
        level = '2'
        for item in target_list:
            brute_per_log, brute_per_warning = self.interface.brute_interface(item)
            print(brute_per_warning)
            print(brute_per_log)
            self.ui.log.append(brute_per_log)
            brute_msg.append([item, str(brute_per_warning), level])

        self.table_data.append(brute_msg)


    def phish_trace(self):
        target_list = self.Tools.scanner_model.getCheckedItems()
        level = str(random.randint(7, 10))
        phish_msg = []
        for item in target_list:
            phish_per_log, phish_per_warning = self.interface.phish_interface(item)
            self.ui.log.append(phish_per_log)
            phish_msg.append([item, phish_per_warning, level])

        self.table_data.append(phish_msg)
        for row_data in self.table_data:
            for item_data in row_data:
                self.Table.add_row(item_data)

    def clear_log(self):
        self.ui.log.clear()

    def find_log(self):

        folder_path = self.config_ini['main_project']['project_path'] + self.config_ini['log']['log_path']

        select_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选取文件", folder_path, "Text Files (*.txt)")
        if select_file_path:
        # 将文件路径转换为QUrl对象
            url = QUrl.fromLocalFile(select_file_path)
        # 使用默认的文本编辑器打开文件
            QDesktopServices.openUrl(url)

    def change_theme(self):
        if self.wintheme == self.light_theme:
            qApp.setStyleSheet(self.dark_theme)
            self.wintheme = self.dark_theme
        else:
            qApp.setStyleSheet(self.light_theme)
            self.wintheme = self.light_theme
        self.Table.set_theme(self.wintheme)

    def download_report(self):
        resource_data = self.table_data
        self.interface.download_interface(resource_data)

        folder_path = self.config_ini['main_project']['project_path'] + self.config_ini['pdf']['pdf_path']

        select_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选取文件", folder_path, "Text Files (*.pdf)")
        if select_file_path:
        # 将文件路径转换为QUrl对象
            url = QUrl.fromLocalFile(select_file_path)
        # 使用默认的文本编辑器打开文件
            QDesktopServices.openUrl(url)

    # override
    def enterEvent(self, event):
        # 鼠标进入部件时更换光标
        # 创建自定义光标对象
        cursor = QCursor(self.smaller_pixmap)
        self.setCursor(cursor)

    def leaveEvent(self, event):
        # 鼠标离开部件时，恢复默认光标样式
        self.unsetCursor()

    def showContextMenu(self, pos):
        menu = QtWidgets.QMenu(self.ui.scanner)
        # 添加菜单项
        menu.addAction("添加数据", self.addData)
        # 显示菜单
        menu.exec_(self.ui.scanner.viewport().mapToGlobal(pos))

    def addData(self):
        print('yes')
        validator = QRegularExpressionValidator(QRegularExpression(r'[a-zA-z]+://[^\s]*'), self)
        url, ok = QInputDialog.getText(self, "添加网址", "请输入网址:")
        if validator.validate(url, 0)[0] == QValidator.Acceptable:
            # 添加数据到模型
            item = QStandardItem(url)
            item.setCheckable(True)
            # 获取根节点 这里有问题... 要给全局？不对是scanner的实例化对象
            root_item = self.Tools.scanner_model.invisibleRootItem()
            item1 = root_item.child(0)
            # 将新项插入到第一个子项的第一个位置
            item1.insertRow(0, item)
        else:
            QMessageBox.warning(self, "输入错误", "请输入有效的网址！", QMessageBox.Ok)
