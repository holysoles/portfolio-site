import re
from os import listdir
from os.path import join, splitext

import yaml

BLOG_ROOT = "./blog"
CODE_SNIPPET_PATH = "./blog/code_snippets/"


def get_posts(subdir: str):
    posts_dir = join(BLOG_ROOT, subdir)
    dir_files = listdir(posts_dir)
    yaml_files = [file for file in dir_files if splitext(file)[1] == ".yaml"]
    yaml_files.sort(reverse=True)
    timeline = {}
    for yaml_file in yaml_files:
        file_dict = {
            "file_name": yaml_file,
        }
        # collect datetime info
        datetime_list = re.split("_|\.", yaml_file)
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


def load_post_data(files: list[str], subdir: str = ""):
    post_array = []
    post_dir = join(BLOG_ROOT, subdir)
    for yaml_file in files:
        # load in post text
        with open(join(post_dir, yaml_file), "r") as file:
            post_data = yaml.safe_load(file)

        # perform pre-processing
        date_link, _ = splitext(yaml_file)
        date_elems = date_link.split("_")
        post_data["date"] = ""
        if len(date_elems) > 1:
            post_data["date"] = f"{date_elems[1]}/{date_elems[2]}/{date_elems[0]}"
        if post_data.get("body"):
            for body in post_data["body"]:
                # parse and preload code snippet files
                if body.get("code"):
                    with open(
                        join(CODE_SNIPPET_PATH, body["code"]["file_name"]), "r"
                    ) as file:
                        code_snippet = file.read()
                        body["code"]["type"] = splitext(body["code"]["file_name"])[
                            1
                        ].replace(".", "")
                        body["code"]["content"] = code_snippet
                if body.get("text"):
                    body["text"] = parse_table(body["text"])
                    body["text"] = parse_hyperlinks(body["text"])
                    body["text"] = parse_bold(body["text"])
                    body["text"] = parse_code_inline(body["text"])
        post_array.append(post_data)
    return post_array


def parse_hyperlinks(paragraph: str) -> str:
    markdown_link_re = re.compile(r"\[[^\[\]]*\]\([^\(\)]*\)")
    text_re = re.compile(r"(?<=\[)[^\[\]]*(?=\])")
    link_re = re.compile(r"(?<=\()[^\(\)]*(?=\))")
    all_hyperlinks = markdown_link_re.finditer(paragraph)
    for hyperlink in all_hyperlinks:
        hyperlink_match = hyperlink.group()
        text = text_re.search(hyperlink_match).group()
        link = link_re.search(hyperlink_match).group()
        new_hyperlink = f'<a href="{link}">{text}</a>'
        paragraph = paragraph.replace(hyperlink_match, new_hyperlink)
    return paragraph


def parse_bold(paragraph: str) -> str:
    bold_re = re.compile(r"(\*\*).+?(\*\*)")
    bold_text_re = re.compile(r"(?<=\*\*).+?(?=\*\*)")
    all_bold_text = bold_re.finditer(paragraph)
    for bold_match in all_bold_text:
        bold_match_text = bold_match.group()
        matches = re.search(bold_text_re, bold_match_text)
        if matches is None:
            raise Exception("error parsing bolded text")
        text = matches.group()
        new_text = f"<b>{text}</b>"
        paragraph = paragraph.replace(bold_match_text, new_text)
    return paragraph


def parse_code_inline(paragraph: str) -> str:
    bold_re = re.compile(r"(\`).+?(\`)")
    bold_text_re = re.compile(r"(?<=\`).+?(?=\`)")
    all_bold_text = bold_re.finditer(paragraph)
    for bold_match in all_bold_text:
        bold_match_text = bold_match.group()
        matches = re.search(bold_text_re, bold_match_text)
        if matches is None:
            raise Exception("error parsing code syntax text")
        text = matches.group()
        new_text = f"<code>{text}</code>"
        paragraph = paragraph.replace(bold_match_text, new_text)
    return paragraph


def parse_table(paragraph: str) -> str:
    table_re = re.compile(r"(\|.*\|(\n|$))+")
    table_match = table_re.search(paragraph)
    if table_match is not None:
        table_og_text = table_match.group()
        table_re_text = re.compile(r"[^\|]+")
        all_table = table_re_text.finditer(table_og_text)
        header_sep_re = re.compile(r"\s+-+\s+")
        table_rows = ""
        row = "<tr>"
        cell_type = "th"
        for match in all_table:
            cell = match.group()
            if cell == "\n":
                # make sure not empty row
                if row != "<tr>":
                    row += "</tr>"
                    table_rows += row
                    row = "<tr>"
            elif header_sep_re.match(cell) is not None:
                cell_type = "td"
            else:
                row += f"<{cell_type}>{cell}</{cell_type}>"
        # hack: table can't under p
        new_text = f"""</p><table>
        {table_rows}
        </table><p class="article-text">"""
        paragraph = paragraph.replace(table_og_text, new_text)
    return paragraph


def get_tags() -> list[str]:
    yaml_files, _ = get_posts(subdir="posts")
    post_array = load_post_data(files=yaml_files, subdir="posts")
    tags = {}
    for post in post_array:
        if post.get("tags") is not None:
            for tag in post["tags"]:
                tags[tag] = None
    return tags.keys()
