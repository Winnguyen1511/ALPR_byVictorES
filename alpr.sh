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

DATABASE_DIR=$THIS_DIR/"database/"
META_DIR=$DATABASE_DIR"meta/"
PROTOBUF_DIR=$DATABASE_DIR"protobuf/"

META_PLATE=$META_DIR"yolo-plate.meta"
META_CHARACTER=$META_DIR"yolo-character.meta"

PROTOBUF_PLATE=$PROTOBUF_DIR"yolo-plate.pb"
PROTOBUF_CHARACTER=$PROTOBUF_DIR"yolo-character.pb"

CNN=$DATABASE_DIR"character_recognition.h5"

PROG=$THIS_DIR/"prog/platerecognition.py"
GPU="0.9"

helpFunction()
{
    echo "Usage: ./alpr "
    echo "Usage: ./alpr -f [full_path_workspace] -g [gpu-usage]"
}

setupFunction()
{
    echo "setup..."
    ./setup.sh
}

if [ "$1" == "--help" ]; then
    helpFunction
    exit
fi
if [ "$1" == "--setup" ]; then
    setupFunction
    exit
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

python3 $PROG $WORKSPACE $PROTOBUF_PLATE $META_PLATE $PROTOBUF_CHARACTER $META_CHARACTER $CNN $GPU
