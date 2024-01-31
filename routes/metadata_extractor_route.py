# Imports:
from flask import Blueprint, render_template, send_file, request, session

from utils import aws, metadata_extractor
from utils.datetime_capture import datetime_capture

import uuid
import threading

# Blueprint constructor:
metadata_extractor_bp = Blueprint('metadata_extractor_bp', __name__)

# Metadata extractor route:
@metadata_extractor_bp.route('/metadata_extractor', methods=['GET', 'POST'])
def metadata_extract():
    return render_template('metadata-extractor.html', success_control=False)

# Metadata extracted route:
@metadata_extractor_bp.route('/metadata_extracted', methods=['GET', 'POST'])
def metadata_extracted():
    try:
        file = request.files.get("extract_metadata")

        current_datetime = datetime_capture()
        session_id = str(uuid.uuid4())
        session['metadata_folder_name'] = f'metadata-extractor-{current_datetime}-{session_id}'

        aws.create_s3_folder('yolo-toolkit-bucket', session["metadata_folder_name"])

        if str(file.filename)[-4:] == '.zip':

            metadata_extractor.create_dataset_folder(session['metadata_folder_name'])
            aws.upload_file_to_s3(file, 'yolo-toolkit-bucket', f'{session["metadata_folder_name"]}/dataset/{file.filename}')

            metadata_extractor.unzip(session['metadata_folder_name'], file.filename)
            data = metadata_extractor.coordinates(session['metadata_folder_name'])
        else:
            aws.delete_s3_folder('yolo-toolkit-bucket', session["metadata_folder_name"])
            return render_template('metadata-extractor.html', success_control='not_a_zip')


        headings = ['Image', 'Time', 'Date', 'Latitude', 'Longitude', 'Altitude', 'Latitude Reference',
                    'Longitude Reference', 'Image Pixel Dimensions', 'Image Real Dimensions', 'Image Area']

        return render_template('metadata-extractor.html', success_control=True, headings=headings, data=data)
    except Exception as e:
        aws.delete_s3_folder('yolo-toolkit-bucket', session['metadata_folder_name'])
        print(e)
        return render_template('error.html')
    finally:
        threading.Timer(300, delete_bucket_folder, args=(session['metadata_folder_name'],)).start()

# Metadata extracted file download:
@metadata_extractor_bp.route('/metadata_extracted_download_excel', methods=['GET'])
def metadata_extracted_download_excel():
    try:
        metadata_folder = session.get("metadata_folder_name")
        
        if metadata_folder is not None:
            return send_file(
                aws.get_file_object_from_s3('yolo-toolkit-bucket', f'{metadata_folder}/images-metadata-excel.xlsx'),
                mimetype='text/csv',
                download_name='images-metadata-excel.xlsx',
                as_attachment=True
            )
    finally:
        threading.Timer(60, delete_bucket_folder, args=(metadata_folder,)).start()

# Metadata kml files download:
@metadata_extractor_bp.route('/metadata_extracted_download_kml', methods=['GET'])
def metadata_extracted_download_kml():
    try:
        metadata_folder = session.get("metadata_folder_name")
        
        if metadata_folder is not None:
            return send_file(
                aws.get_file_object_from_s3('yolo-toolkit-bucket', f'{metadata_folder}/images-metadata-kml.kml'),
                mimetype='application/vnd.google-earth.kml+xml',
                download_name='images-metadata-kml.kml',
                as_attachment=True
            )
    finally:
        threading.Timer(60, delete_bucket_folder, args=(metadata_folder,)).start()

# Deletes a folder from the s3 bucket:
def delete_bucket_folder(folder_name):
    aws.delete_s3_folder('yolo-toolkit-bucket', folder_name)
