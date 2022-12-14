from osgeo import gdal
import json
import os

XSIZE = 640
YSIZE = 640

""" Read env variable """
NOTFOUND = "NOTFOUND"
WORKER_CONFIG = os.getenv("WORKER_CONFIG", NOTFOUND)

env_ok = True
if WORKER_CONFIG == NOTFOUND:
    print("WORKER_CONFIG env variable no set")
    env_ok = False

if env_ok:
    """Read config"""
    with open(WORKER_CONFIG, "r") as config_file:
        config_json = json.load(config_file)
        tif_file_path = config_json["parameters"]["resource_tif"]


def tif_to_patches(tif_file_path):
    dir = "data/temp"
    os.mkdir(dir)
    raster = gdal.Open(tif_file_path)
    tif_width = raster.RasterXSize
    tif_height = raster.RasterYSize
    i = 1
    for y in range(0, tif_height, YSIZE):
        for x in range(0, tif_width, XSIZE):
            window = (x, y, XSIZE, YSIZE)
            gdal.Translate(
                f"data/temp/crop_tif_{i}.tif",
                tif_file_path,
                srcWin=window,
            )
            i += 1
    return


if __name__ == "__main__":
    tif_to_patches(tif_file_path)
