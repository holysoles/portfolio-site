import re
from os import listdir
from os.path import join, splitext
import yaml
from flask import Flask, request, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_minify import minify

app = Flask(__name__)

minify(app=app, html=True, js=True, cssless=True)

# Proxy setup
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

posts_dir = './blog/posts/'
code_snippet_path = './blog/code_snippets/'

def get_posts():
    dir_files = listdir(posts_dir)
    yaml_files = [file for file in dir_files if splitext(file)[1] == '.yaml']
    yaml_files.sort(reverse=True)
    timeline = {}
    for yaml_file in yaml_files:
        file_dict = {
            'file_name': yaml_file,
            'link_to_post': "/post?date=" + yaml_file,
        }
        # collect datetime info
        datetime_list = re.split('_|\.', yaml_file)
        file_year = int(datetime_list[0])
        file_month = int(datetime_list[1])
        file_day = int(datetime_list[2])
        if file_year in timeline:
            if file_month in timeline[file_year]:
                timeline[file_year][file_month][file_day] = file_dict
            else:
                timeline[file_year][file_month] = {file_day: file_dict}
        else:
            timeline[file_year] = {file_month: {file_day: file_dict}}
    return yaml_files, timeline

def load_post_data(yaml_files, timeline = {}):
    post_array = []
    if timeline:
        yaml_files = []
        for year in sorted(timeline, reverse=True):
            for month in sorted(timeline[year], reverse=True):
                for day in sorted(timeline[year][month]):
                    yaml_files.append(timeline[year][month][day]['file_name'])
    for yaml_file in yaml_files:
        # load in post text
        with open(join(posts_dir, yaml_file), 'r') as file:
            post_data = yaml.safe_load(file)

        # perform pre-processing
        if post_data.get('body'):
            for body in post_data['body']:
                # parse and preload code snippet files
                if body.get('code'):
                    with open(join(code_snippet_path, body['code']), 'r') as file:
                        code_snippet = file.read()
                        body['code'] = code_snippet
                if body.get('text'):
                    body['text'] = parse_hyperlinks(body['text'])
        post_array.append(post_data)
    return post_array

def parse_hyperlinks(paragraph: str)-> str:
    markdown_link_re = re.compile(r'\[[^\[\]]*\]\([^\(\)]*\)')
    text_re = re.compile(r'(?<=\[)[^\[\]]*(?=\])')
    link_re = re.compile(r'(?<=\()[^\(\)]*(?=\))')
    all_hyperlinks = markdown_link_re.finditer(paragraph)
    for hyperlink in all_hyperlinks:
        hyperlink_match = hyperlink.group()
        text = text_re.search(hyperlink_match).group()
        link = link_re.search(hyperlink_match).group()
        new_hyperlink = f"<a href=\"{link}\">{text}</a>"
        paragraph = paragraph.replace(hyperlink_match, new_hyperlink)
    return paragraph

@app.route("/", methods=['GET'])
def home():
    yaml_files, timeline = get_posts()
    post_array = load_post_data(yaml_files, timeline=timeline)
    return render_template('blog.html.j2', post_array=post_array, date_dict=timeline)

@app.route("/post", methods=['GET'])
def post():
    req_post = request.args.get('date')
    if req_post:
        yaml_files, timeline = get_posts()
        if req_post in yaml_files:
            post = load_post_data([req_post])
            return render_template('blog.html.j2', post_array=post, date_dict=timeline)
    return "Post not found", 404

@app.route("/contact", methods=['GET'])
def contact():
    return render_template('contact.html.j2')

@app.route("/projects", methods=["GET"])
def projects():
    return render_template('projects.html.j2')