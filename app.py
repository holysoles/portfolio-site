from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_minify import minify
import yaml
import re
from os import listdir
from os.path import isfile, join, splitext

app = Flask(__name__)

minify(app=app, html=True, js=True, cssless=True)

# Proxy setup
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

@app.route("/")
def home():
    posts_dir = './blog/posts/'
    code_snippet_path = './blog/code_snippets/'
    dir_files = listdir(posts_dir)
    yaml_files = [file for file in dir_files if splitext(file)[1] == '.yaml']
    yaml_files.sort(reverse=True)
    post_array = []
    timeline = {}
    for yaml_file in yaml_files:
        # collect datetime info
        datetime_list = re.split('_|\.', yaml_file)
        file_year = datetime_list[0]
        file_month = datetime_list[1]
        file_day = datetime_list[2]
        if file_year in timeline:
            if file_month in timeline[file_year]:
                timeline[file_year][file_month].append(file_day)
            else:
                timeline[file_year][file_month] = {file_day: }
        else:
            timeline[file_year] = {file_month: [file_day]}

        # load in post text
        with open(join(posts_dir, yaml_file), 'r') as file:
            post_data = yaml.safe_load(file)
        
        # parse and preload code snippet files
        if post_data.get('body'):
            for body in post_data['body']:
                if body.get('code'):
                    with open(join(code_snippet_path, body['code']), 'r') as file:
                        code_snippet = file.read()
                        body['code'] = code_snippet
        
        post_array.append(post_data)
    return render_template('blog.html', post_array=post_array, date_dict=timeline)

@app.route("/contact")
def contact():
    return render_template('contact.html')