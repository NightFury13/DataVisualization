
# A very simple Flask Hello World app for you to get started with...

from flask import Flask
import os
from flask import request, redirect, url_for, send_from_directory
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
    return '''
    <!doctype html>
    <head>
    <title>Dummy Graph</title>
        <link href="static/c3/c3.css" rel="stylesheet" type="text/css">
        <script src="static/c3/d3/d3.min.js" charset="utf-8"></script>
        <script src="static/c3/c3.min.js"></script>
    </head>
    <body>
        <h1>Dummy Graph in C3.js</h1>
        <div id="chart"></div>
        <script>
            var chart = c3.generate({
                bindto: '#chart',
                data: {
                  columns: [
                    ['data1', 30, 200, 100, 400, 150, 250],
                    ['data2', 50, 20, 10, 40, 15, 25]
                  ]
                }
            });
        </script>
        <p>Hurray! It works!</p>
    </body>
    '''