import os
import cv2

import argparse

def rgbtogray(rgb_dir, gray_dir):
    if rgb_dir == gray_dir:
        print("Error: Cannot override original directory!")
        return False
    if not os.path.isdir(rgb_dir):
        print("Error: No such file or directory ", rgb_dir)
        return False
    #Creating gray directory:
    print("Reading directory ", rgb_dir)
    rgb_dir_tree = [root for root,_,_ in os.walk(rgb_dir)]
    gray_dir_tree = [root.replace(rgb_dir, gray_dir) for root in rgb_dir_tree]
    # print(rgb_dir_tree)
    # print(gray_dir_tree)
    for i in range(0, len(gray_dir_tree)):
        if not os.path.exists(gray_dir_tree[i]):
            os.makedirs(gray_dir_tree[i])
    
    #converting brg to gray:
    lstOrgImg = []
    lstGrayImg = []
    for root, _, files in os.walk(rgb_dir):
        if len(files) != 0:
            orgPaths = [root + "/"+file for file in files if file.endswith(".png")
                                                            or file.endswith(".jpg")
                                                            or file.endswith(".jpeg")]

            # rootGray = root.replace(rgb_dir, gray_dir)
            # grayPaths = [rootGray + "/"+file for file in files if file.endswith(".png")
            #                                                 or file.endswith(".jpg")
            #                                                 or file.endswith(".jpeg")]

            lstOrgImg.extend(orgPaths)
            # lstGrayImg.extend(grayPaths)
    # print(lstOrgImg)
    # print(lstGrayImg)
    # if(len(lstOrgImg) != len(lstGrayImg)):
    #     print("Error: Internal error!")
    #     return False

    for i in range(0, len(lstOrgImg)):
        orgPath = lstOrgImg[i]
        grayPath = orgPath.replace(rgb_dir, gray_dir)
        im = cv2.imread(orgPath)
        imGray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        # print(imGray.shape)
        cv2.imwrite(grayPath, imGray)
    print("Complete converting %d images to gray"%i)
    
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('rgb_dir')
    parser.add_argument('gray_dir')
    args = parser.parse_args()

    rgb_dir = args.rgb_dir
    gray_dir = args.gray_dir

    res = rgbtogray(rgb_dir, gray_dir)
    if res == False:
        print('Error!')
    else:
        print('Success!')
    return res

if __name__ == '__main__':
    main()