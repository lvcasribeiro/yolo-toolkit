# Imports:
import xml.etree.ElementTree as ET
import tempfile
import os

from utils import aws

# Concatenates kml files:
def concatenate_kml_files(folder_name):
    kml_root = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    document = ET.SubElement(kml_root, "Document")

    for kml_file_key in aws.list_s3_objects('yolo-toolkit-bucket', folder_name):
        
        if kml_file_key[-4:] == '.kml':
            kml_file = aws.yolo_bucket.get_object(Bucket='yolo-toolkit-bucket', Key=kml_file_key)['Body'].read().decode('utf-8')
            
            if kml_file:
                root = ET.fromstring(kml_file)

                for element in root.iter():
                    document.append(element)

    concatenated_kml_tree = ET.ElementTree(kml_root)

    with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as kml_temp_file:
        kml_temp_file.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        concatenated_kml_tree.write(kml_temp_file, encoding="utf-8")

    try:
        aws.yolo_bucket.put_object(Bucket='yolo-toolkit-bucket', Key=f'{folder_name}/compiled-kml.kml', Body=open(kml_temp_file.name, 'rb'), ContentType='application/vnd.google-earth.kml+xml')
    finally:
        os.remove(kml_temp_file.name)
