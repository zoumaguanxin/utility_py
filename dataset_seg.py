import os
import re
import cv2
import random

# 先将标注txt文件全部拷入source_img_dataset文件夹


path = "/media/shawn/ubuntu_data/datasets/deep_learning_datasets/tianchi_tile/tile_round1_train_20201231/"

if __name__ == '__main__':
    # 定义路径
    source_dataset_path = os.path.join(path, 'JPEGImages/')
	
    train_path = os.path.join(path,'train.txt')
    test_path = os.path.join(path,'val.txt')

    # 读取source_dataset_path路径下所有文件（包括子文件夹下文件）
    filenames = os.listdir(source_dataset_path)
    # print(filenames)
    # ['1.jpg', '1.txt', '10.jpg',...]

    # 提取.jpg
    filenames_jpg = []
    for i in filenames:
        if i.endswith('.txt'):
            filenames_jpg.append(os.path.splitext(i)[0] + '.jpg')
    # print(filenames_jpg)
    # ['1.jpg', '10.jpg', '100.jpg',...]

    # 排序
    filenames_jpg.sort(key=len)
    # print(filenames_jpg)
    # ['1.jpg', '2.jpg', '3.jpg',...]

    # 拆分写入
    train_scale = 0.75  # 训练集占比
    train_file = open(train_path, 'w', encoding='utf-8')
    test_file = open(test_path, 'w', encoding='utf-8')
    for file_name in filenames_jpg:
        proba = random.random()  # 设置随机概率
        write_content = os.path.join(source_dataset_path, file_name+'\n')  # 创建写入内容
        if proba < train_scale:  # 判断该写入哪个文件
            train_file.write(write_content)
        else:
            test_file.write(write_content)
    train_file.close()
    test_file.close()
