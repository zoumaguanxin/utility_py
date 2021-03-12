from glob import glob
import os.path as op

from shutil import copy

path = 'labels'
img_path = 'image'
new_path = 'annoted_images'
annotations = glob(op.join(path,'*.json'))
images = glob(op.join(img_path,'*.jpg'))

for annotation in annotations:
    path , name = op.split(annotation)
    #print(path,name)
    name = name[:-5]
    for image in images:
        img_path, img_name = op.split(image)
        if name==img_name[:-4]:
            copy(image,op.join(new_path,img_name))
            print("copy image",image, "to",op.join(new_path,img_name))
        

