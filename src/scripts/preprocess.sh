#!/bin/bash

# Customize Stage DIR
STAGE_DIR=/tmp
#mkdir -p $STAGE_DIR

# Download the dataset
if [ "$Dataset_Name" == "coco" ]; then
    echo "Downloading coco dataset"
    mkdir -p $STAGE_DIR/coco
    wget -O $STAGE_DIR/coco/train2017.zip http://images.cocodataset.org/zips/train2017.zip
    unzip $STAGE_DIR/coco/train2017.zip  -d $STAGE_DIR/coco/images
    rm $STAGE_DIR/coco/train2017.zip

    wget -O $STAGE_DIR/coco/val2017.zip http://images.cocodataset.org/zips/val2017.zip
    unzip $STAGE_DIR/coco/val2017.zip -d $STAGE_DIR/coco/images
    rm $STAGE_DIR/coco/val2017.zip

    wget -O $STAGE_DIR/coco/annotations_trainval2017.zip http://images.cocodataset.org/annotations/annotations_trainval2017.zip
    unzip $STAGE_DIR/coco/annotations_trainval2017.zip -d $STAGE_DIR/coco
    rm $STAGE_DIR/coco/annotations_trainval2017.zip

    aws s3 cp --recursive $STAGE_DIR/coco s3://$Experiment_Bucket/$Experiment_Prefix/training_data

    # cd $STAGE_DIR
    # wget -O ./model.h5 https://github.com/fizyr/keras-retinanet/releases/download/0.5.1/resnet50_coco_best_v2.1.0.h5
    # tar cvfz ./model.tar.gz ./model.h5
    # aws s3 cp ./model.tar.gz s3://$Experiment_Bucket/$Experiment_Prefix/pre-trained_model/model.tar.gz

elif [ "$Dataset_Name" == "fashion" ]; then
    echo "Downloading Fashion-MNIST dataset"
    mkdir -p $STAGE_DIR/fashion
    wget -O $STAGE_DIR/fashion/train-images-idx3-ubyte.gz http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-images-idx3-ubyte.gz
    wget -O $STAGE_DIR/fashion/train-labels-idx1-ubyte.gz http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-labels-idx1-ubyte.gz
    wget -O $STAGE_DIR/fashion/t10k-images-idx3-ubyte.gz http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-images-idx3-ubyte.gz
    wget -O $STAGE_DIR/fashion/t10k-labels-idx1-ubyte.gz http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-labels-idx1-ubyte.gz

    aws s3 cp --recursive $STAGE_DIR/fashion s3://$Experiment_Bucket/$Experiment_Prefix/training_data

else
    echo "Dataset_Name doesn't exist... Exiting"
    exit 1
fi