# YOLOv5 detection and inference on aerial images as a service

Running YOLOv5 training and inference on aerial images (orthophoto) labelled via GeoJSON (in WGS84 Coordinate System) inside of a docker container. 
As a result, you get a trained model and another GeoJSON file containing all the instances found by YOLOv5 (WGS84 Coordinate System).

## Dataset
Tips for best training results according to YOLOv5 [documentation](https://docs.ultralytics.com/tutorials/training-tips-best-results/).

## Input data
Place the following files in the input_data directory :
- *.tif - image (orthophoto) for training and inference containing instances of the object to be detected.
- *_ANNOTATIONS_TRAIN.json - GeoJSON file containing areas in which objects are labelled.
- *_ANNOTATIONS_MANUAL.json - GeoJSON file containing labels of objects to be detected (with Polygons).

Check whether *_ANNOTATIONS_MANUAL.json is tagged with Polygons (otherwise it won't work).

Change dataset.yml (names -> name of the class to be detected), worker-config.json (paths to *.tif and *.json files).


## How to build
Run build script from the root of repository.
```bash
./build.sh
```

If everything is ok, you will see messages like this. 
```
Successfully built d7f06fb2cab3
Successfully tagged adelya/object-detection-worker:2dfbfdd0db44206cea0b588119d58c3d1d5f8d04
Successfully tagged adelya/object-detection-worker:latest
```



To run the image inside of a container :
```bash
./run.sh
```


## Expected results
In the output_data directory should be the following files :
- ANNOTATIONS_GENERATED.json - GeoJSON file containing inference results (detected objects) in WGS84 Coordinate System.
- runs (which contains training results)
