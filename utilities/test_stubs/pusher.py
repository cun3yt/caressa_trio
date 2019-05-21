from utilities.logger import log


class Pusher:
    def __init__(self, *args, **kwargs):
        log("Pusher stub is initialized")

    def trigger(self, channels, event, data):
        log("Test Stub Pusher::trigger is called with channels: {}, event: {}, data: {}".format(channels, event, data))
