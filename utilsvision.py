
from PIL import Image, ImageDraw, ImageFont
import numpy

import torchvision

def my_nms(preds, iou_thres=0.5):
    keep = torchvision.ops.nms(preds[:,:3],preds[:,4],iou_thres)
    return [preds[keep]]

last_det = []

def smoothDet(det): 
    if last_det:
        last_det_ = last_det[0]
        for i, current_bbox in enumerate(det):
            for j,last_bbox in enumerate(last_det_):
                iou = computeIou(current_bbox[:4],last_bbox[:4])
                if(iou>0.9):
                    det[i,:4] = last_bbox[:4]
                    
                elif iou > 0.7:
                    det[i,:4] =  (det[i,:4] + last_bbox[:4])/2
        last_det[0] = det
    else:
        last_det.append(det)
    return det
                

def computeIou(pred1, pred2):
    x1_min, y1_min, x1_max, y1_max = pred1[:4]
    x2_min, y2_min, x2_max, y2_max = pred2[:4]
    x_min = min(x1_min, x2_min)
    w = max(0, min(x2_max, x1_max) - max(x1_min, x2_min))
    h = max(0, min(y2_max, y1_max) - max(y1_min, y2_min))
    area = (x1_max - x1_min) * (y1_max - y1_min) 
    area2 = (x2_max - x2_min) * (y2_max - y2_min)  
    iou = w * h / (area+area2-w*h) 
    return iou

def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, numpy.ndarray)):  #判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype(
        'NotoSansCJK-Black.ttc', textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)
    
# draw a 'rectange'
def draw_magic_rectangle(img, left, top, color, thickness, lineType=cv2.LINE_AA):
    corner_w = int((top[0]-left[0])*0.2)
    corner_h = int((top[1]-left[1])*0.2)
    cv2.line(img,left,(left[0],left[1]+corner_h),color,thickness)
    cv2.line(img,left,(left[0]+corner_w,left[1]),color,thickness)

    cv2.line(img,(top[0],left[1]),(top[0]-corner_w,left[1]),color,thickness)
    cv2.line(img,(top[0],left[1]),(top[0],left[1]+corner_h),color,thickness)

    cv2.line(img,(left[0],top[1]),(left[0]+corner_w,top[1]),color,thickness)
    cv2.line(img,(left[0],top[1]),(left[0],top[1]-corner_h),color,thickness)

    cv2.line(img,top,(top[0]-corner_w,top[1]),color,thickness)
    cv2.line(img,top,(top[0],top[1]-corner_h),color,thickness)
    return img


def plot_one_cn_box(x, img, color=None, label=None, line_thickness=None):
    # Plots one bounding box on image img
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))

    #cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    img = draw_magic_rectangle(img,c1, c2, color, thickness=7)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        #t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        #c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        #cv2.rectangle(img, 40, 40, color, -1, cv2.LINE_AA)  # filled
        #print(label)
        #print(tl / 3)
        top = c1[1]-45 if (c1[1]-45)>0 else c1[1]
        left = c1[0] if (c1[1]-45)>0 else c1[0]+5
        img = cv2ImgAddText(img,label,left, top ,(color[2],color[1],color[0]),30)
        return img

def draw_text(img,label=None,line_thickness=None):
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    if label:
        tf = max(tl - 1, 1)
        cv2.putText(img, label, (img.shape[0]/2+10, 10), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
