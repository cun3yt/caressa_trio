from django.http import JsonResponse

from alexa.models import User


def message_thread(request, **kwargs):
    response = {
        "resident": {
            "id": 94,
            "first_name": "Edward",
            "last_name": "Hofferton",
            "room_no": "106",
            "device_status": {
                "is_online": True,
                "status_checked": "2019-02-02T23:37:43.811630Z",
                "last_activity_time": "2019-03-22T03:59:08.302690Z",
                "is_today_checked_in": True
            },
            "message_thread_url": "https://caressa.herokuapp.com/senior-id-94-message-thread-url",
            "profile_picture": "https://s3-us-west-1.amazonaws.com/caressa-prod/images/user/no_user/default_profile_pic_w_250.jpg",
            "mock_status": True
        },
        "messages": {
            "url": "https://caressa.herokuapp.com/api/message-threads/1/messages/"
        },
        "mock_status": True
    }

    return JsonResponse(response)
