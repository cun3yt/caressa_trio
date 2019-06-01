import re


def ssml_post_process(ssml: str) -> str:
    """
    Remove unnecessary whitespaces

    :param ssml: str
    :return: str
    """
    return re.sub(r' +', ' ', re.sub(r'[\s+]', ' ', ssml)).strip()


def ssml_new_lines_to_breaks(data):
    arr = data.splitlines()
    str_with_markup = ""

    for content in arr:
        format_string = "<media begin='0.5s'><speak>{content}</speak></media>".format(content=content)
        str_with_markup += format_string
    return "<seq>{str_with_markup}</seq>".format(str_with_markup=str_with_markup)
