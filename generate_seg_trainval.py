import cv2
import os.path as ops
import os

def gen_train_sample(src_dir, b_gt_image_dir, i_gt_image_dir, image_dir):
    """
    generate sample index file
    :param src_dir:
    :param b_gt_image_dir:
    :param i_gt_image_dir:
    :param image_dir:
    :return:
    """

    with open('{:s}/train.txt'.format(src_dir), 'w') as file:

        for image_name in os.listdir(b_gt_image_dir):
            if not image_name.endswith('.png'):
                continue
            
            binary_gt_image_path = ops.join(b_gt_image_dir, image_name)
            instance_gt_image_path = ops.join(i_gt_image_dir, image_name)
            src_img_name = image_name[:-4]+'.jpg'
            image_path = ops.join(image_dir, src_img_name)
            print(binary_gt_image_path,instance_gt_image_path,image_path)

            assert ops.exists(image_path), '{:s} not exist'.format(image_path)
            assert ops.exists(instance_gt_image_path), '{:s} not exist'.format(instance_gt_image_path)

            b_gt_image = cv2.imread(binary_gt_image_path, cv2.IMREAD_COLOR)
            i_gt_image = cv2.imread(instance_gt_image_path, cv2.IMREAD_COLOR)
            image = cv2.imread(image_path, cv2.IMREAD_COLOR)

            if b_gt_image is None or image is None or i_gt_image is None:
                print('图像对: {:s}损坏'.format(image_name))
                continue
            else:
                info = '{:s} {:s} {:s}'.format(image_path, binary_gt_image_path, instance_gt_image_path)
                file.write(info + '\n')
    return

def main():
    path = 'donghang_data'
    image_dir = 'image'
    relative_gt_bin_img_path = 'gt_binary_image'
    relative_gt_object_img_path = 'gt_instance_image'
    gen_train_sample(path, ops.join(path,relative_gt_bin_img_path),ops.join(path,relative_gt_object_img_path),ops.join(path,image_dir))

if __name__ == "__main__":
    main()