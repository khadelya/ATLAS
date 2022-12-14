import numpy as np
from sklearn.model_selection import train_test_split
import shutil
import os

PATH_TO_LABELS_TRAIN = "data/labels/train"
PATH_TO_IMAGES_TRAIN = "data/images/train"
PATH_TO_LABELS_VAL = "data/labels/val"
PATH_TO_IMAGES_VAL = "data/images/val"


def files_divider(files):
    files_test, files_val = train_test_split(files, train_size=0.8)
    for file in files:
        if file in files_val:
            source_tif = os.path.join(PATH_TO_IMAGES_TRAIN, file.replace("txt", "tif"))
            source_txt = os.path.join(PATH_TO_LABELS_TRAIN, file)
            destination_tif = os.path.join(
                PATH_TO_IMAGES_VAL, file.replace("txt", "tif")
            )
            destination_txt = os.path.join(PATH_TO_LABELS_VAL, file)
            shutil.move(source_tif, destination_tif)
            shutil.move(source_txt, destination_txt)
    return


def divide_files():
    files = os.listdir(path=PATH_TO_LABELS_TRAIN)
    images_with_objects = []
    background_images = []
    for file in files:
        txt_path = os.path.join(PATH_TO_LABELS_TRAIN, file)
        if os.stat(txt_path).st_size == 0:
            background_images.append(file)
        else:
            images_with_objects.append(file)
    files_divider(images_with_objects)
    files_divider(background_images)


if __name__ == "__main__":
    divide_files()


