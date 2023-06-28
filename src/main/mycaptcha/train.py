import numpy as np
import torch
from torch import nn
import matplotlib.pyplot as plt
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import os

captcha_list = list('0123456789abcdefghijklmnopqrstuvwxyz_')
captcha_length = 6

# 验证码文本转为向量
def text2vec(text):
    vector = torch.zeros((captcha_length, len(captcha_list)))
    text_len = len(text)
    if text_len > captcha_length:
        raise ValueError("验证码超过6位啦！")
    for i in range(text_len):
        vector[i,captcha_list.index(text[i])] = 1
    return vector

# 验证码向量转为文本
def vec2text(vec):
    label = torch.nn.functional.softmax(vec, dim =1)
    vec = torch.argmax(label, dim=1)
    for v in vec:
        text_list = [captcha_list[v] for v in vec]
    return ''.join(text_list)

# 加载所有图片，并将验证码向量化
def make_dataset(data_path):
    img_names = os.listdir(data_path)
    samples = []
    for img_name in img_names:
        img_path = data_path+img_name
        target_str = img_name.split('_')[0].lower()
        samples.append((img_path, target_str))
    return samples

class CaptchaData(Dataset):
    def __init__(self, data_path, transform=None):
        super(Dataset, self).__init__()
        self.transform = transform
        self.samples = make_dataset(data_path)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        img_path, target = self.samples[index]
        target = text2vec(target)
        target = target.view(1, -1)[0]
        img = Image.open(img_path)
        img = img.resize((140,44))
        img = img.convert('RGB') # img转成向量
        if self.transform is not None:
            img = self.transform(img)
        return img, target

class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        # 第一层神经网络
        # nn.Sequential: 将里面的模块依次加入到神经网络中
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1), # 3通道变成16通道，图片：44*140
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2)  # 图片：22*70
        )
        # 第2层神经网络
        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 64, kernel_size=3), # 16通道变成64通道，图片：20*68
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2)  # 图片：10*34
        )
        # 第3层神经网络
        self.layer3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3), # 16通道变成64通道，图片：8*32
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2)  # 图片：4*16
        )
        # 第4层神经网络
        self.fc1 = nn.Sequential(
            nn.Linear(4*16*128, 1024),
            nn.Dropout(0.2),  # drop 20% of the neuron
            nn.ReLU()
        )
        # 第5层神经网络
        self.fc2 = nn.Linear(1024, 6*37) # 6:验证码的长度， 37: 字母列表的长度

    #前向传播
    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        x = self.fc2(x)
        return x

net = Net()
print(net)

def calculat_acc(output, target):
    output, target = output.view(-1, len(captcha_list)), target.view(-1, len(captcha_list)) # 每37个就是一个字符
    output = nn.functional.softmax(output, dim=1)
    output = torch.argmax(output, dim=1)
    target = torch.argmax(target, dim=1)
    output, target = output.view(-1, captcha_length), target.view(-1, captcha_length) #每6个字符是一个验证码
    c = 0
    for i, j in zip(target, output):
        if torch.equal(i, j):
            c += 1
    acc = c / output.size()[0] * 100
    return acc

def train(epoch_nums):
    # 数据准备
    transform = transforms.Compose([transforms.ToTensor()]) # 不做数据增强和标准化了
    train_dataset = CaptchaData('../captcha/1/train/', transform=transform)
    train_data_loader = DataLoader(train_dataset, batch_size=32, num_workers=0, shuffle=True, drop_last=True)

    test_data = CaptchaData('../captcha/1/test/', transform=transform)
    test_data_loader = DataLoader(test_data, batch_size=128, num_workers=0, shuffle=True, drop_last=True)
    # 更换设备
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print('当前设备是:',device)
    net.to(device)

    criterion = nn.MultiLabelSoftMarginLoss() # 损失函数
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001) # 优化器

    # 加载模型
    model_path = '../captcha/1/checkpoints/model.pth'
    if os.path.exists(model_path):
        print('开始加载模型')
        checkpoint = torch.load(model_path)
        net.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    # 开始训练
    i = 1
    for epoch in range(epoch_nums):
        running_loss = 0.0
        net.train() # 神经网络开启训练模式
        for data in train_data_loader:
            inputs, labels = data
            inputs, labels = inputs.to(device), labels.to(device) #数据发送到指定设备
            #每次迭代都要把梯度置零
            optimizer.zero_grad()
            # 关键步骤
            # 前向传播
            outputs = net(inputs)
            # 计算误差
            loss = criterion(outputs, labels)
            # 后向传播
            loss.backward()
            # 优化参数
            optimizer.step()

            running_loss += loss.item()
            if i % 2000 == 0:
                acc = calculat_acc(outputs, labels)
                print('第%s次训练正确率: %.3f %%, loss: %.3f' % (i,acc,running_loss/2000))
                running_loss = 0
                # 保存模型
                torch.save({
                            'model_state_dict':net.state_dict(),
                            'optimizer_state_dict':optimizer.state_dict(),
                            },model_path)
            i += 1
        # 结束一个epoch,计算测试集的正确率
        net.eval() #测试模式
        with torch.no_grad():
            for inputs, labels in test_data_loader:
                outputs = net(inputs)
                acc = calculat_acc(outputs, labels)
                print('测试集正确率: %.3f %%' % (acc))
                break # 只测试一个batch

        # 每5个epoch 更新学习率
        if epoch % 5 == 4:
            for p in optimizer.param_groups:
                p['lr'] *= 0.9

def test():
    transform = transforms.Compose([transforms.ToTensor()]) # 不做数据增强和标准化了
    test_data = CaptchaData('../captcha/1/test/', transform=transform)
    test_data_loader = DataLoader(test_data, batch_size=128, num_workers=0, shuffle=True, drop_last=True)
    # 加载模型
    model_path = '../captcha/1/checkpoints/model.pth'
    if os.path.exists(model_path):
        print('开始加载模型')
        checkpoint = torch.load(model_path)
        net.load_state_dict(checkpoint['model_state_dict'])
    net.eval() #测试模式
    acc,i = 0, 0
    with torch.no_grad():
        for inputs, labels in test_data_loader:
            outputs = net(inputs)
            acc += calculat_acc(outputs, labels)
            i += 1
    print('测试集正确率: %.3f %%' % (acc/i))

def predict(inputs):
    net.eval() #测试模式
    with torch.no_grad():
        outputs = net(inputs)
        outputs = outputs.view(-1, len(captcha_list)) # 每37个就是一个字符
    return vec2text(outputs)

def test_one(src):
    transform = transforms.Compose([transforms.ToTensor()])  # 不做数据增强和标准化了
    test_data = CaptchaData(src, transform=transform)
    # 加载模型
    model_path = './model.pth'
    if os.path.exists(model_path):
        print('开始加载模型')
        checkpoint = torch.load(model_path)
        net.load_state_dict(checkpoint['model_state_dict'])
    output = predict(src)
    return output