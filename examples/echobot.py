from zlapi import ZaloAPI
from zlapi.models import *

# Subclass zlapi.ZaloAPI and override required methods
class EchoBot(ZaloAPI):
    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        self.markAsDelivered(mid, message_object.cliMsgId, author_id, thread_id, thread_type, message_object.msgType)
        self.markAsRead(mid, message_object.cliMsgId, author_id, thread_id, thread_type, message_object.msgType)
        
        # If message not is str, set message to [not a message]
        if not isinstance(message, str):
            message = "[not a message]"
        
        # If you're not the author, echo
        if author_id != self._uid:
            self.send(Message(text=message), thread_id=thread_id, thread_type=thread_type)


client = EchoBot('</>', '</>', imei="<imei>", session_cookies="<session_cookies>")
client.listen()
