import os
import cv2
import argparse



def getMaxSize(img_dir):
    lstWidth =[]
    lstHeight =[]
    if img_dir == ".":
        img_dir = ""
    elif not img_dir.endswith("/"):
        img_dir = img_dir+"/"
    
    lstImg = [img_dir+fname for fname in os.listdir(img_dir)]
    for i in range(0, len(lstImg)):
        im = cv2.imread(lstImg[i])
        lstWidth.append(im.shape[1])
        lstHeight.append(im.shape[0])
    return max(lstWidth), max(lstHeight)
def getMinSize(img_dir):
    lstWidth =[]
    lstHeight =[]
    if img_dir == ".":
        img_dir = ""
    elif not img_dir.endswith("/"):
        img_dir = img_dir+"/"
    
    lstImg = [img_dir+fname for fname in os.listdir(img_dir)]
    for i in range(0, len(lstImg)):
        im = cv2.imread(lstImg[i])
        lstWidth.append(im.shape[1])
        lstHeight.append(im.shape[0])
    return min(lstWidth), min(lstHeight)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('img_dir')
    args = parser.parse_args()
    img_dir = args.img_dir
    max = getMaxSize(img_dir)
    min = getMinSize(img_dir)
    print("Max width: %d, height: %d"%(max[0], max[1]))
    print("Min width: %d, height: %d"%(min[0], min[1]))

if __name__ == '__main__':
    main()