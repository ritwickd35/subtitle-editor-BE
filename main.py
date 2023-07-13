from distutils.log import debug
import os
from fileinput import filename
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask import *

app = Flask(__name__)
CORS(app)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # specifies the maximum size of the file to be uploaded in bytes.

# get the absolute path to the working directory in a string
path = os.getcwd()

#  join this absolute path string to the ‘uploads’ string and assign it to the variable UPLOAD_FOLDER
UPLOAD_FOLDER = os.path.join(path, 'uploads')

# check whether the specified path is an existing directory or not.
# If the uploads folder does not exist, a new folder will be made
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# defines path for the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#  set of all the allowed extensions for file upload
ALLOWED_EXTENSIONS = ['mp4', 'vtt', 'srt']


# check whether the file uploaded has the allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    return '<h1>upload server working</h1>'


@app.route('/save-file', methods=['POST'])
def upload_file():
    print('in controller')
    if request.method == 'POST':
        if 'file' not in request.files:
            return {'status': 'failure', 'message': 'no file sent'}, 400
        file = request.files['file']
        if file.filename == '':
            return {'status': 'failure', 'message': 'no file selected for upload'}, 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print('file uploaded successfully')
            return {'status': 'success', 'message': 'file uploaded'}, 200
        else:
            return {'status': 'failure', 'message': 'allowed filetypes are .mp4, .vtt, .srt'}, 400


# if __name__ == '__main__':
# 	app.run(debug=True)
