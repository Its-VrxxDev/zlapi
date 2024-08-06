from zlapi import ZaloAPI
from zlapi.models import *

client = ZaloAPI('</>', '</>', imei="<imei>", session_cookies="<session_cookies>")

print("Own id: {}".format(client.uid))

client.send(Message(text="Hello myself"), thread_id=client.uid, thread_type=ThreadType.USER)