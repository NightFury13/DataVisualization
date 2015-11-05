
# A very simple Flask Hello World app for you to get started with...

from flask import Flask
import os
from flask import request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename

UPLOAD_FOLDER = '/home/NightFury13/CloudComputing/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def hello_world():
    return '''
    <!doctype html>
    <title>Landing Page</title>
    <h1>Cloud Project : Data visualization</h1>
    <p>Currently the different blocks in place are :</p>
    <ul>
        <li> '/upload' : File upload [txt/csv]</li>
        <li> '/uploads' : redirected from /upload, shows file contents</li>
        <li> '/dummy' : a dummy graph built on c3.js</li>
    </ul>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    file_content = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return file_content

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/dummy')
def dummy_graph():
    return render_template('dummy.html')


if __name__ == '__main__':
    app.run()
