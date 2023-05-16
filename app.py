from flask import Flask, render_template
import yaml
from os import listdir
from os.path import isfile, join

app = Flask(__name__)

@app.route("/")
def home():
    yaml_path = './posts/'
    yaml_files = [join(yaml_path, file) for file in listdir(yaml_path) if isfile(join(yaml_path, file))]
    post_array = []
    yaml_files.sort(reverse=True)
    for yaml_file in yaml_files:
        with open(yaml_file, 'r') as file:
            post_array.append(yaml.safe_load(file))
    return render_template('blog.html', post_array=post_array)

@app.route("/contact")
def contact():
    return render_template('contact.html')