def speech_render(speech):
    return {
        "type": "SSML",
        "ssml": "<speak>{}</speak>".format(speech)
    }


def alexa_render(speech, directive=None, should_session_end=False):
    template = {
        "version": "1.0",
        "response": {
            "outputSpeech": speech_render(speech),
            "reprompt": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Can I help you with any thing?"
                }
            },
            "shouldEndSession": should_session_end
        }
    }

    if directive:
        template['directives'] = [
            {
                "type": "Dialog.Delegate",
                "updatedIntent": {
                    "name": directive.get('intent_name'),
                    "confirmationStatus": "NONE",
                    "slots": {
                        directive.get('slot_to_elicit'): {
                            "name": directive.get('slot_to_elicit'),
                            "value": "string",
                            "confirmationStatus": "NONE"
                        }
                    }
                }
            }
            # dialog model dialogState:STARTED, IN_PROGRESS

            # {
            #     "type": "Dialog.ElicitSlot",
            #     "slotToElicit": directive.get('slot_to_elicit'),
            #     "updatedIntent": {
            #         "name": directive.get('intent_name'),
            #         "confirmationStatus": "NONE",
            #         "slots": {
            #             directive.get('slot_to_elicit'): {
            #                 "name": directive.get('slot_to_elicit'),
            #                 "confirmationStatus": "NONE"
            #             },
            #         },
            #     },
            # },
        ]

    print(template)

    return template
