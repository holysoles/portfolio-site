from os import getenv
import base64
import src.posts as posts
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

TAGS = posts.get_tags()

app = Flask(__name__, static_folder='static', static_url_path='')

minify(app=app, html=True, js=True, cssless=True, static=True)

# Proxy setup
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

@app.get("/")
def home():
    return post()

@app.get("/blog/post/<date>")
@app.get("/blog")
def post(date: str = None, year: str = None, tag: str = None):
    if not year:
        year = request.args.get('year')
    if not tag:
        tag = request.args.get('tag')

    yaml_files, timeline = posts.get_posts()

    if date is not None:
        req_post = date + '.yaml'
        if req_post not in yaml_files:
            return "Post not found", 404
        post_array = posts.load_post_data(yaml_files=[req_post])
    else:
        # process years before loading post data since we can just search filenames
        if year:
            yaml_files = [file for file in yaml_files if file.split('_')[0] == year]
        post_array = posts.load_post_data(yaml_files=yaml_files)
        # process tag filtering now that we have post data
        if tag:
            post_array = [post for post in post_array if tag in post.get('tags', [])]

    # TODO split out preprocessing from loading base YAMLs for speedup
    return render_template('blog.html.j2', post_array=post_array, date_dict=timeline, tags=TAGS)

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

    _, timeline = posts.get_posts()
    xml = render_template('sitemap.xml.j2', host_url=request.host_url[:-1], static_pages=static_pages, blog_posts=timeline, default_last_mod=DEFAULT_LAST_MOD)
    r = Response(response=xml, status=200, mimetype="application/xml")
    r.headers["Content-Type"] = "text/xml; charset=utf-8"
    return r
