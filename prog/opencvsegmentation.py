# from darkflow.net.build import TFNet
# import tensorflow as tf
# from tensorflow.keras import layers, models
import numpy as np
import cv2
import imutils
import math
import argparse
import timeit
import time
import os
import recognitionmodules as rm

MIN_WIDTH = 300
MIN_HEIGHT = 80

MAX_WIDTH = 600
MAX_HEIGHT = 160

resources_path = 'resources/'

def opencvSegmentation(img):
    charList = []
    cv2.imshow('original', img)
    gray =cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh_inv = cv2.adaptiveThreshold(gray,200,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,39,1)
    cv2.imshow('invert color', thresh_inv)
    edges = rm.auto_canny(thresh_inv, sigma=0.1)
    cv2.imshow('canny edge detection', edges)

    # ctrs, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
    ctrs, _ = cv2.findContours(edges.copy(), cv2.CCL_GRANA, cv2.CHAIN_APPROX_TC89_L1)
    sorted_ctrs= sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
    img_area = img.shape[0]*img.shape[1]

    for i, ctr in enumerate(sorted_ctrs):
        x, y, w, h = cv2.boundingRect(ctr)
        roi_area = w*h
        non_max_sup = roi_area/img_area
        if((non_max_sup >= 0.03) and (non_max_sup < 0.09)):
            if ((h>1.2*w) and (3*w>=h)):
                cv2.rectangle(img, (x,y), (x+w, y+h), (90,0,255),2)
    cv2.imshow('segmentation', img)


def main():
    os.chdir(resources_path)
    while True:
        print("Please enter the image (0 or q to exit)")
        image = input("> Input image: ")
        if(image == '0' or image == 'q'):
            break 
        img = cv2.imread(image)
        opencvSegmentation(img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    print("Exiting...")

if __name__ == '__main__':
    main()