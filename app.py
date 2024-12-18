import re
from os import listdir, getenv
from os.path import join, splitext
import base64
import yaml
from flask import Flask, request, Response, render_template, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_minify import minify

DEFAULT_LAST_MOD = getenv('BUILD_DATE')
CONTACT_INFO = [
    {
        "label": "Email",
        "icon": "email.svg",
        "text": "patrickvevans@gmail.com",
        "href": "mailto:patrickvevans@gmail.com",
    },
    {
        "label": "Matrix",
        "icon": "matrix.svg",
        "text": "@holysoles:beeper.com",
        "href": "https://matrix.to/#/@holysoles:beeper.com",
    },
]

app = Flask(__name__, static_folder='static', static_url_path='')

minify(app=app, html=True, js=True, cssless=True, static=True)

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

def encode_contact_info(contact_info):
    encode_type = "utf-8"
    for dict in contact_info:
        dict["href"] = base64.b64encode(dict["href"].encode(encode_type)).decode(encode_type)
        dict["text"] = base64.b64encode(dict["text"].encode(encode_type)).decode(encode_type)
    return contact_info

encoded_contact_info = encode_contact_info(CONTACT_INFO)
@app.route("/contact", methods=['GET'])
def contact():
    return render_template('contact.html.j2', contact_info=encoded_contact_info)

@app.route("/projects", methods=["GET"])
def projects():
    return render_template('projects.html.j2')

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    static_pages = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            static_pages.append(url)

    _, timeline = get_posts()
    xml = render_template('sitemap.xml.j2', host_url=request.host_url[:-1], static_pages=static_pages, blog_posts=timeline, default_last_mod=DEFAULT_LAST_MOD)
    r = Response(response=xml, status=200, mimetype="application/xml")
    r.headers["Content-Type"] = "text/xml; charset=utf-8"
    return r
