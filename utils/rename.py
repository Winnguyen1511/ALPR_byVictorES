import os
import argparse


def rename(old_path, new_path):
    pass

def extFilter(filepath):
    filename, ext = os.path.splitext(filepath)
    if ext == '':
        return False
    if ext == '.jpg' or ext == '.jpeg' or '.png' or ext == '.raw':
        # print(filepath)
        return True
    else:
        return False
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    # parser.add_argument("new_path")

    args = parser.parse_args()

    dir = args.directory
    # new_path = args.new_path
    print(">> Rename all file in ", dir)
    # rename(old_path, new_path)
    lst = os.listdir(dir)
    lst  = list(filter(extFilter, lst))
    # print(lst)
    for count, filepath in enumerate(lst):
        _, ext = os.path.splitext(filepath)
        src = dir+'/'+filepath
        dst = dir+'/'+str(count)+ext
        os.rename(src,dst)
    print('>> Rename completed!')
        
main()