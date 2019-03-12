from twilio.rest import Client
from caressa.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
from utilities.template import template_to_str


def send_sms(to_phone_number, context, template_file):
    text_content = template_to_str(template_file, context)
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message_instance = client.messages.create(body=text_content, from_=TWILIO_PHONE_NUMBER, to=to_phone_number)
    send_res = {
        'date_sent': message_instance.date_sent,
        'direction': message_instance.direction,
        'body': message_instance.body,
        'from': message_instance.from_
    }

    return send_res, text_content, to_phone_number
