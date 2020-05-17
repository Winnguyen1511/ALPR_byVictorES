from darkflow.net.build import TFNet
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import cv2
import imutils
import math
import argparse
import timeit
import time
import os
import recognitionmodules as rm

resources_path = 'resources/'

def opencvsecondCrop(img):
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray,210,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,39,1)
    edges = rm.auto_canny(thresh, sigma=0.1)
    # edges =thresh
    ctrs, hier = cv2.findContours(edges,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_TC89_L1)
    # areas = [cv2.contourArea(c) for c in contours]
    # if(len(areas)!=0):
    #     max_index = np.argmax(areas)
    #     cnt=contours[max_index]
    #     x,y,w,h = cv2.boundingRect(cnt)
    #     cv2.rectangle(thresh,(x,y),(x+w,y+h),(0,255,0),2)
    #     cv2.imshow('border',thresh)
    #     secondCrop = img[y:y+h,x:x+w]
    # else: 
    #     secondCrop = img
    # return secondCrop
    chosen_lst = []
    areas = []
    img_area = img.shape[0]*img.shape[1]
    # count = 0
    for i, ctr in enumerate(ctrs):
        x,y, w, h = cv2.boundingRect(ctr)
        roi_area = w*h
        non_max_sup = roi_area/img_area
        if non_max_sup > 0.75:
            # cv2.rectangle(img,(x,y),(x+w,y+h),(90,0,255),2)
            # count+=1
            chosen_lst.append([x,y,w,h])
            areas.append(roi_area)
    # print('> Num:',count)
    if len(chosen_lst) != 0:
        max_index = np.argmin(areas)
        x, y, w, h = chosen_lst[max_index]
        cv2.rectangle(img,(x,y), (x+w, y+h), (90,0,255),2)
        secondCrop = img[y:y+h,x:x+w]
    else:
        secondCrop = img
    cv2.imshow('image:', img)
    cv2.imshow('invert',edges)
    return secondCrop


def opencvCrop(image, yoloPlate):
    prediction = yoloPlate.return_predict(image)
    if len(prediction) > 0:
        image = rm.firstCrop(image, prediction)
        cv2.imshow('firstCrop',image)
        image = opencvsecondCrop(image)
        cv2.imshow('secondCrop',image)
    


def main():
    plateOptions = {"pbLoad": 'database/protobuf/yolo-plate.pb', "metaLoad": 'database/meta/yolo-plate.meta', "gpu": 0.9}
    yoloPlate = TFNet(plateOptions)
    os.chdir(resources_path)
    while True:
        print("Please enter the image (0 or q to exit)")
        image = input("> Input image: ")
        if(image == '0' or image == 'q'):
            break
        img = cv2.imread(image)
        start = time.time()
        opencvCrop(img, yoloPlate)
        stop = time.time()
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        t = stop - start
        print(">> Time:%.2fsec "%(t))
        print(">> FPS :%.2f"%(1/t))
    print("Exiting...")
if __name__ == '__main__':
    main()