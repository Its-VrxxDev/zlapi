from zlapi import ZaloAPI
from zlapi.models import *


class InfoBot(ZaloAPI):
    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        self.markAsDelivered(mid, message_object.cliMsgId, author_id, thread_id, thread_type, message_object.msgType)
        self.markAsRead(mid, message_object.cliMsgId, author_id, thread_id, thread_type, message_object.msgType)
        
        # If message not is str, set message to [not a message]
        if not isinstance(message, str):
            message = "[not a message]"
        
        # If message is /info, fetch user information
        if message == "/info":
            user_info = self.fetchUserInfo(author_id)
            self.send(Message(text=str(user_info)), thread_id=thread_id, thread_type=thread_type)


client = InfoBot('</>', '</>', imei="<imei>", session_cookies="<session_cookies>")
client.listen()