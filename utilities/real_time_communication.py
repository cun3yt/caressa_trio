from caressa.settings import pusher_client
from utilities.logger import log


def send_instance_message(channel, event_name, data):
    log("Sending realtime message, channel: {channel}\n "
        "event_name: {event_name},\n "
        "data: {data}".format(channel=channel, event_name=event_name, data=data))
    pusher_client.trigger(channel, event_name, data)
