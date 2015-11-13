#########################################
# Controller functions for Chartify(TM) #
#                                       #
# @Authors : Mohit Jain                 #
#          : Prithvi Deep Chawla        #
#          : Sambuddha Basu             #
#          : Saurabh Dhanotia           #
#########################################

from flask import Flask
import os
import sys
import json
import yaml
import logging
import json, ast
from logging.handlers import RotatingFileHandler
import pymongo
from pymongo import MongoClient
from flask import request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename

#UPLOAD_FOLDER = '/home/NightFury13/CloudComputing/uploads'
UPLOAD_FOLDER='/home/sourabh/Semester 3/Cloud Computing/Major/DataVisualization/CloudComputing/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv' , 'json'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def landing():
    """
    Landing page for the website.
    """
    return render_template('landing.html')

@app.route('/show/<filename>')
def uploaded_file(filename):
    """
    Handles the conversion of uploaded meta-data files for automated graph generation.
    """
    app.logger.info('in uploaded file')

    if check_file(filename,'csv'):
        file_content = parse_csv(filename)        
        file_content=push_to_mongo(file_content)                        
        jsonobj=json.dumps(file_content)
        file_content=yaml.safe_load(jsonobj)
        #del jsonobj['_id']
        return render_template('show_graph.html',file_content=file_content,file_content_json=jsonobj, valid_file=True)
    else:
        file_content = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        return render_template('show_graph.html',file_content=file_content, valid_file=False)

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    """
    Handles meta-data files upload.
    """
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('upload_file.html')


@app.route('/query', methods=['GET','POST'])
def handle_query():
    """
    Handles Queries.
    """

    app.logger.info("inside handle query")
    if request.method == 'POST':
        queries =request.form.get('query')
        queries=queries.split(',')

        querydict={}

        for query in queries:
            querydict[query.split(':')[0]]=query.split(':')[1]
                
        client = MongoClient()
        db = client.test_database
        graphs = db.graphs

        query=json.dumps(querydict)
        app.logger.info(query)
        #result=graphs.find_one(json.loads(query),{"_id":0})
        result=graphs.find_one(querydict,{"_id":0})
        app.logger.info(result)
        client.close()
        jsonobj=json.dumps(result)
        result=yaml.safe_load(json.dumps(result))
        app.logger.info(result["filename"])
        app.logger.info(json.dumps(result))
        #render_template('show_graph.html',file_content=file_content,file_content_json=jsonobj, valid_file=True)
        return render_template('show_graph.html',file_content=result,file_content_json=jsonobj, valid_file=True)

    return render_template('query.html')

@app.route('/dummy')
def dummy_graph():
    """
    Display a dummy c3.js graph.
    """
    return render_template('dummy.html')


def push_to_mongo(file_content):
    client = MongoClient()
    db = client.test_database
    graphs = db.graphs
    #app.logger.info("Printing file content:")
    #app.logger.info(file_content)
    objid=graphs.insert_one(file_content).inserted_id
    client.close()
    #app.logger.info(file_content)
    return graphs.find_one({"_id":objid},{"_id":0})
    #app.logger.info("Inserted in DB")

def parse_csv(filename):
    """
    Parser function for csv type files.
    Returns:
        file_content - type : dict
    """
    file_content = {'filename':filename}
    try:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as f:
            for line in f.readlines():
                app.logger.info(line)
                line_content = line.split(',')
                if line_content[0] == 'name':
                    file_content['name'] = line_content[1].strip()
                elif line_content[0] == 'data':
                    if not 'data' in file_content.keys():
                        file_content['data'] = {line_content[1]:[line_content[1]]+[float(val) for val in line_content[2:]]}
                    else:
                        file_content['data'][line_content[1]] = [line_content[1]]+[float(val) for val in line_content[2:]]
                elif line_content[0] == 'type':
                    file_content['type'] = js_string(line_content[1].strip())
                elif line_content[0] == 'types':
                    if not 'types' in file_content.keys():
                        file_content['types'] = {line_content[1]:js_string(line_content[2].strip())}
                    else:
                        file_content['types'][line_content[1]] = js_string(line_content[2].strip())
                elif line_content[0] == 'groups':
                    if not 'groups' in file_content.keys():
                        file_content['groups'] = [[line_content[1].strip(),line_content[2].strip()]]
                    else:
                        file_content['groups'].append([line_content[1].strip(),line_content[2].strip()])

        return file_content
    except:
        return sys.exc_info()[0]

def js_string(string):
    """
    Returns:
        string suitable for use in JS.
        eg. mohit --> 'mohit'
    """
    return "'"+string+"'"

def check_file(filename, filetype):
    """
    Check if filename is of the given filetype.
    Returns:
        True  : if the check is positive
        False : otherwise
    """
    if filename.split('.')[-1] == filetype:
        return True
    return False

def allowed_file(filename):
    """
    Check if the filename is of the allowed global file-types.
    Returns:
        True  : if check is positive
        False : otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(debug=True)
