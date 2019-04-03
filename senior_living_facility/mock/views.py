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


def user_profile(request, **kwargs):
    pics = User.objects.filter(pk=100)[0].get_profile_pictures()

    response = {
        "id": 100,
        "first_name": "Pamela",
        "last_name": "Emeryville",
        'profile_picture_url': pics.get('w_250'),
        'thumbnail_url': pics.get('w_25'),
        "online_status": "Online",
        "message_thread_url": "https://caressa.heroku.app/message-threads/16/messages",
        "phone_number": "+14154395638",
        "birthday:": "08/15/1932",
        "move_in data": "10/02/2017",
        "service_type": "independent",
        "morning_status": {
            "status": "self-checked-in",
            "label": "Self Checked"
        },
        "senior_specific": {
            "primary_contact": {
                "first_name": "James",
                "last_name": "Emeryville",
                "relationship": "Son",
                "phone_number": "+14452375031"
            },
            "caretaker": {
                "first_name": "Julia",
                "last_name": "Hans",
                "phone_number": "+14452375031"
            }
        },
        "mock_status": True
    }

    return JsonResponse(response)
