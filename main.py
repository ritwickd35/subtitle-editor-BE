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


# check whether the specified path is an existing directory or not.
# If the uploads folder does not exist, a new folder will be made
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


# defines path for the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#  set of all the allowed extensions for file upload
ALLOWED_EXTENSIONS = ['mp4', 'vtt']


# check whether the file uploaded has the allowed extension
def allowed_file(file_name):
    return '.' in file_name and file_name.rsplit('.', 1)[1].casefold() in ALLOWED_EXTENSIONS


# validates a webVTT timestamp in the format hh:mm:ss.ttt
def validate_webvtt_timestamp(timestamp):
    pattern = r'^\d{2}:\d{2}:\d{2}.\d{3}$'
    return re.match(pattern, timestamp) is not None



'''
Test route to check if the server is working
'''
@app.route('/')
def main():
    return '<h1>upload server working</h1>'



'''
Route: /save-file
Method: POST
Description: Uploads a file to the server.
Request Parameters: None
'''
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



'''
Route: /display/<file_name>
Method: GET
Description: Displays a file stored on the server.
Request Parameters:
    file_name (string): The name of the file to be displayed.
'''
@app.route('/display/<file_name>')
def display_file(file_name):
    if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], file_name)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], path=file_name, as_attachment=False)
    else:
        return {'status': 'failure', 'message': 'file not found'}, 404



'''
Route: /insert-caption
Method: PUT
Description: Inserts a caption into a WebVTT subtitle file.
Request Parameters: None
Request Body:
    fileName (string): The name of the WebVTT subtitle file.
    captionStartTime (string): The start time of the caption (in the format hh:mm:ss.ttt).
    captionEndTime (string): The end time of the caption (in the format hh:mm:ss.ttt).
    captionContent (string): The content of the caption.
'''
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



'''
Route: /create-subtitle
Method: POST
Description: Creates a new WebVTT subtitle file for the specified video name.
Request Parameters: None
Request Body:
    fileName (string): The name of the subtitle file.
'''
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


'''
Route: /delete-caption
Method: POST
Description: Deletes a specific caption from a WebVTT subtitle file.
Request Parameters: None
Request Body:
    fileName (string): The name of the WebVTT subtitle file.
    startTime (string): The start time of the caption to be deleted (in the format hh:mm:ss.ttt).
    endTime (string): The end time of the caption to be deleted (in the format hh:mm:ss.ttt).
    content (string): The content of the caption to be deleted.
'''
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

        if del_index != -1:
            try:
                del vtt.captions[del_index]
                vtt.save()  # saving the file

                return {'status': 'success', 'message': 'selected subtitle deleted'}, 200
            except Exception as e:
                return {'status': 'failure', 'message': 'could not delete subtitle'}, 400
        return {'status': 'failure', 'message': 'could not find subtitle to delete'}, 400


'''
Route: /update-caption
Method: POST
Description: Updates the content of a specific caption in a WebVTT subtitle file.
Request Parameters: None
Request Body:

    fileName (string): The name of the WebVTT subtitle file.
    startTime (string): The start time of the caption to be updated (in the format hh:mm:ss.ttt).
    endTime (string): The end time of the caption to be updated (in the format hh:mm:ss.ttt).
    content (string): The updated content of the caption.
'''
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
                'message': 'could not find subtitle to update'}, 400  
    
    
# if __name__ == '__main__':  # 	app.run(debug=True)
