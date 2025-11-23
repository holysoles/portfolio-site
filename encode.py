import base64


def contact_info(contact_info):
    encode_type = "utf-8"
    for dict in contact_info:
        if dict.get("mask", False):
            dict["href"] = base64.b64encode(dict["href"].encode(encode_type)).decode(
                encode_type
            )
    return contact_info
