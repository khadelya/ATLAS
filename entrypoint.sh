#!/usr/bin/env bash

set -e
set -x

python /usr/src/yolov5/annotations/get_annotation.py
python /usr/src/yolov5/annotations/divider.py
python train.py --img 1280 --batch -1 --epochs 100 --data /input_data/dataset.yml --weights yolov5m6.pt
python /usr/src/yolov5/annotations/tif_to_patches.py
python detect.py --source data/temp --weights runs/train/exp/weights/best.pt --conf-thres 0.25 --name results_detected_exp --imgsz 1280 --save-txt
python /usr/src/yolov5/annotations/results_to_json.py
cp -r runs/ /output_data/
