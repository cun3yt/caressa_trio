from twilio.rest import Client


def send_sms(to_phone_number, context):

    account_sid = 'AC6d70b398898414615a199da96fe39ed4'
    auth_token = '1ee5facd877ea03c9bea6ae0001c3eb3'
    from_phone_number = '+14156499485'
    body = "Hello {prospect_name}, {facility_name} invited you to connect with your senior " \
           "{prospect_senior_full_name} using Caressa. Click the link below to download Caressa app and feel " \
           "better connected with {prospect_senior_first_name}. " \
           "{invitation_url}"

    to_send_text = body.format(prospect_name=context['prospect_name'],
                               facility_name=context['facility_name'],
                               prospect_senior_full_name=context['prospect_senior_full_name'],
                               prospect_senior_first_name=context['prospect_senior_first_name'],
                               invitation_url=context['invitation_url'])

    client = Client(account_sid, auth_token)
    send_res = client.messages.create(body=to_send_text, from_=from_phone_number, to=to_phone_number)

    return send_res, to_send_text, to_phone_number
