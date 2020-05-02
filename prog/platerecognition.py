
from darkflow.net.build import TFNet
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import cv2
import imutils
import argparse
import math
import recognitionmodules as rm
import timeit
import time
import os
import datetime

from progress.bar import IncrementalBar

MIN_WIDTH = 460
MIN_HEIGHT = 100

MAX_WIDTH = 1200
MAX_HEIGHT = 290
# dir = '/home/khoa/AI_DeepLearning/LicensePlateRecognition/LicensePlateRecognition/'
# # imageDir = dir+'resources/'

# platePbDir = dir +'database/protobuf/yolo-plate.pb'
# plateMetaDir = dir+'database/meta/yolo-plate.meta'

# charPbDir = dir+'database/protobuf/yolo-character.pb'
# charMetaDir = dir+'database/meta/yolo-character.meta'

# charCnnDir = dir+'database/character_recognition.h5'

# gpuMode = 0.9
def sysInit(platePb, plateMeta, charPb, charMeta,charCnn, gpu):
    plateOptions = {"pbLoad": platePb, "metaLoad": plateMeta, "gpu": gpu}
    yoloPlate = TFNet(plateOptions)

    charOptions = {"pbLoad": charPb, "metaLoad": charMeta, "gpu":gpu}
    yoloCharacter = TFNet(charOptions)

    characterRecognition = tf.keras.models.load_model(charCnn)

    return yoloPlate, yoloCharacter, characterRecognition

def plateRecogTest(yoloPlate, yoloCharacter, characterRecognition, testfile):
    print(">> Testing mode:")

    testList = {}
    file = open(testfile, 'r')
    line =file.readline()
    while line and line != '\n':
        entry = line.split(" ")
        tmp = {entry[0]: entry[1].strip('\n')}
        testList.update(tmp)
        line =file.readline()
    # print(testList)
    total = len(testList)
    countCNN = 0
    countOpenCV = 0
    bar = IncrementalBar('Tesing', max=total)
    t = datetime.datetime.now()
    logname = 'log'+t.strftime("%y_%m_%d_%H%M%S")
    logfile = open(logname, 'w')

    for key in testList.keys():
        resMan = testList[key]
        _,resCNN, resOpenCV = plateRecog(key,yoloPlate, yoloCharacter, characterRecognition, show=False)
        if resCNN == resMan:
            countCNN += 1
        if resOpenCV == resMan:
            countOpenCV += 1
        tmp = key+' man:'+resMan+' cnn:'+resCNN+' opencv:'+resOpenCV+'\n'
        logfile.write(tmp)
        bar.next()
    bar.finish()
    logfile.close()
    print(">> Testing Finished!")
    print("> CNN: %.2f %%" %(countCNN*100/total))
    print("> OpenCV: %.2f %%"%(countOpenCV*100/total))


def plateRecog(image, yoloPlate, yoloCharacter, characterRecognition, show=True):
    #Init the recognition configuration:
    
    #Start:
    im = cv2.imread(image)
    if type(im) == type(None):
        print("> Error: Cannot read/find image ", image)
        return False
    
    #Plate detection by YOLO:
    platePrediction = yoloPlate.return_predict(im)
    # print(len(platePrediction))
    #Crop the plate out and second crop to reduce some background:
    if len(platePrediction) > 0:
        im = rm.firstCrop(im, platePrediction)
        # cv2.imwrite('test.jpg', im)
        im = rm.secondCrop(im)
        # cv2.imwrite('test2.jpg', im)
    
    
    #resize the capture of plate before we detect the character:
    imsize = im.shape
    w = imsize[1]
    h = imsize[0]
    if(show== True):
        print(">>Origin: Width: ", w, ", Height: ", h)
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
    if show == True:
        print(">>Scale up: Width: ", w, ", Height: ", h)
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_CUBIC)
    imcv = im.copy()
    #Character Segmentation by YOLO:
    charPrediction = yoloCharacter.return_predict(im)
    #character detection:
    resultCNN = rm.yoloCharDetection(charPrediction, im, characterRecognition, show=show) 
    
    resultOpenCV = rm.opencvReadPlate(imcv, characterRecognition, show=show)
    if show == True:
        print(">>Plate number CNN: ", resultCNN)
        print(">>Plate number OpenCV: ", resultOpenCV)
    
    return True, resultCNN, resultOpenCV


def main():
    #arguments parser:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    parser.add_argument("platePb")
    parser.add_argument("plateMeta")
    parser.add_argument("charPb")
    parser.add_argument("charMeta")
    parser.add_argument("charCnn")
    parser.add_argument("gpuMode")
    parser.add_argument("testmode")
    parser.add_argument("testfile")
    args = parser.parse_args()
    workspace = args.workspace
    os.chdir(workspace)
    
    platePbDir = args.platePb
    plateMetaDir = args.plateMeta

    charPbDir = args.charPb
    charMetaDir = args.charMeta

    charCnnDir = args.charCnn

    gpuMode = float(args.gpuMode)

    testmode = args.testmode
    testfile =args.testfile
    #Start to run the program:
    yoloPlate, yoloCharacter, characterRecognition = sysInit(platePbDir, plateMetaDir,
                charPbDir, charMetaDir, charCnnDir, gpuMode)
    for i in range(0,5):    
        print(".")
    time.sleep(0.5)
    print(">>> Init Completed.")
    time.sleep(0.5)
    print(">>> Ready!")
    time.sleep(1)
    os.system('clear')
    print("*****PLATE RECOGNITION*****")
    print("> Workspace: ",workspace)
    print("> GPU mode: ", gpuMode * 100,"%")
    if(testmode == 'normal'):
        while(True):
            print("Please enter the image (0 or q to exit)")
            image = input("> Input image: ")
            if(image == '0' or image == 'q'):
                break 
            # image = workspace + image 
            start = timeit.default_timer()
            res, _, _ = plateRecog(image, yoloPlate, yoloCharacter, characterRecognition)
            stop = timeit.default_timer()
            print("Runtime: ", stop - start)
            if(res == True):
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                print("******************************") 
        print(">>> Exiting...")
    elif testmode == 'test':
        if(testfile != ''):
            if(os.path.isfile(testfile) == False):
                print("Error: no such file or directory!")
            else:
                plateRecogTest(yoloPlate, yoloCharacter, characterRecognition, testfile)
    else:
        print("Error: Wrong operation mode!")
    
    
main()

