from twilio.rest import Client
from caressa.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
from django.template.loader import get_template


def send_sms(to_phone_number, context, template_txt):
    context = {} if context is None else context

    text_template_content = get_template(template_txt)

    data = context

    text_content = text_template_content.render(data)

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message_instance = client.messages.create(body=text_content, from_=TWILIO_PHONE_NUMBER, to=to_phone_number)
    send_res = {
        'date_sent': message_instance.date_sent,
        'direction': message_instance.direction,
        'body': message_instance.body,
        'from': message_instance.from_
    }

    return send_res, text_content, to_phone_number
