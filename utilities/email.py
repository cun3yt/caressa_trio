from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


FROM_EMAIL = 'cuneyt@caressa.ai' # todo hardcode and suitable email change


def send_email(to_email_address, subject, template_html, template_txt, context=None):
    context = {} if context is None else context

    html_template_content = get_template(template_html)
    text_template_content = get_template(template_txt)

    data = context

    text_content = text_template_content.render(data)
    html_content = html_template_content.render(data)

    msg = EmailMultiAlternatives(subject, text_content, FROM_EMAIL, [to_email_address])
    msg.attach_alternative(html_content, "text/html")

    send_res = msg.send()
    return send_res, html_content, text_content, to_email_address
