
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

MIN_WIDTH = 300
MIN_HEIGHT = 80

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

def plateRecog(image, yoloPlate, yoloCharacter, characterRecognition):
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
    # print(">>Origin: Width: ", w, ", Height: ", h)
    if w < MIN_WIDTH or h < MIN_HEIGHT:
        w_scale = math.ceil(MIN_WIDTH / w)
        h_scale = math.ceil(MIN_HEIGHT / h)
        scale = max(w_scale, h_scale)
        w = w * scale
        h = h * scale
    # print(">>Scale up: Width: ", w, ", Height: ", h)
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_CUBIC)
    imcv = im.copy()
    #Character Segmentation by YOLO:
    charPrediction = yoloCharacter.return_predict(im)
    #character detection:
    result = rm.yoloCharDetection(charPrediction, im, characterRecognition)
    print(">>Plate number CNN: ", result)
    
    # print(result)
    result = rm.opencvReadPlate(imcv, characterRecognition)
    print(">>Plate number OpenCV: ", result)
    
    return True


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

    args = parser.parse_args()
    workspace = args.workspace
    os.chdir(workspace)
    
    platePbDir = args.platePb
    plateMetaDir = args.plateMeta

    charPbDir = args.charPb
    charMetaDir = args.charMeta

    charCnnDir = args.charCnn

    gpuMode = float(args.gpuMode)
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
    while(True):
        print("Please enter the image (0 or q to exit)")
        image = input("> Input image: ")
        if(image == '0' or image == 'q'):
            break  
        # image = workspace + image 
        start = timeit.default_timer()
        res = plateRecog(image, yoloPlate, yoloCharacter, characterRecognition)
        stop = timeit.default_timer()
        print("Runtime: ", stop - start)
        if(res == True):
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            print("******************************")
        
    print(">>> Exiting...")
main()

