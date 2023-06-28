import os

import qdarkstyle
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QPainter, QIcon, QTextDocument
from PyQt5.QtWidgets import QTableWidget, QToolTip, QTableWidgetItem, QMenu, QAction, \
    QStyledItemDelegate
from pyqt5_plugins.examplebutton import QtWidgets
from qdarkstyle import LightPalette

img1 = 'ui/img/web.png'
img2 = 'ui/img/star.png'


class TreeModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)

    def setTreeData(self, data):
        self.clear()
        root_item = self.invisibleRootItem()
        item1 = QStandardItem("网站")
        root_item.appendRow(item1)
        # 把两个元素添加到根目录下的一行
        for item in data:
            per_item = QStandardItem(item)
            per_item.setToolTip(item)  # 设置完整的网址为提示信息
            item1.appendRow(per_item)  # 子元素设置为根目录 再次添加
            per_item.setCheckable(True)
        item1.setCheckable(False)
        self.setHeaderData(0, Qt.Horizontal, '扫描数据')

    # 检测被选中的子项
    def getCheckedItems(self):
        checked_items = []
        root_item = self.invisibleRootItem()
        item1 = root_item.child(0)  # 获取网站节点
        for row in range(item1.rowCount()):
            child_item = item1.child(row)
            if child_item.checkState() == Qt.Checked:
                checked_items.append(child_item.text())
        return checked_items


class TableView(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setColumnCount(4)
        headers = ['网址', '漏洞描述', '评级', 'flag']
        self.setHorizontalHeaderLabels(headers)

        header = self.horizontalHeader()

        content_width = 430
        sign_width = 40

        self.setColumnWidth(0, content_width)
        self.setColumnWidth(1, content_width)
        self.setColumnWidth(2, sign_width)
        self.setColumnWidth(3, sign_width)

        # 创建自定义委托对象
        self.custom_delegate = self.CustomDelegate(self)

        # 应用委托对象到需要自定义行宽和换行的列上
        self.setItemDelegateForColumn(0, self.custom_delegate)
        self.setItemDelegateForColumn(1, self.custom_delegate)

        self.marked_rows = set()  # 保存已标记的行索引
        self.setToolTip("")  # 初始化提示文本为空

        self.set_theme(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))

    def set_theme(self, theme):
        self.setStyleSheet(theme)
        self.custom_delegate.current_theme = theme

    def viewportEvent(self, event):
        if event.type() == QEvent.ToolTip:
            # 获取鼠标所在的单元格坐标
            pos = event.pos()
            index = self.indexAt(pos)
            if index.isValid():
                item = self.item(index.row(), index.column())
                if item is not None:
                    QToolTip.showText(event.globalPos(), item.text())
                else:
                    QToolTip.hideText()
            else:
                QToolTip.hideText()
        return super().viewportEvent(event)

    def add_row(self, data):
        row = self.rowCount()
        self.insertRow(row)

        for col, col_data in enumerate(data):
            item = QTableWidgetItem(col_data)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置水平居中和垂直居中对齐
            self.setItem(row, col, item)

            if col == 2:
                rating = int(col_data)
                if rating > 6:
                    item.setForeground(QColor("#FF4500"))
                else:
                    item.setForeground(QColor("#00FF7F"))
        # 调整行高
        self.resizeRowToContents(row)

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        action_fill_red = QAction("Dinggo", self)
        action_fill_red.triggered.connect(self.fillSelectedRowsRed)
        menu.addAction(action_fill_red)
        menu.exec_(event.globalPos())

    def paintEvent(self, event):
        super().paintEvent(event)
        # 在指定行的列头位置绘制图标
        painter = QPainter(self.viewport())
        for row in range(self.rowCount()):
            if row in self.marked_rows:
                icon = QIcon(img1)
            else:
                icon = QIcon(img2)

            icon_rect = self.visualRect(self.model().index(row, 3))
            icon.paint(painter, icon_rect, Qt.AlignCenter, QIcon.Normal, QIcon.On)

    def fillSelectedRowsRed(self):
        selected_ranges = self.selectedRanges()
        for selected_range in selected_ranges:
            top_row = selected_range.topRow()
            bottom_row = selected_range.bottomRow()
            for row in range(top_row, bottom_row + 1):
                self.markRowWithIcon(row)

    def markRowWithIcon(self, row):
        if row in self.marked_rows:
            self.marked_rows.remove(row)
        else:
            self.marked_rows.add(row)
        self.viewport().update()

    # 定义换行类
    class CustomDelegate(QStyledItemDelegate):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.current_theme = None

        def paint(self, painter, option, index):
            if index.column() == 0 or index.column() == 1:  # 需要换行自定义
                text = index.data().replace('\n', '<br>')
                document = QTextDocument()

                if self.current_theme == (qdarkstyle.load_stylesheet(qt_api='pyqt5')):
                    document.setHtml('<html><body style="color: #E0E1E3;">{}</body></html>'.format(text))
                else:
                    document.setHtml('<html><body style="color: #000000;">{}</body></html>'.format(text))

                document.setTextWidth(option.rect.width())  # 设置文本宽度为单元格宽度
                document.setDefaultFont(option.font)
                painter.save()
                painter.translate(option.rect.topLeft())
                document.drawContents(painter)
                painter.restore()
            else:
                QStyledItemDelegate.paint(self, painter, option, index)

        def sizeHint(self, option, index):
            size = QStyledItemDelegate.sizeHint(self, option, index)
            if index.column() == 0 or index.column() == 1:  # 需要自定义的列
                text = index.data().replace('\n', '<br>')
                document = QTextDocument()
                document.setHtml("<html><body>{}</body></html>".format(text))
                document.setTextWidth(option.rect.width())  # 设置文本宽度为单元格宽度
                document.setDefaultFont(option.font)
                size.setHeight(int(document.size().height()))
            return size


class Tools:
    def __init__(self):
        self.scanner_model = None
        self.webfile_model = None

    def addFilesToScanner(self, data, component):
        self.scanner_model = TreeModel()
        component.setModel(self.scanner_model)
        self.loadData(data, self.scanner_model)
        self.adjustTreeViewHeader(component)  # 调整树形控件的列宽适应内容宽度

    def addFilesToWebfile(self, data, component):
        self.webfile_model = TreeModel()
        component.setModel(self.webfile_model)
        self.loadData(data, self.webfile_model)
        self.adjustTreeViewHeader(component)  # 调整树形控件的列宽适应内容宽度

    def handleHeaderClicked(self):
        path = r''
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(None, "选择文件夹", path)
        allfiles = self.get_files(folder_path)
        return allfiles

    def get_files(self, folder_path):
        # 在这里实现获取指定文件夹下的所有 PHP 文件的逻辑
        # 返回 PHP 文件的列表
        all_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith((".php", ".py", ".txt", '.log',".html",".ini",".png",".ui",".js",".db")):  # 可改
                    all_files.append(os.path.join(root, file))
        return all_files

    def adjustTreeViewHeader(self, component):
        component.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        component.header().setStretchLastSection(False)

    def loadData(self, data, model):
        model.setTreeData(data)
