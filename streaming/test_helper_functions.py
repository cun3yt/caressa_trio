def request_body_creator_for_intent(is_cold_start, request_type):
    request_body_1 = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'TestAlexaSessionId1',
            'application': {
                'applicationId': 'TestAlexaUserId1'
            },
            'user': {
                'userId': 'TestAlexaUserId1'
            }
        },
        'context': {
            'AudioPlayer': {
                'playerActivity': 'IDLE'
            },
            'System': {
                'application': {
                    'applicationId': 'TestAlexaUserId1'
                },
                'user': {
                    'userId': 'TestAlexaUserId1'
                },
                'device': {
                    'deviceId': 'TestAlexaDeviceId1',
                    'supportedInterfaces': {
                        'AudioPlayer': {

                        }
                    }
                },
                'apiEndpoint': 'https://api.amazonalexa.com',
                'apiAccessToken': 'TestAlexaApiAccessToken1'
            }
        },
        'request': {
            'type': 'IntentRequest',
            'requestId': 'TestAlexaRequestId1',
            'timestamp': '2018-09-19T00:50:17Z',
            'locale': 'en-US',
            'intent': {
                'name': request_type,
                'confirmationStatus': 'NONE',
            },
        },
    }
    request_body_2 = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'TestAlexaSessionId2',
            'application': {
                'applicationId': 'TestAlexaUserId2'
            },
            'user': {
                'userId': 'TestAlexaUserId2'
            }
        },
        'context': {
            'AudioPlayer': {
                'playerActivity': 'IDLE'
            },
            'System': {
                'application': {
                    'applicationId': 'TestAlexaUserId2'
                },
                'user': {
                    'userId': 'TestAlexaUserId2'
                },
                'device': {
                    'deviceId': 'TestAlexaDeviceId2',
                    'supportedInterfaces': {
                        'AudioPlayer': {

                        }
                    }
                },
                'apiEndpoint': 'https://api.amazonalexa.com',
                'apiAccessToken': 'TestAlexaApiAccessToken1'
            }
        },
        'request': {
            'type': 'IntentRequest',
            'requestId': 'TestAlexaRequestId1',
            'timestamp': '2018-09-19T00:50:17Z',
            'locale': 'en-US',
            'intent': {
                'name': request_type,
                'confirmationStatus': 'NONE',
            },
        }
    }
    return request_body_1 if is_cold_start else request_body_2


def request_body_creator_for_audio_player(is_cold_start, request_type, token=None):
    request_body_1 = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'TestAlexaSessionId1',
            'application': {
                'applicationId': 'TestAlexaUserId1'
            },
            'user': {
                'userId': 'TestAlexaUserId1'
            }
        },
        'context': {
            'AudioPlayer': {
                "offsetInMilliseconds": 0,
                "token": token,
                "playerActivity": "PLAYING"
            },
            'System': {
                'application': {
                    'applicationId': 'TestAlexaUserId1'
                },
                'user': {
                    'userId': 'TestAlexaUserId1'
                },
                'device': {
                    'deviceId': 'TestAlexaDeviceId1',
                    'supportedInterfaces': {
                        'AudioPlayer': {

                        }
                    }
                },
                'apiEndpoint': 'https://api.amazonalexa.com',
                'apiAccessToken': 'TestAlexaApiAccessToken1'
            }
        },
        'request': {
            'type': request_type,
            'requestId': 'TestAlexaRequestId1',
            'timestamp': '2018-09-20T00:08:02Z',
            'locale': 'en-US',
            'token': token,
            'offsetInMilliseconds': 0
        },
    }
    request_body_2 = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'TestAlexaSessionId2',
            'application': {
                'applicationId': 'TestAlexaUserId2'
            },
            'user': {
                'userId': 'TestAlexaUserId2'
            }
        },
        'context': {
            'AudioPlayer': {
                "offsetInMilliseconds": 0,
                "token": token,
                "playerActivity": "PLAYING"
            },
            'System': {
                'application': {
                    'applicationId': 'TestAlexaUserId2'
                },
                'user': {
                    'userId': 'TestAlexaUserId2'
                },
                'device': {
                    'deviceId': 'TestAlexaDeviceId2',
                    'supportedInterfaces': {
                        'AudioPlayer': {}
                    }
                },
                'apiEndpoint': 'https://api.amazonalexa.com',
                'apiAccessToken': 'TestAlexaApiAccessToken1'
            }
        },
        'request': {
            'type': request_type,
            'requestId': 'TestAlexaRequestId2',
            'timestamp': '2018-09-20T00:08:02Z',
            'locale': 'en-US',
            'token': token,
            'offsetInMilliseconds': 0
        },
    }
    return request_body_1 if is_cold_start else request_body_2


def request_body_creator_for_next_command(is_cold_start, token=None):
    request_body_1 = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'TestAlexaSessionId1',
            'application': {
                'applicationId': 'TestAlexaUserId1'
            },
            'user': {
                'userId': 'TestAlexaUserId1'
            }
        },
        'context': {
            'AudioPlayer': {
                "offsetInMilliseconds": 5,
                "token": token,
                "playerActivity": "PLAYING"
            },
            'System': {
                'application': {
                    'applicationId': 'TestAlexaUserId1'
                },
                'user': {
                    'userId': 'TestAlexaUserId1'
                },
                'device': {
                    'deviceId': 'TestAlexaDeviceId1',
                    'supportedInterfaces': {
                        'AudioPlayer': {

                        }
                    }
                },
                'apiEndpoint': 'https://api.amazonalexa.com',
                'apiAccessToken': 'TestAlexaApiAccessToken1'
            }
        },
        'request': {
            'type': 'PlaybackController.NextCommandIssued',
            'requestId': 'TestAlexaRequestId1',
            'timestamp': '2018-09-20T00:08:02Z',
            'locale': 'en-US',
        },
    }
    request_body_2 = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'TestAlexaSessionId2',
            'application': {
                'applicationId': 'TestAlexaUserId2'
            },
            'user': {
                'userId': 'TestAlexaUserId2'
            }
        },
        'context': {
            'AudioPlayer': {
                "offsetInMilliseconds": 0,
                "token": token,
                "playerActivity": "PLAYING"
            },
            'System': {
                'application': {
                    'applicationId': 'TestAlexaUserId2'
                },
                'user': {
                    'userId': 'TestAlexaUserId2'
                },
                'device': {
                    'deviceId': 'TestAlexaDeviceId2',
                    'supportedInterfaces': {
                        'AudioPlayer': {}
                    }
                },
                'apiEndpoint': 'https://api.amazonalexa.com',
                'apiAccessToken': 'TestAlexaApiAccessToken1'
            }
        },
        'request': {
            'type': 'PlaybackController.NextCommandIssued',
            'requestId': 'TestAlexaRequestId2',
            'timestamp': '2018-09-20T00:08:02Z',
            'locale': 'en-US',
            'token': token,
            'offsetInMilliseconds': 0
        },
    }
    return request_body_1 if is_cold_start else request_body_2


def request_body_creator_for_pause_command(is_cold_start, token=None):
    request_body_1 = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'TestAlexaSessionId1',
            'application': {
                'applicationId': 'TestAlexaUserId1'
            },
            'user': {
                'userId': 'TestAlexaUserId1'
            }
        },
        'context': {
            'AudioPlayer': {
                "offsetInMilliseconds": 5,
                "token": token,
                "playerActivity": "STOPPED"
            },
            'System': {
                'application': {
                    'applicationId': 'TestAlexaUserId1'
                },
                'user': {
                    'userId': 'TestAlexaUserId1'
                },
                'device': {
                    'deviceId': 'TestAlexaDeviceId1',
                    'supportedInterfaces': {
                        'AudioPlayer': {

                        }
                    }
                },
                'apiEndpoint': 'https://api.amazonalexa.com',
                'apiAccessToken': 'TestAlexaApiAccessToken1'
            }
        },
        'request': {
            'type': 'PlaybackController.PauseCommandIssued',
            'requestId': 'TestAlexaRequestId1',
            'timestamp': '2018-09-20T00:08:02Z',
            'locale': 'en-US',
        },
    }
    request_body_2 = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'TestAlexaSessionId2',
            'application': {
                'applicationId': 'TestAlexaUserId2'
            },
            'user': {
                'userId': 'TestAlexaUserId2'
            }
        },
        'context': {
            'AudioPlayer': {
                "offsetInMilliseconds": 0,
                "token": token,
                "playerActivity": "STOPPED"
            },
            'System': {
                'application': {
                    'applicationId': 'TestAlexaUserId2'
                },
                'user': {
                    'userId': 'TestAlexaUserId2'
                },
                'device': {
                    'deviceId': 'TestAlexaDeviceId2',
                    'supportedInterfaces': {
                        'AudioPlayer': {}
                    }
                },
                'apiEndpoint': 'https://api.amazonalexa.com',
                'apiAccessToken': 'TestAlexaApiAccessToken1'
            }
        },
        'request': {
            'type': 'PlaybackController.PauseCommandIssued',
            'requestId': 'TestAlexaRequestId2',
            'timestamp': '2018-09-20T00:08:02Z',
            'locale': 'en-US',
            'token': token,
            'offsetInMilliseconds': 0
        },
    }
    return request_body_1 if is_cold_start else request_body_2


def request_body_creator(is_cold_start, request_type):
    request_body_1 = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'TestAlexaSessionId1',
            'application': {
                'applicationId': 'TestAlexaUserId1'
            },
            'user': {
                'userId': 'TestAlexaUserId1'
            }
        },
        'context': {
            'AudioPlayer': {
                'playerActivity': 'IDLE'
            },
            'System': {
                'application': {
                    'applicationId': 'TestAlexaUserId1'
                },
                'user': {
                    'userId': 'TestAlexaUserId1'
                },
                'device': {
                    'deviceId': 'TestAlexaDeviceId1',
                    'supportedInterfaces': {
                        'AudioPlayer': {

                        }
                    }
                },
                'apiEndpoint': 'https://api.amazonalexa.com',
                'apiAccessToken': 'TestAlexaApiAccessToken1'
            }
        },
        'request': {
            'type': request_type,
            'requestId': 'TestAlexaRequestId1',
            'timestamp': '2018-09-19T00:50:17Z',
            'locale': 'en-US',
            'shouldLinkResultBeReturned': False,
        }
    }
    request_body_2 = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'TestAlexaSessionId2',
            'application': {
                'applicationId': 'TestAlexaUserId2'
            },
            'user': {
                'userId': 'TestAlexaUserId2'
            }
        },
        'context': {
            'AudioPlayer': {
                'playerActivity': 'IDLE'
            },
            'System': {
                'application': {
                    'applicationId': 'TestAlexaUserId2'
                },
                'user': {
                    'userId': 'TestAlexaUserId2'
                },
                'device': {
                    'deviceId': 'TestAlexaDeviceId2',
                    'supportedInterfaces': {
                        'AudioPlayer': {

                        }
                    }
                },
                'apiEndpoint': 'https://api.amazonalexa.com',
                'apiAccessToken': 'TestAlexaApiAccessToken1'
            }
        },
        'request': {
            'type': request_type,
            'requestId': 'TestAlexaRequestId1',
            'timestamp': '2018-09-19T00:50:17Z',
            'locale': 'en-US',
            'shouldLinkResultBeReturned': False,
        }
    }
    return request_body_1 if is_cold_start else request_body_2
