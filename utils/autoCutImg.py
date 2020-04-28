import xml.etree.ElementTree as ET
import os
import cv2
import argparse
from progress.bar import IncrementalBar


OBJECT='object'
BNDBOX='bndbox'
NAME='name'
XMIN ='xmin'; YMIN ='ymin'; XMAX ='xmax'; YMAX = 'ymax'
XML=0; IMAGE=1; ROOT=2
lstQuery = []
class Object:
    def __init__(self, obj):
        
        if not isinstance(obj,ET.Element):
            print("Error: Wrong type input!")
            print("Expected ET.Element, got ", type(obj))
            return None

        self.name = obj.find(NAME).text
        bndbox = obj.find(BNDBOX)
        self.xmin = int(bndbox.find(XMIN).text)
        self.ymin = int(bndbox.find(YMIN).text)
        self.xmax = int(bndbox.find(XMAX).text)
        self.ymax = int(bndbox.find(YMAX).text)
    
def autoCropImg(xmlDir, imgDir, cropDir):
    global lstQuery
    #Check validity first:
    check = checkValid(xmlDir, imgDir)
    if not check:
        print("Error: Please check your database for missing images!")
        return False
    #handle with folder format:
    if xmlDir == '.':
        xmlDirSuffix = ""
    else:
        if not xmlDir.endswith('/'):
            xmlDirSuffix = xmlDir+"/"
        else:
            xmlDirSuffix = xmlDir
    if imgDir == '.':
        imgDirSuffix = ""
    else:
        if not imgDir.endswith('/'):
            imgDirSuffix = imgDir+"/"
        else:
            imgDirSuffix = imgDir
    if cropDir == '.':
        cropDirSuffix = ""
    else:
        if not cropDir.endswith('/'):
            cropDirSuffix = cropDir+"/"
        else:
            cropDirSuffix = cropDir

    
    # lstXml = [xmlDirSuffix+xml for xml in os.listdir(xmlDir) if xml.endswith('.xml')]
    # lstImg = [imgDirSuffix+img for img in os.listdir(imgDir)
    lstXml = [xml for xml in os.listdir(xmlDir) if xml.endswith('.xml')]
    lstImg = [img for img in os.listdir(imgDir)
                    if img.endswith('.png')
                    or img.endswith('.jpg')
                    or img.endswith('.jpeg')]
    lstXmlNoExt = [name.strip('.xml') for name in lstXml]
    lstImgNoExt = [name.split('.')[0] for name in lstImg]
    lstValidImg = []
    for i in range(0, len(lstXmlNoExt)):
        index = lstImgNoExt.index(lstXmlNoExt[i])
        lstValidImg.append(lstImg[index])
    # lstValidImg = [img for img in lstImg if img.split('.')[0] in lstXmlNoExt]
    # print(lstValidImg)

    #Add suffix to get full path:
    lstXml = [xmlDirSuffix+name for name in lstXml]
    lstValidImg = [imgDirSuffix+img for img in lstValidImg]
    lstRoot = []
    # print(lstXml)
    # print(lstImg)
    # print(lstValidImg)
    for annotation in lstXml:
        root = ET.parse(annotation).getroot()
        lstRoot.append(root)
    lstQuery = list(zip(lstXml, lstValidImg,lstRoot))
    # print(lstObj)

    bar = IncrementalBar('Cropping', max=len(lstQuery))

    for i in range(0, len(lstQuery)):
        # print("Cropping objects from ", lstQuery[i][IMAGE])
        res = cropImg(lstQuery[i], cropDirSuffix)
        if not res:
            print("Error: cropping error!")
            return False
        bar.next()
    bar.finish()
    print("> Auto crop %d images completed!"%(i+1))
    return True
def cropImg(query, cropDirSuffix):
    #Crop image from query (xml, img, root):
    #the results are images of objects contains in xml file.
    xmlFile = query[XML]
    imgFile = query[IMAGE]
    root = query[ROOT]
    im = cv2.imread(imgFile)
    #Now we dont need the full pat anymore:
    imgFile = imgFile.split('/')[-1]
    lstObj = []
    count = 0
    for element in root.iter(OBJECT):
        obj = Object(element)
        # print(obj.name)
        # print((obj.xmin))
        # lstObj.append(obj)
        if not os.path.isdir(cropDirSuffix+obj.name):
            os.mkdir(cropDirSuffix+obj.name)
        cropImgName = imgFile.split('.')[0]+"_"+str(count)+"."+imgFile.split('.')[1]
        cropImgName = cropDirSuffix+obj.name+"/"+cropImgName
        cropImg = im[obj.ymin:obj.ymax, obj.xmin:obj.xmax]
        cv2.imwrite(cropImgName, cropImg)
        # print("Saved ", cropImgName)
        count+=1
        # print(isinstance(obj, ET.Element))
    return True

def checkValid(xmlDir, imgDir):
    lstXml = [xml for xml in os.listdir(xmlDir) if xml.endswith('.xml')]
    lstImg = [img for img in os.listdir(imgDir)
                    if img.endswith('.png')
                    or img.endswith('.jpg')
                    or img.endswith('.jpeg')]
    lstXmlNoExt = [name.strip('.xml') for name in lstXml]
    lstImgNoExt = [name.split('.')[0] for name in lstImg]
    # print(lstXmlNoExt)
    # print(lstImgNoExt)
    #check if there is valid image in corresponding to xml annotations:
    # check = all(annotation in lstImgNoExt for annotation in lstXmlNoExt)
    # if(check == False):
    #     print("Error: ")
    check = True
    for annotation in lstXmlNoExt:
        if not annotation in lstImgNoExt:
            print("> Missing: %s image"%(annotation))
            check = False
    return check
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("XMLAnnotations")
    parser.add_argument("Images")
    parser.add_argument("Cropped")
    args = parser.parse_args()
    
    XMLAnnotations = args.XMLAnnotations
    Images = args.Images
    Cropped = args.Cropped
    res = autoCropImg(XMLAnnotations, Images, Cropped)

    if(res == 'False'):
        print("Error!")
    return res

if __name__ == '__main__':
    main()