import re


def ssml_post_process(ssml: str) -> str:
    """
    Remove unnecessary whitespaces

    :param ssml: str
    :return: str
    """
    return re.sub(r' +', ' ', re.sub(r'[\s+]', ' ', ssml)).strip()
