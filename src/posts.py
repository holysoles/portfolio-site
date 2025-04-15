import yaml
from os import listdir
from os.path import join, splitext
import re

POSTS_DIR = './blog/posts/'
CODE_SNIPPET_PATH = './blog/code_snippets/'

def get_posts():
    dir_files = listdir(POSTS_DIR)
    yaml_files = [file for file in dir_files if splitext(file)[1] == '.yaml']
    yaml_files.sort(reverse=True)
    timeline = {}
    for yaml_file in yaml_files:
        file_dict = {
            'file_name': yaml_file,
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

def load_post_data(yaml_files):
    post_array = []
    for yaml_file in yaml_files:
        # load in post text
        with open(join(POSTS_DIR, yaml_file), 'r') as file:
            post_data = yaml.safe_load(file)

        # perform pre-processing
        date_link, _ = splitext(yaml_file)
        date_elems = date_link.split('_')
        post_data["date"] = f"{date_elems[1]}/{date_elems[2]}/{date_elems[0]}"
        if post_data.get('body'):
            for body in post_data['body']:
                # parse and preload code snippet files
                if body.get('code'):
                    with open(join(CODE_SNIPPET_PATH, body['code']['file_name']), 'r') as file:
                        code_snippet = file.read()
                        body['code']['type'] = splitext(body['code']['file_name'])[1].replace('.', '')
                        body['code']['content'] = code_snippet
                if body.get('text'):
                    body['text'] = parse_hyperlinks(body['text'])
                    body['text'] = parse_bold(body['text'])
                    body['text'] = parse_code_inline(body['text'])
        post_array.append(post_data)
    return post_array

def parse_hyperlinks(paragraph: str) -> str:
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

def parse_bold(paragraph: str) -> str:
    bold_re = re.compile(r'(\*\*).+?(\*\*)')
    bold_text_re = re.compile(r'(?<=\*\*).+?(?=\*\*)')
    all_bold_text = bold_re.finditer(paragraph)
    for bold_match in all_bold_text:
        bold_match_text = bold_match.group()
        text = re.search(bold_text_re, bold_match_text).group()
        new_text = f"<b>{text}</b>"
        paragraph = paragraph.replace(bold_match_text, new_text)
    return paragraph

def parse_code_inline(paragraph: str) -> str:
    bold_re = re.compile(r'(\`).+?(\`)')
    bold_text_re = re.compile(r'(?<=\`).+?(?=\`)')
    all_bold_text = bold_re.finditer(paragraph)
    for bold_match in all_bold_text:
        bold_match_text = bold_match.group()
        text = re.search(bold_text_re, bold_match_text).group()
        new_text = f"<code>{text}</code>"
        paragraph = paragraph.replace(bold_match_text, new_text)
    return paragraph

def get_tags() -> list[str]:
    yaml_files, _ = get_posts()
    post_array = load_post_data(yaml_files)
    tags = {}
    for post in post_array:
        if post.get('tags') is not None:
            for tag in post['tags']:
                tags[tag] = None
    return tags.keys()