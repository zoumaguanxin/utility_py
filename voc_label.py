import os
from os.path import join
from tqdm import tqdm
from glob import glob
import xml.etree.ElementTree as ET

classes = ['1', '2','3','4','5','6']

def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

root = '/media/shawn/ubuntu_data/datasets/deep_learning_datasets/tianchi_tile/tile_round1_train_20201231/'
os.makedirs(root + 'labels', exist_ok=True)
filelists = glob(root + 'xmls/*.xml')
for item in tqdm(filelists):
    tree = ET.parse(item)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    for obj in root.iter('object'):
        if obj.find('name') is None:
            break
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (min(max(float(xmlbox.find('xmin').text), 0), w), min(max(float(xmlbox.find('xmax').text), 0), w),\
             min(max(float(xmlbox.find('ymin').text), 0), h), min(max(float(xmlbox.find('ymax').text), 0), h))
        bb = convert((w,h), b)
        with open(item.replace('/xmls/', '/labels/').replace('.xml', '.txt'), 'a+') as f:
            f.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
            f.close()
