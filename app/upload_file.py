import os, re, csv, json

from flask import Flask, render_template, request, redirect, url_for
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.utils import secure_filename
from itertools import groupby
from collections import Counter

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = r'C:\flask\app\static\logs'
app.config['RESULT_FILE'] = r'C:\flask\app\static\logs'

def format_str(log_line):
    IP_regexp = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    PgType_regexp = r' +\d{3} +\-'
    keys = ['date', 'time', 'IP_addr', 'Request_Type', 'Page_type', 'Remote_addr']
    str_var = []
    
    str_lst = log_line.split(" ")
    str_lst1 = str_lst[:4]
    page_type = re.findall(PgType_regexp, log_line)
    ips_list = re.findall(IP_regexp, log_line)
    
    str_lst1.extend([x.strip('-').strip(' ') for x in page_type])
    str_var = str_lst1
    if ips_list:
        if ips_list[1]:
            str_var.append(ips_list[1])    

    str_dict = dict(zip(keys, str_lst1))
    return str_dict


def canonicalize_dict(x):
    "Return a (key, value) list sorted by the hash of the key"
    return sorted(x.items(), key=lambda x: hash(x[0]))

def unique_and_count(lst):
    "Return a list of unique dicts with a 'count' key added"
    grouper = groupby(sorted(map(canonicalize_dict, lst)))
    return [dict(k + [("count", len(list(g)))]) for k, g in grouper]

def reader(filename):    
    addr_list = []
    str_list = []
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as f:
        for line in f:
            dict_str = format_str(line)
            str_list.append(dict_str)
    
    return unique_and_count(str_list)

def write_to_file(data):
    with open(r'C:\flask\app\static\logs\outputfile.log', 'w') as fout:
        json.dump(data, fout)

@app.route('/read_file', methods=['GET'])
def read_uploaded_file():
    filename = secure_filename(request.args.get('filename'))
    try:
        if filename:
            write_to_file(reader(filename))
            filename = r'\outputfile.log'
            with open(r'C:\flask\app\static\logs\outputfile.log') as f:
                return f.read()
    except IOError:
        pass
    return "Unable to read file"

@app.route('/upload_file', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('read_uploaded_file', filename=filename))
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
