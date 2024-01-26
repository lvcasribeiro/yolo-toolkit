# Imports:
from flask import Flask, render_template, send_file, request, session

from utils import aws, kml_compiler
from utils.datetime_capture import datetime_capture

import os
import uuid
import threading

# Flask constructor:
app = Flask(__name__)
app.secret_key = 'lvc4s'

# Home route:
@app.route('/')
def home():
    return render_template('index.html')

# KML compiler route:
@app.route('/kml_compiler', methods=['GET', 'POST'])
def kml_compile():
    return render_template('kml-compiler.html', result_file=False)


# KML compiled route:
@app.route('/kml_compiled', methods=['GET', 'POST'])
def kml_compiled():
    try:
        files = request.files.getlist("merge_kml_files")

        current_datetime = datetime_capture()
        session_id = str(uuid.uuid4())
        session['kml_folder_name'] = f'kml-compiler-{current_datetime}-{session_id}'

        aws.create_s3_folder('yolo-toolkit-bucket', session["kml_folder_name"])

        for aux, file in enumerate(files):
            if str(file.filename)[-4:] == '.kml':
                file.filename = f'kml-file-{aux}.kml'
            else:
                pass

        for file in files:
            if len(files) > 1:
                if str(file.filename)[-4:] == '.kml':
                    aws.upload_file_to_s3(file, 'yolo-toolkit-bucket', f'{session["kml_folder_name"]}/{file.filename}')
                else:
                    aws.delete_s3_folder('yolo-toolkit-bucket', session["kml_folder_name"])
                    return render_template('kml-compiler.html', result_file='not_a_zip')
            else:
                aws.delete_s3_folder('yolo-toolkit-bucket', session["kml_folder_name"])
                return render_template('kml-compiler.html', result_file='not_a_zip')

        kml_compiler.concatenate_kml_files(session['kml_folder_name'])

        return render_template('kml-compiler.html', result_file=True)
    except:
        pass
    finally:
        threading.Timer(300, delete_kml_compiler_folder, args=(session['kml_folder_name'],)).start()

# KML concatenated file download:
@app.route('/kml_compiled_download', methods=['GET'])
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
        pass
    finally:
        threading.Timer(60, delete_kml_compiler_folder, args=(kml_folder,)).start()

# Delets kml folder:
def delete_kml_compiler_folder(kml_folder):
    aws.delete_s3_folder('yolo-toolkit-bucket', kml_folder)

# Overall execution:
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
