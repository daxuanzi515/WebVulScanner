import os.path


class Loadkey:
    def __init__(self, path):
        self.path = path

    def load(self):
        if not os.path.exists(self.path):
            open(self.path, 'r', encoding='utf-8').close()

        with open(self.path, 'r', encoding='utf-8') as file:
            txt = []
            line = file.readline()
            while line:
                txt_data = str(line.strip('\n'))
                # txt_data) # 可将字符串变为元组
                txt.append(txt_data)  # 列表增加
                line = file.readline()  # 读取下一行
            file.close()
        return txt

# if __name__ == '__main__':
#     path ='D:/AAtestplaceforcode/WebVulScanner/src/main/bruteforce/passw.txt'
#     load = Loadkey(path)
#     passw = load.load()
#     print(passw)
