# Imports:
import tempfile
import zipfile
import io
import os

import pandas as pypd
import simplekml
import math

from exif import Image

from utils import aws

# Creates dataset folder:
def create_dataset_folder(parent_folder):
    parent_folder_exists = aws.does_s3_folder_exist(
        'yolo-toolkit-bucket', parent_folder)

    if parent_folder_exists:
        aws.create_s3_folder('yolo-toolkit-bucket', f'{parent_folder}/dataset')

# Unzips the files from the .zip file inside the dataset folder:
def unzip(parent_folder, file_name):
    object_key = f'{parent_folder}/dataset/{file_name}'
    response = aws.yolo_bucket.get_object(
        Bucket='yolo-toolkit-bucket', Key=object_key)
    zip_content = response['Body'].read()

    with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_ref:
        files_list = zip_ref.namelist()

        for file in files_list:
            file_content = zip_ref.read(file)
            new_object_key = f'{parent_folder}/dataset/{file}'
            aws.yolo_bucket.put_object(Body=file_content, Bucket='yolo-toolkit-bucket', Key=new_object_key)

# Reads images:
def read_images(parent_folder):
    dataset = aws.list_s3_objects('yolo-toolkit-bucket', parent_folder)
    refined_dataset = []

    for aux in range(len(dataset)):
        if (dataset[aux][-4:] == '.JPG' or dataset[aux][-4:] == '.jpg' or dataset[aux][-4:] == '.PNG' or dataset[aux][-4:] == '.png'):
            refined_dataset.append(dataset[aux])

    return refined_dataset

# Extracts images metadata:
def coordinates(parent_folder):
    image_time = []
    image_date = []
    image_latitude = []
    image_longitude = []
    image_altitude = []
    image_latitude_reference = []
    image_longitude_reference = []
    image_pixel_dimensions = []
    image_real_dimensions = []
    image_area = []
    path_to_image = []

    def image_coordinates(image_data, image_name):        
        image_stream = io.BytesIO(image_data)
        image = Image(image_stream)

        if image.has_exif:
            try:
                image.gps_longitude
                coords = (decimal_coords(image.gps_latitude, image.gps_latitude_ref), decimal_coords(image.gps_longitude, image.gps_longitude_ref))

                altitude = image.gps_altitude - 1172
                horizontal_field_of_view = 87
                vertical_field_of_view = 50

                horizontal_field_of_view = math.radians(horizontal_field_of_view)
                vertical_field_of_view = math.radians(vertical_field_of_view)

                footprint_width = round(2 * altitude * math.tan(horizontal_field_of_view / 2), 2)
                footprint_height = round(2 * altitude * math.tan(vertical_field_of_view / 2), 2)

                image_time.append(image.datetime_original[11:19])
                image_date.append(image.datetime_original[:10])
                image_latitude.append(coords[0])
                image_longitude.append(coords[1])
                image_altitude.append(f'{round(image.gps_altitude - 1172, 2)} m')
                image_latitude_reference.append(image.gps_latitude_ref)
                image_longitude_reference.append(image.gps_longitude_ref)
                image_pixel_dimensions.append(f'{image.pixel_x_dimension} x {image.pixel_y_dimension} pixels')
                image_real_dimensions.append(f'{footprint_width} x {footprint_height} m')
                image_area.append(f'{round(footprint_width*footprint_height, 2)} m²')
                path_to_image.append(image_name)

            except AttributeError:
                pass

    dataset = read_images(parent_folder)

    for aux in range(len(dataset)):
        if (dataset[aux][-4:] == '.JPG' or dataset[aux][-4:] == '.jpg' or dataset[aux][-4:] == '.PNG' or dataset[aux][-4:] == '.png'):
            image_data = aws.yolo_bucket.get_object(Bucket='yolo-toolkit-bucket', Key=dataset[aux])['Body'].read()
            image_coordinates(image_data, dataset[aux].split('/')[-1])

    images_info_dataframe = pypd.DataFrame(list(zip(path_to_image, image_time, image_date, image_latitude, image_longitude, image_altitude, image_latitude_reference, image_longitude_reference, image_pixel_dimensions, image_real_dimensions, image_area)), columns=[
                                           'Image', 'Time', 'Date', 'Latitude', 'Longitude', 'Altitude', 'Latitude Reference', 'Longitude Reference', 'Image Pixel Dimensions', 'Image Real Dimensions', 'Image Area'])
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:
        images_info_dataframe.to_excel(temp_excel.name, index=False)

    excel_key = f'{parent_folder}/images-metadata-excel.xlsx'
    with open(temp_excel.name, 'rb') as excel_file:
        aws.yolo_bucket.put_object(Bucket='yolo-toolkit-bucket', Key=excel_key, Body=excel_file.read())

    kml = simplekml.Kml()
    for index, row in images_info_dataframe.iterrows():
        if 'Latitude' in row and 'Longitude' in row:
            lat = row['Latitude']
            lon = row['Longitude']
            placemark = kml.newpoint(name=row['Image'], coords=[(lon, lat)])
            placemark.description = row.get('description', '')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.kml') as temp_kml:
        kml.save(temp_kml.name)

    kml_key = f'{parent_folder}/images-metadata-kml.kml'
    with open(temp_kml.name, 'rb') as kml_file:
        aws.yolo_bucket.put_object(Bucket='yolo-toolkit-bucket', Key=kml_key, Body=kml_file.read())
    
    data = []

    for row in range(0, len(images_info_dataframe)):
        data.append((path_to_image[row], image_time[row], image_date[row], image_latitude[row], image_longitude[row], image_altitude[row],
                    image_latitude_reference[row], image_longitude_reference[row], image_pixel_dimensions[row], image_real_dimensions[row], image_area[row]))
    
    os.remove(temp_excel.name)
    os.remove(temp_kml.name)

    return data

# Converts the coord to decimal coords:
def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1]/60 + coords[2]/3600

    if ref == 'S' or ref == 'W':
        decimal_degrees = -decimal_degrees

    return decimal_degrees
