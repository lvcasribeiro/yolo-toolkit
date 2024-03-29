# Imports:
from flask import Blueprint, render_template, send_file, request, session

from utils import aws, kml_compiler
from utils.datetime_capture import datetime_capture

import uuid
import threading

# Blueprint constructor:
kml_compiler_bp = Blueprint('kml_compiler_bp', __name__)

# Kml compiler route:
@kml_compiler_bp.route('/kml_compiler', methods=['GET', 'POST'])
def kml_compile():
    return render_template('kml-compiler.html')

# KML compiled route:
@kml_compiler_bp.route('/kml_compiled', methods=['GET', 'POST'])
def kml_compiled():
    try:
        files = request.files.getlist("merge_kml_files")

        current_datetime = datetime_capture()
        session_id = str(uuid.uuid4())
        session['kml_folder_name'] = f'kml-compiler-{current_datetime}-{session_id}'

        aws.create_s3_folder('yolo-toolkit-bucket', session["kml_folder_name"])

        for aux, file in enumerate(files):
            if len(files) > 1:
                if str(file.filename)[-4:] == '.kml':
                    file.filename = f'kml-file-{aux}.kml'
                    aws.upload_file_to_s3(file, 'yolo-toolkit-bucket', f'{session["kml_folder_name"]}/{file.filename}')
                else:
                    aws.delete_s3_folder('yolo-toolkit-bucket', session["kml_folder_name"])
                    return render_template('kml-compiler.html', success_control=False, problem_control='files_extension')
            else:
                aws.delete_s3_folder('yolo-toolkit-bucket', session["kml_folder_name"])
                return render_template('kml-compiler.html', success_control=False, problem_control='files_quantity')

        kml_compiler.concatenate_kml_files(session['kml_folder_name'])

        return render_template('kml-compiler.html', success_control=True, problem_control=None)
    except:
        render_template('error.html')
    finally:
        threading.Timer(300, delete_bucket_folder, args=(session['kml_folder_name'],)).start()

# KML concatenated file download:
@kml_compiler_bp.route('/kml_compiled_download', methods=['GET'])
def kml_compiled_download():
    try:
        kml_folder = session.get("kml_folder_name")
        
        if kml_folder is not None:
            return send_file(
                aws.get_file_object_from_s3('yolo-toolkit-bucket', f'{kml_folder}/compiled-kml.kml'),
                mimetype='application/vnd.google-earth.kml+xml',
                download_name='compiled-kml.kml',
                as_attachment=True
            )
    except:
        render_template('error.html')
    finally:
        threading.Timer(60, delete_bucket_folder, args=(kml_folder,)).start()

# Deletes a folder from the s3 bucket:
def delete_bucket_folder(folder_name):
    aws.delete_s3_folder('yolo-toolkit-bucket', folder_name)
