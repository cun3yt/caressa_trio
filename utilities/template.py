from django.template.loader import get_template


def template_to_str(template_file, context) -> str:
    """
    Executes the template file with the context dictionary provided and
    returns the string content

    :param template_file: String
    :param context: Dict
    :return: string
    """

    template_content = get_template(template_file)
    context = {} if context is None else context
    return template_content.render(context)
