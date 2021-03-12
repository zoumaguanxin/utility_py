# coding: utf-8
import os
import cv2
import codecs
from glob import glob
from tqdm import tqdm
import xml.etree.ElementTree as ET


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

if __name__ == "__main__":
    saved_path = './tile_round1_train_20201231/'
    os.makedirs(os.path.join(saved_path, 'cutimgs'), exist_ok=True)
    os.makedirs(os.path.join(saved_path, 'cutbg'), exist_ok=True)
    os.makedirs(os.path.join(saved_path, 'cutxmls'), exist_ok=True)
    filelists = glob(saved_path + 'imgs/*.jpg')
    patch_size = [800, 800]
    overlap = 0.2
    dx = int(patch_size[1] * (1 - overlap))
    dy = int(patch_size[0] * (1 - overlap))
    for item in tqdm(filelists):
        img = cv2.imread(item)
        H, W = img.shape[:2]
        if img is None:
            continue
        if H == 3500:
            ratio = 4
        else:
            ratio = 8
        tmp_img = cv2.resize(img, (W//ratio, H//ratio))
        tmp_gray = cv2.cvtColor(tmp_img, cv2.COLOR_BGR2GRAY)
        median = cv2.medianBlur(tmp_gray, 3)
        binary = 255 - cv2.adaptiveThreshold(median, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 5)
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        flag = 0
        for i in range(len(contours)):
            if cv2.contourArea(contours[i]) > cv2.contourArea(contours[flag]):
                flag = i
        x, y, w, h = cv2.boundingRect(contours[flag])
        x = max(0, (x - 10) * ratio)
        y = max(0, (y - 10) * ratio)
        w = min(W - x - 1, (w + 20) * ratio)
        h = min(H - y - 1, (h + 20) * ratio)
        img = img[y:y+h, x:x+w, :]
        H, W = img.shape[:2]
        tmp_box = []
        anns = ET.parse(item.replace('/imgs/', '/xmls/').replace('.jpg', '.xml'))
        tmp = anns.getroot() 
        for obj in tmp.findall('object'):
            if obj is None:
                break
            label = obj.find('name').text
            xmin = max(0, float(obj.find('bndbox').find('xmin').text) - x)
            ymin = max(0, float(obj.find('bndbox').find('ymin').text) - y)
            xmax = max(0, float(obj.find('bndbox').find('xmax').text) - x)
            ymax = max(0, float(obj.find('bndbox').find('ymax').text) - y)
            tmp_box.append([xmin, ymin, xmax, ymax, label])
        image_shape = (H, W)
        for i in range(0, image_shape[1], dx):
            for j in range(0, image_shape[0], dy):
                xmin = i if i + dx < image_shape[1] else image_shape[1] - patch_size[1]
                ymin = j if j + dy < image_shape[0] else image_shape[0] - patch_size[0]
                xmax = xmin + patch_size[1]
                ymax = ymin + patch_size[0]
                bbox = bbox_extract([xmin, ymin, xmax, ymax], tmp_box, patch_size)
                cut_img = img[ymin:ymax, xmin:xmax, :]
                if len(bbox) > 0:
                    name = str(len(os.listdir(os.path.join(saved_path, 'cutxmls'))) + 1).zfill(5)
                    with codecs.open(os.path.join(saved_path, 'cutxmls') + '/' + name + '.xml', 'w', 'utf-8') as xml:
                        xml.write('<annotation>\n')
                        xml.write('\t<filename>' + name + '.jpg' + '</filename>\n')
                        xml.write('\t<size>\n')
                        xml.write('\t\t<width>'+ str(patch_size[1]) + '</width>\n')
                        xml.write('\t\t<height>'+ str(patch_size[0]) + '</height>\n')
                        xml.write('\t\t<depth>' + str(3) + '</depth>\n')
                        xml.write('\t\t<segmented>0</segmented>\n')
                        xml.write('\t</size>\n')
                        for idx, bb in enumerate(bbox):
                            xml.write('\t<object>\n')
                            xml.write('\t\t<name>' + str(bb[-1]) + '</name>\n')
                            xml.write('\t\t<pose>Unspecified</pose>\n')
                            xml.write('\t\t<truncated>1</truncated>\n')
                            xml.write('\t\t<difficult>0</difficult>\n')
                            xml.write('\t\t<bndbox>\n')
                            xml.write('\t\t\t<xmin>' + str(bb[0]) + '</xmin>\n')
                            xml.write('\t\t\t<ymin>' + str(bb[1]) + '</ymin>\n')
                            xml.write('\t\t\t<xmax>' + str(bb[2]) + '</xmax>\n')
                            xml.write('\t\t\t<ymax>' + str(bb[3]) + '</ymax>\n')
                            xml.write('\t\t</bndbox>\n')
                            xml.write('\t</object>\n')
                        xml.write('</annotation>')
                        cv2.imwrite(os.path.join(saved_path, 'cutimgs') + '/' + name + '.jpg', cut_img)
                else:
                    name = str(len(os.listdir(os.path.join(saved_path, 'cutbg'))) + 1).zfill(5)
                    cv2.imwrite(os.path.join(saved_path, 'cutbg') + '/bg_' + name + '.jpg', cut_img)
