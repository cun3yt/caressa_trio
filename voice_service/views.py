import os

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from voice_service.google.tts import tts
from voice_service.google.transcribe import transcribe_file
from voice_service.google.intents import yes_intent, no_intent

from caressa.settings import PROJECT_ROOT


# todo: File Upload needs to be written in DRF
@csrf_exempt
def speech_to_text(request):
    if request.method == 'POST':
        data = request.FILES['file']

        if not data:
            print('no file is found!')
            return

        file_saved_path = os.path.join(PROJECT_ROOT, 'uploads/{}'.format(data.name))
        path = default_storage.save(file_saved_path, ContentFile(data.read()))
        print('file saved here: {}. Also check: {}'.format(file_saved_path, path))

        res = transcribe_file(file_saved_path)

        is_yes_match = yes_intent.is_match(res)
        is_no_match = no_intent.is_match(res)

        if is_yes_match == is_no_match:
            print('BOTH ON')
            _, speech_response = tts(text='I am confused because you did not exactly said yes or no!')
            response = HttpResponse(open(speech_response, 'rb'), content_type='audio/mpeg')
            response['Content-Length'] = os.path.getsize(speech_response)
            return response
        if is_yes_match:
            print('YES')
            _, speech_response = tts(text='I am glad you said yes!')
            response = HttpResponse(open(speech_response, 'rb'), content_type='audio/mpeg')
            response['Content-Length'] = os.path.getsize(speech_response)
            return response
        if is_no_match:
            print('NO')
            _, speech_response = tts(text='Okey, no problem!')
            response = HttpResponse(open(speech_response, 'rb'), content_type='audio/mpeg')
            response['Content-Length'] = os.path.getsize(speech_response)
            return response

    print('NEITHER')
    _, speech_response = tts(text='Say what?')
    response = HttpResponse(open(speech_response, 'rb'), content_type='audio/mpeg')
    response['Content-Length'] = os.path.getsize(speech_response)
    return response
