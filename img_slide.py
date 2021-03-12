import numpy as np

import cv2
import json
import math
from tqdm import tqdm
from xml.etree import ElementTree as ET
import os

# return 多个(i,j ,img)，i,j对应行列索引，对应图像（y,x）
def slide_img(img, kernel_size, step):
    h,w,c = img.shape
    imgs = []
    starts_x = range(0,w-kernel_size-1,step)
    starts_y = range(0,h-kernel_size-1,step)
    n = 0
    padding_x = False
    padding_y = False
    new_w = w
    new_h = h
    if((w-kernel_size)%step != 0):
        new_w = ((w-kernel_size)/step+1)*step+kernel_size
    if((h-kernel_size)%step != 0 ):
        new_h = ((h-kernel_size)/step+1)*step+kernel_size
    new_img = np.zeros((int(new_h),int(new_w),c))
    new_img[:h,:w,:] = img
    #print(new_img)
    for i in starts_y:
        for j in starts_x:
            crop_img = new_img[i:i+kernel_size,j:j+kernel_size]
            #print(crop_img.shape)
            if(np.min(crop_img) > 10):
                imgs.append((i,j,crop_img))
    return imgs


def bbox_extract(cut_box, src_box, patch_size, iou_thresh=0.5):
    bbox = []
    cut_xmin, cut_ymin, cut_xmax, cut_ymax = cut_box
    for bb in src_box:
        xmin, ymin, xmax, ymax, category = bb
        area = (xmax - xmin) * (ymax - ymin)
        w = max(0, min(cut_xmax, xmax) - max(cut_xmin, xmin))
        h = max(0, min(cut_ymax, ymax) - max(cut_ymin, ymin))
        iou = w * h / area 
        if iou >= iou_thresh:
            x = max(0, xmin - cut_xmin)
            y = max(0, ymin - cut_ymin)
            bbox.append([x, y, min(patch_size[1] - 1, x + (xmax - xmin)), min(patch_size[0] - 1, y + (ymax - ymin)), category])
    return bbox


#img_raw = cv2.imread("/media/shawn/ubuntu_data/datasets/deep_learning_datasets/tianchi_tile/tile_round1_train_20201231/train_imgs/197_1_t20201119084916310_CAM2.jpg")

#imgs = slide_img(img_raw,640,200)


#for i,j,img in imgs:
#    print("(i,j):",i,j)
#     print(img)
#     img = img.astype(np.uint8)
#     cv2.imshow("xx",img)
#     cv2.waitKey(1000)

# cv2.destroyAllWindows()



img_paths = './train_imgs/'

with open('train_annos.json', 'r') as f:
    image_meta = json.load(f, encoding='etf-8')

each_img_meta = {}
for each_item in image_meta:
    each_img_meta[each_item['name']] = []

for idx, each_item in enumerate(image_meta):
    bbox = each_item['bbox']
    bbox.append(each_item['category'])
    each_img_meta[each_item['name']].append(bbox)


# 创建xml文件的函数
def create_tree(image_name, h, w):
    global annotation
    # 创建树根annotation
    annotation = ET.Element('annotation')
    # 创建一级分支folder
    folder = ET.SubElement(annotation, 'folder')
    # 添加folder标签内容
    folder.text = None

    # 创建一级分支filename
    filename = ET.SubElement(annotation, 'filename')
    filename.text = image_name

    # 创建一级分支source
    source = ET.SubElement(annotation, 'source')
    # 创建source下的二级分支database
    database = ET.SubElement(source, 'database')
    database.text = 'Unknown'

    # 创建一级分支size
    size = ET.SubElement(annotation, 'size')
    # 创建size下的二级分支图像的宽、高及depth
    width = ET.SubElement(size, 'width')
    width.text = str(w)
    height = ET.SubElement(size, 'height')
    height.text = str(h)
    depth = ET.SubElement(size, 'depth')
    depth.text = '3'

    # 创建一级分支segmented
    segmented = ET.SubElement(annotation, 'segmented')
    segmented.text = '0'


# 定义一个创建一级分支object的函数
def create_object(root, xi, yi, xa, ya, obj_name):  # 参数依次，树根，xmin，ymin，xmax，ymax
    # 创建一级分支object
    _object = ET.SubElement(root, 'object')
    # 创建二级分支
    name = ET.SubElement(_object, 'name')
    # print(obj_name)
    name.text = str(obj_name)
    pose = ET.SubElement(_object, 'pose')
    pose.text = 'Unspecified'
    truncated = ET.SubElement(_object, 'truncated')
    truncated.text = '0'
    difficult = ET.SubElement(_object, 'difficult')
    difficult.text = '0'
    #     # 创建bndbox
    bndbox = ET.SubElement(_object, 'bndbox')
    xmin = ET.SubElement(bndbox, 'xmin')
    xmin.text = '%s' % xi
    ymin = ET.SubElement(bndbox, 'ymin')
    ymin.text = '%s' % yi
    xmax = ET.SubElement(bndbox, 'xmax')
    xmax.text = '%s' % xa
    ymax = ET.SubElement(bndbox, 'ymax')
    ymax.text = '%s' % ya


def slice_img(img_name,img,kernel_size,step,boxes):
    h,w,c = img.shape
    imgs = []
    starts_x = range(0,w-kernel_size-1,step)
    starts_y = range(0,h-kernel_size-1,step)
    padding_x = False
    padding_y = False
    new_w = w
    new_h = h
    if((w-kernel_size)%step != 0):
        new_w = ((w-kernel_size)/step+1)*step+kernel_size
    if((h-kernel_size)%step != 0 ):
        new_h = ((h-kernel_size)/step+1)*step+kernel_size
    new_img = np.zeros((int(new_h),int(new_w),c))
    new_img[:h,:w,:] = img
    #print(new_img)
    for i in starts_y:
        for j in starts_x:
            y = i
            x = j
            b = y + kernel_size
            r = x + kernel_size
            annotations = []
            has_defect = False
            slice_img = new_img[i:i+kernel_size,j:j+kernel_size]
            if(np.max(slice_img) < 10):
                continue
            for e_box in boxes:
                if x < e_box[0] < r and y < e_box[1] < b and x < e_box[2] < r and y < e_box[3] < b:
                    e_box = [int(m) for m in e_box]
                    e_box[0] = math.floor(e_box[0] - x)
                    e_box[1] = math.floor(e_box[1] - y)
                    e_box[2] = math.ceil(e_box[2] - x)
                    e_box[3] = math.ceil(e_box[3] - y)
                    annotations.append(e_box)
                    has_defect = True
                    #print(crop_img.shape)
            if has_defect:
                create_tree(img_name, kernel_size, kernel_size)                
                for anno in annotations:
                    create_object(annotation, anno[0], anno[1], anno[2], anno[3], anno[4])
                tree = ET.ElementTree(annotation)
                slice_name=img_name[:-4]+'_'+str(x)+'_'+str(y)+'.jpg'
                xml_name=img_name[:-4]+'_'+str(x)+'_'+str(y)+'.xml'
                cv2.imwrite('./JPEGImages/' + slice_name, slice_img)
                print("wriete new img")
                tree.write('./Annotations/' + xml_name)
                if x < 0 or y < 0 or r > new_w or b > new_h:
                    print(each_item['name'])

    return



os.makedirs('./JPEGImages',exist_ok=True)
os.makedirs('./Annotations',exist_ok=True)
window_s = 608
step = 300
for image_name in tqdm(each_img_meta):
    # print(each_item)
    img = cv2.imread(os.path.join(img_paths,image_name))
    path = os.path.join(img_paths,image_name)
    print(path)
    boxes = each_img_meta[image_name]
    slice_img(image_name,img,window_s,step,boxes)

    # for anno in annotations:
    #     cv2.putText(slice_img, str(anno[4]), (int(anno[0]) - 5, int(anno[1]) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    #                 (0, 255, 0))
    #     cv2.rectangle(slice_img, (int(anno[0]), int(anno[1])), (int(anno[2]), int(anno[3])), (0, 255, 0), 2)
    # cv2.imshow('slice_img', slice_img)
    #
    # cv2.waitKey(1000)


