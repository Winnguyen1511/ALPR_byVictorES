import xml.etree.ElementTree as ET
import os
import cv2
import argparse
from progress.bar import IncrementalBar

OBJECT='object'
BNDBOX='bndbox'
NAME='name'
XMIN ='xmin'; YMIN ='ymin'; XMAX ='xmax'; YMAX = 'ymax'
XML=0; TREE=1; ROOT=2
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

def autoChangeLabel(xmlDir, newXmlDir, newLabel):
    global lstQuery
    if xmlDir == '.':
        xmlDirSuffix = ""
    else:
        if not xmlDir.endswith('/'):
            xmlDirSuffix = xmlDir+"/"
        else:
            xmlDirSuffix = xmlDir
    
    if newXmlDir == '.':
        newXmlDirSuffix = ""
    else:
        if not newXmlDir.endswith('/'):
            newXmlDirSuffix = newXmlDir+"/"
        else:
            newXmlDirSuffix = newXmlDir
    lstXml = [xml for xml in os.listdir(xmlDir) if xml.endswith('.xml')]
    lstXml = [xmlDirSuffix+name for name in lstXml]
    lstRoot = []
    lstTree = []
    for annotation in lstXml:
        tree = ET.parse(annotation)
        lstTree.append(tree)
        root = tree.getroot()
        lstRoot.append(root)
    lstQuery = list(zip(lstXml, lstTree, lstRoot))
    bar = IncrementalBar('Cropping', max=len(lstQuery))

    for i in range(0, len(lstQuery)):
        res = changeLabel(lstQuery[i], newXmlDirSuffix, newLabel)
        if not res:
            print("Error: Change label failed!")
            return False
        bar.next()
    bar.finish()
    print("> Auto Change label %d xml files completed!"%(i+1))
    return True

def changeLabel(query, newXmlDirSuffix, newLabel):
    xmlFile = query[XML]
    xmlFile =xmlFile.split('/')[-1]
    tree = query[TREE]
    root = query[ROOT]
    lstObj = []
    if not os.path.isdir(newXmlDirSuffix):
        os.mkdir(newXmlDirSuffix)
    newXmlName = newXmlDirSuffix+"/"+xmlFile
    for element in root.iter(OBJECT):
        element.find(NAME).text = newLabel
    tree.write(newXmlName)
    return True

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("XMLAnnotations")
    parser.add_argument("ChangeLabelDir")
    parser.add_argument("new_label")
    args = parser.parse_args()
    XMLAnnotations = args.XMLAnnotations
    ChangeLabelDir = args.ChangeLabelDir
    new_label = args.new_label

    res = autoChangeLabel(XMLAnnotations, ChangeLabelDir, new_label)
    if(res == 'False'):
        print("Error!")
    return res

if __name__ == "__main__":
    main()