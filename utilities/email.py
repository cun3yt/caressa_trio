from django.core.mail import EmailMultiAlternatives
from utilities.template import template_to_str


FROM_EMAIL = 'cuneyt@caressa.ai'    # todo hardcode and suitable email change


def send_email(to_email_addresses, subject, template_html_file, template_txt_file, context=None):
    html_content = template_to_str(template_html_file, context)
    text_content = template_to_str(template_txt_file, context)

    msg = EmailMultiAlternatives(subject, text_content, FROM_EMAIL, to_email_addresses)
    msg.attach_alternative(html_content, "text/html")

    send_res = msg.send()
    return send_res, html_content, text_content, to_email_addresses
