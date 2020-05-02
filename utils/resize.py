import os
import cv2
import argparse

width = 75
height = 100

def autoResize(input_dir, output_dir):
    if input_dir == output_dir:
        print("Error: Cannot override original directory!")
        return False
    if not os.path.isdir(input_dir):
        print("Error: No such file or directory ", input_dir)
        return False
    #Creating gray directory:
    print("Reading directory ", input_dir)
    input_dir_tree = [root for root,_,_ in os.walk(input_dir)]
    output_dir_tree = [root.replace(input_dir, output_dir) for root in input_dir_tree]
    # print(input_dir_tree)
    # print(output_dir_tree)
    for i in range(0, len(output_dir_tree)):
        if not os.path.exists(output_dir_tree[i]):
            os.makedirs(output_dir_tree[i])
    
    #converting brg to gray:
    lstOrgImg = []
    #lstGrayImg = []
    for root, _, files in os.walk(input_dir):
        if len(files) != 0:
            orgPaths = [root + "/"+file for file in files if file.endswith(".png")
                                                            or file.endswith(".jpg")
                                                            or file.endswith(".jpeg")]

            # rootGray = root.replace(input_dir, output_dir)
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
        resizePath = orgPath.replace(input_dir, output_dir)
        im = cv2.imread(orgPath)
        im = cv2.resize(im, (width, height), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(resizePath, im)
    print("Complete resizing %d images to gray"%i)
    
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    res = autoResize(input_dir, output_dir)
    if not res:
        print('Rename Error')
        return False
    print('Rename completed!')
    return True
if __name__ == '__main__':
    main()