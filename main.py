from distutils.log import debug
import os
from fileinput import filename
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from flask import *
from webvtt import WebVTT, Caption
import re

app = Flask(__name__)
CORS(app)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # specifies the maximum size of the file to be uploaded in bytes.

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
ALLOWED_EXTENSIONS = ['mp4', 'vtt']


# check whether the file uploaded has the allowed extension
def allowed_file(file_name):
    return '.' in file_name and file_name.rsplit('.', 1)[1].casefold() in ALLOWED_EXTENSIONS


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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            return {'status': 'success', 'message': 'file uploaded'}, 200
        else:
            return {'status': 'failure', 'message': 'allowed filetypes are .mp4, .vtt, .srt'}, 400


@app.route('/display/<file_name>')
def display_file(file_name):
    if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], file_name)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], path=file_name, as_attachment=False)
    else:
        return {'status': 'failure', 'message': 'file not found'}, 404


@cross_origin()
@app.route('/insert-caption', methods=['PUT'])
def update_caption():
    if request.method == 'PUT':
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


@app.route('/create-subtitle', methods=['POST'])
def create_subtitle_file():
    if request.method == 'POST':
        print("got request in create subtitle")
        file_data = request.json
        file_path = file_data['fileName']
        f = None
        try:
            f = open(os.path.join(app.config['UPLOAD_FOLDER'], file_path + '.vtt'), "x")
        except Exception as e:
            return {'status': 'failure', 'message': 'subtitle file already present'}, 400
        finally:
            f.write("WEBVTT\n\n")
            return {'status': 'success', 'message': 'created new subtitle file'}, 200


@app.route('/delete-caption', methods=['POST'])
def delete_subtitle():
    if request.method == 'POST':
        print("got request in delete subtitle")
        caption_data = request.json
        file_path = caption_data['fileName']
        start_time = caption_data['startTime']
        end_time = caption_data['endTime']
        caption_content = caption_data['content']
        vtt = WebVTT.read(os.path.join(app.config['UPLOAD_FOLDER'], file_path + '.vtt'))
        del_index = -1
        index = 0
        for caption in vtt:
            if caption.start == start_time and caption.end == end_time and caption.text == caption_content:
                del_index = index
            index += 1

        print("indedx", del_index)
        if del_index != -1:
            try:
                del vtt.captions[del_index]
                vtt.save()
                return {'status': 'success', 'message': 'selected subtitle deleted'}, 200
            except Exception as e:
                return {'status': 'failure', 'message': 'could not delete subtitle'}, 400
        return {'status': 'failure', 'message': 'could not find subtitle to delete'}, 400


@app.route('/update-caption', methods=['POST'])
def update_subtitle():
    if request.method == 'POST':
        print("got request in delete subtitle")
        caption_data = request.json
        file_path = caption_data['fileName']
        start_time = caption_data['startTime']
        end_time = caption_data['endTime']
        caption_content = caption_data['content']
        vtt = WebVTT.read(os.path.join(app.config['UPLOAD_FOLDER'], file_path + '.vtt'))
        update_index = -1
        index = 0
        for caption in vtt:
            if caption.start == start_time and caption.end == end_time and caption.text == caption_content:
                update_index = index
            index += 1

        print("indedx", update_index)
        if update_index != -1:
            try:
                vtt[update_index].text = caption_content
                vtt.save()
                return {'status': 'success', 'message': 'selected subtitle updated'}, 200
            except Exception as e:
                return {'status': 'failure', 'message': 'could not update subtitle'}, 400
        return {'status': 'failure',
                'message': 'could not find subtitle to update'}, 400  # if __name__ == '__main__':  # 	app.run(debug=True)
