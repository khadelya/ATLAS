#!/usr/bin/env bash

set -e
set -x

python /usr/src/yolov5/annotations/get_annotation.py
python /usr/src/yolov5/annotations/divider.py
python train.py --data /input_data/dataset.yml --weights yolov5s.pt
python /usr/src/yolov5/annotations/tif_to_patches.py
python detect.py --source data/temp --weights runs/train/exp/weights/best.pt --conf 0.4 --name results_detected_exp --save-txt
python /usr/src/yolov5/annotations/results_to_json.py
cp -r runs/ /output_data/
