from geojson import Feature, Polygon, FeatureCollection
from pyproj import Transformer, pyproj
from osgeo import gdal, osr
import geojson
import json
import os

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
        json_file_path_train = config_json["parameters"]["annotations_train"]
        json_file_path_manual = config_json["parameters"]["annotations_manual"]


def circle_to_polygon(json_file_path):
    features_new = []
    with open(json_file_path, "r+") as f:
        data = json.load(f)
        features = data["features"]
        for feature in features:
            if feature["geometry"]["type"] == "Point":
                radius = feature["properties"]["radius"]
                coordinates = feature["geometry"]["coordinates"]
                xmin, ymin = list(map(lambda x: x - radius, coordinates))
                xmax, ymax = list(map(lambda x: x + radius, coordinates))
                feature = Feature(
                    geometry=Polygon(
                        [
                            [
                                (xmin, ymin),
                                (xmin, ymax),
                                (xmax, ymax),
                                (xmax, ymin),
                                (xmin, ymin),
                            ]
                        ]
                    )
                )
            features_new.append(feature)

    feature_collection = FeatureCollection(features_new)

    with open(
        json_file_path.replace(".json", "_polygon.json"), "w", encoding="utf-8"
    ) as f:
        geojson.dump(feature_collection, f, ensure_ascii=False, indent=2)
    return


def json_to_new_coordinates(tif_file_path, json_file_path):
    ds = gdal.Open(tif_file_path)
    prj = ds.GetProjection()
    src = osr.SpatialReference(wkt=prj)
    src_epsg = int(src.GetAuthorityCode(None))  # src - .tif file
    JSON_EPSG = 4326  # EPSG WGS 84 of json file
    transformer = Transformer.from_crs(JSON_EPSG, src_epsg)

    with open(json_file_path, "r+") as f:
        data = json.load(f)
        features = data["features"]
        for feature in features:
            coordinates = feature["geometry"]["coordinates"][0]
            for coordinate in coordinates:
                latitude, longitude = coordinate
                coordinate[1], coordinate[0] = transformer.transform(
                    longitude, latitude
                )

    with open(
        json_file_path.replace(".json", "_new_coord.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return


def crop_tif(tif_file_path, json_file_path):
    with open(json_file_path.replace(".json", "_new_coord.json"), "r") as f:
        train = json.load(f)
        features = train["features"]
        for count, feature in enumerate(features):
            xmin = feature["geometry"]["coordinates"][0][0][0]
            ymin = feature["geometry"]["coordinates"][0][0][1]
            xmax = feature["geometry"]["coordinates"][0][2][0]
            ymax = feature["geometry"]["coordinates"][0][1][1]
            window = (xmin, ymax, xmax, ymin)
            gdal.Translate(
                f"data/images/train/output_crop_raster_{count}.tif",
                tif_file_path,
                projWin=window,
                noData=0,
            )
    return


def get_box_coordinates(feature):
    x_list = []
    y_list = []
    coordinates = feature["geometry"]["coordinates"][0]
    for coordinate in coordinates:
        x_list.append(coordinate[0])
        y_list.append(coordinate[1])

    xmin = min(x_list)
    ymax = max(y_list)
    xmax = max(x_list)
    ymin = min(y_list)

    box_coordinates = [xmin, ymax, xmax, ymin]
    return box_coordinates


# features[0]["geometry"]["coordinates"][0][0][0]


def get_pixel_values(box_coordinates, upper_left, px_size):
    xmin_px = round(
        (box_coordinates[0] - upper_left[0]) / px_size[0]
    )  # round((x_coord - upper_left_x) / px_size_x)
    ymin_px = round(
        (upper_left[1] - box_coordinates[1]) / px_size[1]
    )  # round((upper_left_y - y_coord) / px_size_y)
    xmax_px = round((box_coordinates[2] - upper_left[0]) / px_size[0])
    ymax_px = round((upper_left[1] - box_coordinates[3]) / px_size[1])
    return [xmin_px, ymin_px, xmax_px, ymax_px]


def convert(size, box):
    width_norm = 1.0 / size[0]
    height_norm = 1.0 / size[1]
    x_center = (box[0] + box[2]) * width_norm / 2
    y_center = (box[1] + box[3]) * height_norm / 2
    width = (box[2] - box[0]) * width_norm
    height = (box[3] - box[1]) * height_norm
    return (x_center, y_center, width, height)


def convert_annotation(tif_file_path, json_file_path_train, json_file_path_manual):
    # crop tif file
    json_to_new_coordinates(tif_file_path, json_file_path_train)
    with open(json_file_path_train.replace(".json", "_new_coord.json"), "r") as f:
        train = json.load(f)
        features_train = train["features"]
    num_of_files = len(features_train)
    crop_tif(tif_file_path, json_file_path_train)

    circle_to_polygon(json_file_path_manual)
    json_to_new_coordinates(tif_file_path, json_file_path_manual)

    with open(json_file_path_manual.replace(".json", "_new_coord.json"), "r") as f:
        data = json.load(f)
        features = data["features"]
    for i in range(num_of_files):
        raster = gdal.Open(f"data/images/train/output_crop_raster_{i}.tif")
        gt = raster.GetGeoTransform()
        px_size_x = gt[1]
        px_size_y = -gt[5]
        width = raster.RasterXSize
        height = raster.RasterYSize
        upper_left_x = gt[0]  # xmin
        upper_left_y = gt[3]  # ymax
        lower_right_x = gt[0] + width * gt[1] + height * gt[2]  # xmax
        lower_right_y = gt[3] + width * gt[4] + height * gt[5]  # ymin

        with open(f"data/labels/train/output_crop_raster_{i}.txt", "w") as txt:
            for feature in features:
                sum = 0
                coordinates = feature["geometry"]["coordinates"][0]
                for coordinate in coordinates:
                    if (upper_left_x <= coordinate[0] <= lower_right_x) & (
                        lower_right_y <= coordinate[1] <= upper_left_y
                    ):
                        sum += 1

                if sum == len(coordinates):
                    box_coordinates = get_box_coordinates(feature)
                    class_id = 0
                    box = get_pixel_values(
                        box_coordinates,
                        (upper_left_x, upper_left_y),
                        (px_size_x, px_size_y),
                    )
                    bounding_box = convert((width, height), box)
                    txt.write(
                        str(class_id)
                        + " "
                        + " ".join(
                            [str(bbox_coordinate) for bbox_coordinate in bounding_box]
                        )
                        + "\n"
                    )


if __name__ == "__main__":
    convert_annotation(tif_file_path, json_file_path_train, json_file_path_manual)
