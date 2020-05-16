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
    # edges = rm.auto_canny(thresh_inv, sigma=0.1)
    edges = thresh_inv
    cv2.imshow('canny edge detection', edges)

    # ctrs, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
    ctrs, hier = cv2.findContours(edges.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
    # sorted_ctrs= sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
    sorted_ctrs = ctrs
    img_area = img.shape[0]*img.shape[1]
    count = 0
    # print(len(hier[0]))
    # print(hier)
    index_chosen_lst = []
    chosen_lst = []
    for i, ctr in enumerate(sorted_ctrs):
        x, y, w, h = cv2.boundingRect(ctr)
        roi_area = w*h
        non_max_sup = roi_area/img_area
        if((non_max_sup >= 0.02) and (non_max_sup < 0.09)):
            # if ((h>1.2*w) and (3*w>=h)):
            if h > w:
                # tmp =list(i,ctrs[i], hier[0][i] )
                index_chosen_lst.append(i)
                tmp = [cv2.boundingRect(ctrs[i]), list(hier[0][i])]
                chosen_lst.append(tmp)
                #cv2.rectangle(img, (x,y), (x+w, y+h), (90,0,255),2)
                #count += 1
    
        # cv2.rectangle(img, (x,y), (x+w, y+h), (90,0,255),2)
    # print(chosen_lst)
    # index_lst = [index for index in chosen_lst[0]]
    chosen_lst = filter(lambda query: query[1][3] not in index_chosen_lst, chosen_lst)
    chosen_lst = sorted(chosen_lst, key=lambda query: query[0][0])
    for i in range(0, len(chosen_lst)):
        x, y, w, h = chosen_lst[i][0]
        cv2.rectangle(img,(x,y), (x+w, y+h), (90,0,255),2)
        print(chosen_lst[i])
        count += 1
    cv2.imshow('segmentation', img)
    return count


def main():
    os.chdir(resources_path)
    while True:
        print("Please enter the image (0 or q to exit)")
        image = input("> Input image: ")
        if(image == '0' or image == 'q'):
            break 
        img = cv2.imread(image)
        start = time.time()
        count = opencvSegmentation(img)
        stop = time.time()
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        t = stop - start
        print(">> Num :%d"%(count))
        print(">> Time:%.2fsec "%(t))
        print(">> FPS :%.2f"%(1/t))
    print("Exiting...")

if __name__ == '__main__':
    main()