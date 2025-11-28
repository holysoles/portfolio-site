from os import getenv

from flask import Flask, Response, render_template, request, url_for
from flask_caching import Cache
from flask_minify import minify
from werkzeug.middleware.proxy_fix import ProxyFix

import encode
import src.posts as posts

DEFAULT_LAST_MOD = getenv("BUILD_DATE")
USE_CACHE = getenv("USE_CACHE", "false")
CONTACT_INFO = [
    {
        "label": "GitHub",
        "icon": "github.svg",
        "href": "https://github.com/holysoles",
        "mask": False,
    },
    {
        "label": "Linkedin",
        "icon": "linkedin.svg",
        "href": "https://www.linkedin.com/in/patrickvevans",
        "mask": False,
    },
    {
        "label": "Mastodon",
        "icon": "mastodon.svg",
        "href": "https://unifed.io/@pat",
        "mask": False,
    },
    {
        "label": "Email",
        "icon": "email.svg",
        "href": "mailto:patrickvevans@gmail.com",
        "mask": True,
    },
    {
        "label": "Matrix",
        "icon": "matrix.svg",
        "href": "https://matrix.to/#/@holysoles:beeper.com",
        "mask": True,
    },
]
ENCODED_CONTACT_INFO = encode.contact_info(CONTACT_INFO)

TAGS = posts.get_tags()

cache_type = "NullCache"
if USE_CACHE == "true":
    cache_type = "SimpleCache"
config = {
    "CACHE_TYPE": cache_type,
}
app = Flask(__name__, static_folder="static", static_url_path="")
app.config.from_mapping(config)

if getenv("TESTING") != "true":
    minify(app=app, html=True, js=True, cssless=True, static=True)
cache = Cache(app)

# Proxy setup
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


@app.get("/")
@cache.cached()
def home():
    return post()


@app.get("/blog/post/<date>")
@app.get("/blog")
def post(date: str | None = None, year: str | None = None, tag: str | None = None):
    if year is None:
        year = request.args.get("year")
    if tag is None:
        tag = request.args.get("tag")

    yaml_files, timeline = posts.get_posts(subdir="posts")

    if date is not None:
        req_post = date + ".yaml"
        if req_post not in yaml_files:
            return "Post not found", 404
        post_array = posts.load_post_data(files=[req_post], subdir="posts")
    else:
        # process years before loading post data since we can just search filenames
        if year:
            yaml_files = [file for file in yaml_files if file.split("_")[0] == year]
        post_array = posts.load_post_data(files=yaml_files, subdir="posts")
        # process tag filtering now that we have post data
        if tag:
            post_array = [post for post in post_array if tag in post.get("tags", [])]

    # TODO split out preprocessing from loading base YAMLs for speedup
    return render_template(
        "blog.html",
        post_array=post_array,
        date_dict=timeline,
        tags=TAGS,
        contact_info=ENCODED_CONTACT_INFO,
    )


@app.route("/about", methods=["GET"])
@cache.cached()
def about():
    about_content = posts.load_post_data(files=["about.yaml"])[0]
    return render_template(
        "about.html",
        content=about_content,
        contact_info=ENCODED_CONTACT_INFO,
    )


@app.route("/projects", methods=["GET"])
@cache.cached()
def projects():
    return render_template(
        "projects.html",
        contact_info=ENCODED_CONTACT_INFO,
    )


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/sitemap.xml", methods=["GET"])
@cache.cached()
def sitemap():
    static_pages = []
    for rule in app.url_map.iter_rules():
        if type(rule.methods) == set[str]:
            if "GET" in rule.methods and has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                static_pages.append(url)

    _, timeline = posts.get_posts(subdir="posts")
    xml = render_template(
        "sitemap.xml",
        host_url=request.host_url[:-1],
        static_pages=static_pages,
        blog_posts=timeline,
        default_last_mod=DEFAULT_LAST_MOD,
    )
    r = Response(response=xml, status=200, mimetype="application/xml")
    r.headers["Content-Type"] = "text/xml; charset=utf-8"
    return r
