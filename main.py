from distutils.log import debug
import os
from fileinput import filename
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask import *
from webvtt import WebVTT, Caption
import re

app = Flask(__name__)
CORS(app)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # specifies the maximum size of the file to be uploaded in bytes.

#  join this absolute path string to the ‘uploads’ string and assign it to the variable UPLOAD_FOLDER
UPLOAD_FOLDER = os.getcwd() + '/uploads'
print("UPLOAD_FOLDER", UPLOAD_FOLDER)

# check whether the specified path is an existing directory or not.
# If the uploads folder does not exist, a new folder will be made
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# defines path for the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# print("upload folder is ", path, path+(app.config['UPLOAD_FOLDER']))

#  set of all the allowed extensions for file upload
ALLOWED_EXTENSIONS = ['mp4', 'vtt', 'srt']


# check whether the file uploaded has the allowed extension
def allowed_file(file_name):
    return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_webvtt_timestamp(timestamp):
    pattern = r'^\d{2}:\d{2}:\d{2}.\d{3}$'
    return re.match(pattern, timestamp) is not None


@app.route('/')
def main():
    return '<h1>upload server working</h1>'


@app.route('/save-file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return {'status': 'failure', 'message': 'no file sent'}, 400
        file = request.files['file']
        if file.filename == '':
            return {'status': 'failure', 'message': 'no file selected for upload'}, 400
        if file and allowed_file(file.filename):
            file_name = secure_filename(file.filename)
            print(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            print('file uploaded successfully')
            return {'status': 'success', 'message': 'file uploaded'}, 200
        else:
            return {'status': 'failure', 'message': 'allowed filetypes are .mp4, .vtt, .srt'}, 400


@app.route('/display/<file_name>')
def display_video(file_name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], path=file_name, as_attachment=False)


@app.route('/update-caption', methods=['POST'])
def update_caption():
    if request.method == 'POST':
        caption_data = request.json
        file_path = caption_data['fileName']
        caption_start = caption_data['captionStartTime']
        caption_end = caption_data['captionEndTime']
        caption_content = caption_data['captionContent']
        if caption_content == '':
            return {'status': 'failure', 'message': 'no captions sent'}, 400
        elif validate_webvtt_timestamp(caption_start) and validate_webvtt_timestamp(caption_end):
            vtt = WebVTT.read(os.path.join(app.config['UPLOAD_FOLDER'], file_path + '.vtt'))
            caption = Caption(caption_start, caption_end, caption_content)
            vtt.captions.append(caption)
            vtt.save()

            return {'status': 'success', 'message': 'updated caption'}, 200
        else:
            return {'status': 'failure', 'message': 'allowed timestamp format is hh:mm:ss.ttt'}, 400

# if __name__ == '__main__':
# 	app.run(debug=True)
