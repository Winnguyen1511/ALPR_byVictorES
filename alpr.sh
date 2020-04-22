#!/bin/bash
#*****************************************
# Nguyen Huynh Dang Khoa -Victor Nguyen
# February 2020
# Automatic License Recognition
# Reference: Theophile - Darkflow
# Description: 
#              
#*****************************************  

THIS_DIR=$PWD

RESOURCE_DIR=$THIS_DIR/"resources/"
WORKSPACE=$THIS_DIR/"resources/"
SETUP=$THIS_DIR/"setup"
UTILS_DIR=$THIS_DIR/"utils/"
DATABASE_DIR=$THIS_DIR/"database/"
META_DIR=$DATABASE_DIR"meta/"
PROTOBUF_DIR=$DATABASE_DIR"protobuf/"
MODE="normal"
TESTFILE="_"

META_PLATE=$META_DIR"yolo-plate.meta"
META_CHARACTER=$META_DIR"yolo-character.meta"

PROTOBUF_PLATE=$PROTOBUF_DIR"yolo-plate.pb"
PROTOBUF_CHARACTER=$PROTOBUF_DIR"yolo-character.pb"

CNN=$DATABASE_DIR"character_recognition.h5"

PROG=$THIS_DIR/"prog/platerecognition.py"
RENAME=$UTILS_DIR"rename.py"
TESTMAKER=$UTILS_DIR"testingDataMaker.py"

GPU="0.9"



helpFunction()
{
    echo "Usage: ./alpr "
    echo "Usage: ./alpr -f [full_path_workspace] -g [gpu-usage]"
    echo "Usage: ./alpr --clear"
    echo "Usage: ./alpr --setup"
    echo "Usage: ./alpr --rename"
    echo "Usage: ./alpr --testmaker [test directory]"
    echo "Usage: ./alpr --test [test file]"
}

setupFunction()
{
    echo "setup..."
    if [ ! -d $DATABASE_DIR ]; then
        mkdir $DATABASE_DIR
        mkdir $PROTOBUF_DIR
        mkdir $META_DIR
    else
        rm -rf $DATABASE_DIR
        mkdir $DATABASE_DIR
        mkdir $PROTOBUF_DIR
        mkdir $META_DIR
    fi
    ./setup.sh $PROTOBUF_PLATE $META_PLATE $PROTOBUF_CHARACTER $META_CHARACTER $CNN
}

clearFunction()
{
    echo "Clearing database and credentials..."
    rm -rf $DATABASE_DIR
    rm -rf $SETUP/".credentials"
}
renameFunction()
{
    echo "Rename in ascending order: "
    echo $1
    python3 $RENAME $1
}

testMakerFunction()
{
    echo "TestMaker:"
    python3 $TESTMAKER $1
}

if [ "$1" == "--help" ]; then
    helpFunction
    exit
fi
if [ "$1" == "--setup" ]; then
    setupFunction
    exit
fi

if [ "$1" == "--clear" ]; then
    clearFunction
    exit
fi

if [ "$1" == "--rename" ];then    
    renameFunction $2
    exit
fi

if [ "$1" == "--testmaker" ];then    
    testMakerFunction $2
    exit
fi

if [ "$1" == "--test" ];then 
    MODE="test"
    TESTFILE=$2
fi
while [ -n "$1" ]; do
    case "$1" in
    -f) echo "Changing workspace..."
        if [ "$2" == "" ]; then
            echo "Arguments required"
            helpFunction
            exit
        fi
        WORKSPACE="$2"
        echo "workspace: "$WORKSPACE
        ;;
    -g) echo "Changing gpu usage..."
        if [ "$2" == "" ]; then
            echo "Arguments required"
            helpFunction
            exit
        fi
        GPU="$2"
        echo "Gpu usage: "$GPU
        ;;
    esac
    shift
done


if [ ! -d $DATABASE_DIR ] || [ ! -d $META_DIR ] || [ ! -d $PROTOBUF_DIR ]; then
    echo "Error: Database not found."
    echo "       Please ./alpr --setup to download the database."
    echo "       or create database directory."
    echo "          ├── database/"
    echo "              ├── meta/"
    echo "              └── protobuf/"
    exit
fi

if [ ! -f $CNN ]; then
    echo "Error: Missing file $CNN"
    echo "       Please download $CNN"
    echo "       Or run ./alpr --setup to download."
    exit
fi
if [ ! -f $META_PLATE ] || [ ! -f $PROTOBUF_PLATE ]; then
    echo "Error: Missing file $META_PLATE or $PROTOBUF_PLATE"
    echo "       Please download."
    echo "       Or run ./alpr --setup to download."
    exit
fi
if [ ! -f $META_CHARACTER ] || [ ! -f $PROTOBUF_CHARACTER ]; then
    echo "Error: Missing file $META_CHARACTER or $PROTOBUF_CHARACTER"
    echo "       Please download."
    echo "       Or run ./alpr --setup to download."
    exit
fi

python3 $PROG $WORKSPACE $PROTOBUF_PLATE $META_PLATE $PROTOBUF_CHARACTER $META_CHARACTER $CNN $GPU $MODE $TESTFILE
