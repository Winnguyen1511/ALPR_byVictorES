import cv2
import numpy as np
import math
import argparse
import os
from functools import reduce
from progress.bar import IncrementalBar

def imgBrightness(im):
    im = np.array(im)
    h = im.shape[0]
    w = im.shape[1]
    b = im[:, :, 0] / 255
    g = im[:, :, 1] / 255
    r = im[:, :, 2] / 255
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    return np.sum(brightness)/(w*h)

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
    brightness_lst = []
    bar = IncrementalBar('Calculating', max=len(img_lst))
    for i in range(0,len(img_lst)):
        brightness_lst.append(imgBrightness(cv2.imread(img_lst[i])))
        # print(img_lst[i])
        bar.next()
    bar.finish()
    max_contrast = max(brightness_lst)
    min_contrast = min(brightness_lst)
    avr_contrast = reduce(lambda a,b: a+b, brightness_lst) / len(brightness_lst)
    print("> Min=%.2f, Max=%.2f"%(min_contrast, max_contrast))
    print("> average=%.2f"%(avr_contrast))

if __name__ == '__main__':
    main()