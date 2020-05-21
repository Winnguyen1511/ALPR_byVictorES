import cv2
import numpy as np
import math
import argparse
import os
from functools import reduce
from progress.bar import IncrementalBar


def imgContrast(im):
    rms_contrast = 0
    im = np.array(im)
    h = im.shape[0]
    w = im.shape[1]
    depth = im.shape[2]

    for i in range(0,depth):
        tmp = im[:,:, i]
        # tmp = tmp.reshape(h * w)
        tmp = tmp/255
        # np.concatenate([[0], tmp])
        avr_I = np.sum(tmp)/ (w*h)
        # rms = reduce(lambda total, next: total + (next - avr_I)*(next - avr_I), tmp)
        rms = (tmp - avr_I)**2
        rms = np.sum(rms)
        rms = rms / (h * w)
        rms = math.sqrt(rms)
        rms_contrast += rms
    rms_contrast = rms_contrast / depth
    return rms_contrast

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image_dir')
    args = parser.parse_args()
    image_dir = args.image_dir
    file_lst = os.listdir(image_dir)
    img_lst = [name for name in file_lst if name.endswith('.jpg') 
                                            or name.endswith('.jpeg')
                                            or name.endswith('.png')
                                            or name.endswith('.raw')]
    # print(img_lst)
    os.chdir(image_dir)
    # contrast_lst = [imgContrast(cv2.imread(img_name)) for img_name in img_lst]
    contrast_lst = []
    bar = IncrementalBar('Calculating', max=len(img_lst))
    for i in range(0,len(img_lst)):
        contrast_lst.append(imgContrast(cv2.imread(img_lst[i])))
        # print(img_lst[i])
        bar.next()
    bar.finish()
    max_contrast = max(contrast_lst)
    min_contrast = min(contrast_lst)
    avr_contrast = reduce(lambda a,b: a+b, contrast_lst) / len(contrast_lst)
    print("> Min=%.2f, Max=%.2f"%(min_contrast, max_contrast))
    print("> average=%.2f"%(avr_contrast))
if __name__ == "__main__":
    main()