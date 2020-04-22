import cv2
import os
import argparse
import threading
import math
MIN_WIDTH = 300
MIN_HEIGHT = 80

MAX_WIDTH = 600
MAX_HEIGHT = 160
defaultdatafile = 'data'
#listData: all image name in here:
listData = []
#testData: all tmp test data to write to data file
testData = {}
abort = False
manual = False
def extFilter(filepath):
    filename, ext = os.path.splitext(filepath)
    if ext == '':
        return False
    if ext == '.jpg' or ext == '.jpeg' or '.png' or ext == '.raw':
        # print(filepath)
        return True
    else:
        return False

def cmp_items(a):
    return int(a.split('.')[0])
def imshow(filename, im):
    imsize = im.shape
    w = imsize[1]
    h = imsize[0]

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
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_CUBIC)
    cv2.namedWindow(filename, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(filename,im)
    cv2.waitKey(0)



def testDataReader(directory):
    global defaultdatafile
    print(">> READ TEST DATA ( Chon file data )")
    datafile = input("> Input file (-1 to cancel, [blank] to choose default): ")
    if(datafile == ''):
        datafile = defaultdatafile
    if(datafile =='-1'):
        return False
    print("> Reading the directory: ", directory)
    os.chdir(directory) 
    if(os.path.exists(datafile) == False):
        file = open(datafile, "w")
        file.close()
    file = open(datafile, "r")
    line = file.readline()
    #Reading the test data file:
    while line and line != "\n":
        # print(line)
        entry = line.split(" ")
        if(os.path.isfile(entry[0]) == True):
            testData.update({entry[0]: entry[1].strip('\n')})
        line = file.readline()
    # print(testData)
    file.close()

    #read file name in directory:
    global listData
    listData = os.listdir()
    listData = list(filter(extFilter, listData))
    #Sort the list here:
    listData = sorted(listData, key=cmp_items)

    print("> Reading completed with %d images, already %d entries"%(len(listData), len(testData)))
    print('.')
    return True
    


def testDataMaker():
    global abort
    global manual
    print(">> DATA MAKER ( Danh data )")
    print("> Please choose working mode:")
    print("> ( -1: exit; 0:save; 1: auto; 2: semi;  3: manual)")
    choice = input("> Choice: ")
    # choice = int(choice)
    while(choice == ''):
        choice = input("> Choice: ")
    if(choice == '0'):
        res = True
        manual = False
    elif(choice == '-1'):
        print("> Abort test data maker...")
        abort = True
        res = False
    else:
        if choice == '1':
            res = autoMode()
        elif choice == '2':
            res = semiMode()
        elif choice == '3':
            res = manualMode()
        else:
            res = True
            abort = True
            print("> Error wrong choice, please run again!")
    print('.')
    return res

def autoMode():
    print("---------------------------------------------------")
    print(">> AUTO MODE ( Danh data tu begin -> end )")
    
    # print(listData)
    # print(testData)
    for i in range(0, len(listData)):
        filename = listData[i]
        # print(filename)
        im = cv2.imread(filename)
        t = threading.Thread(target=imshow, args=(filename, im))
        t.start()
        print("> File: ", listData[i])
        num = input("> Plate(-1 to stop): ")
        while(num == ''):
            num = input("> Plate(-1 to stop): ")
        if num == '-1': 
            break
        else:
            tmp = {listData[i] : num}
            testData.update(tmp)
            print("---------------------------------------------------")
        cv2.destroyWindow(filename)
        # print(t.isAlive())
    cv2.destroyAllWindows()
    # print(testData)
    
    return True

def semiMode():
    global abort
    print("---------------------------------------------------")
    print(">> SEMI MODE ( Danh data tu 1 diem bat ki )")
    
    line = input("> Choose the start point (-1 to exit): ")
    while(line == ''):
        line = input("> Choose the start point (-1 to exit): ")
    
    if(line == '-1'):
        abort = True
        return True
    else:
        if(line not in listData):
            print("> Error: no such file in directory!")
            abort = True
            return True
        else:

            #Start to make data from file:
            for i in range(listData.index(line), len(listData)):
                filename = listData[i]
                # print(filename)
                im = cv2.imread(filename)
                t = threading.Thread(target=imshow, args=(filename, im))
                t.start()
                print("> File: ", listData[i])
                num = input("> Plate(-1 to stop): ")
                while(num == ''):
                    num = input("> Plate(-1 to stop): ")
                if num == '-1': 
                    break
                else:
                    tmp = {listData[i] : num}
                    testData.update(tmp)
                    print("---------------------------------------------------")
                cv2.destroyWindow(filename)
            cv2.destroyAllWindows()
   
    return True


def manualMode():
    global abort
    global manual
    print("---------------------------------------------------")
    print(">> MANUAL MODE ( Danh data cho 1 anh duy nhat )")
    line = input("> Choose image (-1 to exit): ")
    while(line == ''):
        line = input("> Choose image (-1 to exit): ")

    if(line == '-1'):
        abort = True
        return True
    else:
        if(line not in listData):
            print("> Error: no such file in directory!")
            abort = True
            return True
        else:
            filename = line
            # print(filename)
            im = cv2.imread(filename)
            t = threading.Thread(target=imshow, args=(filename, im))
            t.start()
            print("> File: ", line)
            num = input("> Plate(-1 to stop): ")
            while(num == ''):
                num = input("> Plate(-1 to stop): ")
            if num != '-1':
                tmp = {line : num}
                testData.update(tmp)
                print("---------------------------------------------------")
            cv2.destroyWindow(filename)
            manual = True
    return True
def updateTestData():
    print(">> UPDATE DATA")
    print("> Already have %d data in test list!"%(len(testData)))
    savefile = input("> Save file (-1 or [blank] to save as tmp): ")
    if(savefile == '-1'):
        return
    if(savefile == ''):
        savefile = 'tmp'
    file = open(savefile, "w")
    for key in testData.keys():
        # print(key)
        # print(testData[key])
        file.write(key+" "+testData[key]+"\n")
    file.close()

def main():
    global abort
    global manual
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args()

    dir = args.directory

    if(testDataReader(dir) == False):
        print(">> Exit!")
        return
    while(True):
        res = testDataMaker()
        if res == True:
            if(abort == False):
                if(manual == False):
                    updateTestData()
            abort = False
            manual = False
            print(">> Test data making completed!")
            print("---------------------------------------------------")
        else:
            break
            print(">> Data is not saved!")
    print(">> Exit!")
    
    
main()

