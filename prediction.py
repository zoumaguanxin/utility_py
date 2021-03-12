# -*- coding: utf-8 -*
import os
import cv2
import torch
import numpy as np
from path import MODEL_PATH
from flyai.framework import FlyAI
from models.experimental import attempt_load
from utils.general import non_max_suppression

LABELS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 
          'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI', 'XXII', 'XXIII', 'XXIV']
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Prediction(FlyAI):
    def load_model(self):
        self.model = attempt_load(os.path.join(MODEL_PATH, 'best.pt'), map_location=device) 
        self.model.eval()

    def preprocess_img(self, img, resize=800, maxsize=800, INPUT=(800, 800), color=(114, 114, 114)):
        h, w = img.shape[:2]
        ratio = resize / min(h, w)
        if ratio * max(h, w) > maxsize:
            ratio = maxsize / max(h, w)
        img_resize = cv2.resize(img, (int(ratio*w), int(ratio*h)))
        pw = INPUT[0] - img_resize.shape[1] 
        ph = INPUT[1] - img_resize.shape[0] 
        img = cv2.copyMakeBorder(img_resize, 0, ph, 0, pw, cv2.BORDER_CONSTANT, value=color)
        return img, ratio, h, w

    def predict(self, image_path):
        image_name = os.path.basename(image_path)
        img = cv2.imread(image_path)
        img_ratio, ratio, h, w = self.preprocess_img(img)
        img_ratio = cv2.cvtColor(img_ratio, cv2.COLOR_BGR2RGB)
        input = torch.from_numpy(img_ratio.transpose((2, 0 ,1))).float().div(255.0).unsqueeze(0).to(device)
        pred = self.model(input, augment=False)[0] 
        pred = non_max_suppression(pred, conf_thres=0.4, iou_thres=0.5)[0]   
        pred_result = [] 
        if pred is not None and len(pred)>0:
            pred[:, :4] /= ratio
            pred[:, 0].clamp_(0, w)
            pred[:, 1].clamp_(0, h)
            pred[:, 2].clamp_(0, w)
            pred[:, 3].clamp_(0, h)
            pred = pred.detach().cpu().numpy()
            pred = pred[np.argsort(-pred[:,-2])]
            for idx, bb in enumerate(pred):
                if idx >= 80:
                    break
                x1,y1,x2,y2 = list(map(int, bb[:4]))
                res = dict()
                res["image_name"] = image_name
                res["label_name"] = LABELS[int(bb[-1])]
                res["bbox"] = [x1, y1, x2 - x1, y2 - y1]
                res["confidence"] = float(bb[-2])
                pred_result.append(res)
        return pred_result