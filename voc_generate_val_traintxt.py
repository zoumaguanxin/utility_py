# -*- coding：utf-8 -*-

import os  
import random  

trainval_percent = 0.8    # 自己设定（训练集+验证集）所占（训练集+验证集+测试集）的比重  
train_percent = 0.9       # 自己设定（训练集）所占（训练集+验证集）的比重
xmlfilepath = 'Annotations/'     #注意自己地址是否正确
txtsavepath = 'ImageSets/Main'   #注意自己地址是否正确
total_xml = os.listdir(xmlfilepath)  

num = len(total_xml)  
list = range(num)  
tv = int(num*trainval_percent)  
tr = int(tv*train_percent)  
trainval = random.sample(list,tv)  
train = random.sample(trainval,tr)  

ftrainval = open(txtsavepath+'/trainval.txt', 'w')  
ftest = open(txtsavepath+'/test.txt', 'w')  
ftrain = open(txtsavepath+'/train.txt', 'w')  
fval = open(txtsavepath+'/val.txt', 'w')  

for i in list:  
    name = total_xml[i][:-4]+'\n'  
    if i in trainval:  
        ftrainval.write(name)  
        if i in train:  
            ftrain.write(name)  
        else:  
            fval.write(name)  
    else:  
        ftest.write(name)  

ftrainval.close()  
ftrain.close()  
fval.close()  
ftest .close()
print('Done')
