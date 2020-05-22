from darkflow.net.build import TFNet
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import cv2
import imutils
import math


MIN_WIDTH = 300
MIN_HEIGHT = 80

MAX_WIDTH = 600
MAX_HEIGHT = 160

SECOND_CROP_LOWLIM = 0.7
SECOND_CROP_HIGHLIM = 0.9

SEGMENT_LOWLIM = 0.02
SEGMENT_HIGHLIM = 0.09

INVERT_LIM = 200

def firstCrop(img, predictions, show=True):
    predictions.sort(key=lambda x: x.get('confidence'))
    xtop = predictions[-1].get('topleft').get('x')
    ytop = predictions[-1].get('topleft').get('y')
    xbottom = predictions[-1].get('bottomright').get('x')
    ybottom = predictions[-1].get('bottomright').get('y')
    firstCrop = img[ytop:ybottom, xtop:xbottom]
    if show == True:
        tmpImg = img.copy()
        cv2.rectangle(tmpImg,(xtop,ytop),(xbottom,ybottom),(0,255,0),3)
        imsize = tmpImg.shape
        w = imsize[1]
        h = imsize[0]
        if w < MIN_WIDTH or h < MIN_HEIGHT:
            w_scale = math.ceil(MIN_WIDTH / w)
            h_scale = math.ceil(MIN_HEIGHT / h)
            scale = max(w_scale, h_scale)
            w = w * scale
            h = h * scale
        if w > MAX_WIDTH or h > MAX_HEIGHT:
            w_scale = math.ceil(w / MAX_WIDTH)
            h_scale = math.ceil(h / MAX_HEIGHT)
            scale = min(w_scale, h_scale)
            w = math.floor(w / scale)
            h = math.floor(h / scale)
        tmpImg = cv2.resize(tmpImg, (w, h), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('Detection',tmpImg)
    return firstCrop
    

def secondCrop(img, show=True):
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    thresh =  cv2.adaptiveThreshold(gray,INVERT_LIM,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,39,1)
    edges = auto_canny(thresh, sigma=0.1)
    
    cv_version = cv2.__version__
    if cv_version == '4.2.0':
        ctrs,_ = cv2.findContours(edges,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_TC89_L1)
    elif cv_version == '3.2.0':
        _,ctrs,_ = cv2.findContours(edges,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_TC89_L1)
    chosen_lst = []
    areas = []
    img_area = img.shape[0]*img.shape[1]
    # count = 0
    for i, ctr in enumerate(ctrs):
        x,y, w, h = cv2.boundingRect(ctr)
        roi_area = w*h
        non_max_sup = roi_area/img_area
        if non_max_sup > SECOND_CROP_LOWLIM and non_max_sup <=SECOND_CROP_HIGHLIM:
            chosen_lst.append([x,y,w,h])
            areas.append(roi_area)
    if len(chosen_lst) != 0:
        max_index = np.argmin(areas)
        x, y, w, h = chosen_lst[max_index]
        # cv2.rectangle(img,(x,y), (x+w, y+h), (90,0,255),2)
        secondCrop = thresh[y:y+h,x:x+w]
        # retimg = img[y:y+h,x:x+w]
    else:
        secondCrop = thresh
        # retimg = img
    if show == True:
        cv2.imshow('canny',edges)
        cv2.imshow('thresh', thresh)
    # return retimg, secondCrop
    return secondCrop
def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
 
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
 
    # return the edged image
    return edged


def opencvReadPlate(img, characterRecognition, show=True):
    charList=[]
    cv_version = cv2.__version__
    if cv_version == '4.2.0':
        ctrs, hier = cv2.findContours(img.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
    elif cv_version == '3.2.0':
        _, ctrs, hier = cv2.findContours(img.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
    # sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
    img_area = img.shape[0]*img.shape[1]

    index_chosen_lst = []
    chosen_lst = []
    for i, ctr in enumerate(ctrs):
        x, y, w, h = cv2.boundingRect(ctr)
        roi_area = w*h
        non_max_sup = roi_area/img_area

        if((non_max_sup >= SEGMENT_LOWLIM) and (non_max_sup < SEGMENT_HIGHLIM)):
            # if ((h>1.2*w) and (3*w>=h)):
            if(h > w):
                index_chosen_lst.append(i)
                tmp = [cv2.boundingRect(ctr), list(hier[0][i])]
                chosen_lst.append(tmp)
    chosen_lst = filter(lambda query: query[1][3] not in index_chosen_lst, chosen_lst)
    chosen_lst = sorted(chosen_lst, key=lambda query: query[0][0])
    for i in range(0,len(chosen_lst)):
        x, y, w, h = chosen_lst[i][0]
        char = img[y:y+h,x:x+w]
        charList.append(cnnCharRecognition(char,characterRecognition))
        cv2.rectangle(img,(x,y), (x+w, y+h), (90,0,255),2)
    if(show == True):
        tmpImg = img.copy()
        imsize = tmpImg.shape
        w = imsize[1]
        h = imsize[0]
        if w < MIN_WIDTH or h < MIN_HEIGHT:
            w_scale = math.ceil(MIN_WIDTH / w)
            h_scale = math.ceil(MIN_HEIGHT / h)
            scale = max(w_scale, h_scale)
            w = w * scale
            h = h * scale
        if w > MAX_WIDTH or h > MAX_HEIGHT:
            w_scale = math.ceil(w / MAX_WIDTH)
            h_scale = math.ceil(h / MAX_HEIGHT)
            scale = min(w_scale, h_scale)
            w = math.floor(w / scale)
            h = math.floor(h / scale)
        tmpImg = cv2.resize(tmpImg, (w, h), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('OpenCV character segmentation',tmpImg)
    licensePlate="".join(charList)
    return licensePlate

def cnnCharRecognition(img,characterRecognition):
    dictionary = {0:'0', 1:'1', 2 :'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'A',
    11:'B', 12:'C', 13:'D', 14:'E', 15:'F', 16:'G', 17:'H', 18:'1', 19:'J', 20:'K',
    21:'L', 22:'M', 23:'N', 24:'P', 25:'Q', 26:'R', 27:'S', 28:'1', 29:'U',
    30:'V', 31:'W', 32:'X', 33:'Y', 34:'Z'}
    # print(img.shape)
    # blackAndWhiteChar=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # blackAndWhiteChar = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,39,1)
    blackAndWhiteChar = img
    # print(blackAndWhiteChar.shape)
    blackAndWhiteChar = cv2.resize(blackAndWhiteChar,(75,100))
    # image = blackAndWhiteChar.reshape((1, 100,75, 1))
    image = np.array(blackAndWhiteChar.reshape(1,100,75, 1))
    image = image / 255.0
    new_predictions = characterRecognition.predict(image)
    
    char = np.argmax(new_predictions)
    # print("> Char=", dictionary[char])
    # prob = np.amax(new_predictions)
    # print("> Prob=%.3f"%(prob))
    return dictionary[char]

def yoloCharDetection(predictions,img, charRecognition,show=True):
    charList = []
    positions = []
    for i in predictions:
        if i.get("confidence")>0.10:
            xtop = i.get('topleft').get('x')
            positions.append(xtop)
            ytop = i.get('topleft').get('y')
            xbottom = i.get('bottomright').get('x')
            ybottom = i.get('bottomright').get('y')
            char = img[ytop:ybottom, xtop:xbottom]
            cv2.rectangle(img,(xtop,ytop),( xbottom, ybottom ),(255,0,0),2)
            charList.append(cnnCharRecognition(char, charRecognition))
    if(show == True):
        tmpImg = img.copy()
        imsize = tmpImg.shape
        w = imsize[1]
        h = imsize[0]
        if w < MIN_WIDTH or h < MIN_HEIGHT:
            w_scale = math.ceil(MIN_WIDTH / w)
            h_scale = math.ceil(MIN_HEIGHT / h)
            scale = max(w_scale, h_scale)
            w = w * scale
            h = h * scale
        if w > MAX_WIDTH or h > MAX_HEIGHT:
            w_scale = math.ceil(w / MAX_WIDTH)
            h_scale = math.ceil(h / MAX_HEIGHT)
            scale = min(w_scale, h_scale)
            w = math.floor(w / scale)
            h = math.floor(h / scale)
        tmpImg = cv2.resize(tmpImg, (w, h), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('Yolo character segmentation',tmpImg)
    sortedList = [x for _,x in sorted(zip(positions,charList))]
    licensePlate="".join(sortedList)
    return licensePlate



