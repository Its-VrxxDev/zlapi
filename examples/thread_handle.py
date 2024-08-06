from zlapi import ZaloAPI
from zlapi.models import *
from concurrent.futures import ThreadPoolExecutor

thread = ThreadPoolExecutor(max_workers=99999)

class FastHandleBot(ZaloAPI):
    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        thread.submit(
            self.onHandle, mid, author_id, message, message_object, thread_id, thread_type
        )

    def onHandle(self, mid, author_id, message, message_object, thread_id, thread_type):
        self.markAsDelivered(mid, message_object.cliMsgId, author_id, thread_id, thread_type, message_object.msgType)
        self.markAsRead(mid, message_object.cliMsgId, author_id, thread_id, thread_type, message_object.msgType)
        
        # If message not is str, set message to [not a message]
        if not isinstance(message, str):
            message = "[not a message]"
        
        if message == "/start":
            mention = Mention(author_id, length=7, offset=3)
            self.send(
                Message(
                    text="Hi @Member, Have a good day 💙.", mention=mention
                ),
                thread_id=thread_id,
                thread_type=thread_type
            )
        elif message == "/reply":
            self.replyMessage(
                Message(
                    text="This is reply message!"
                ),
                message_object,
                thread_id=thread_id,
                thread_type=thread_type
            )
        elif message[:5] == "/info":
            phoneNumber = message.replace("/info", "").strip()
            phoneNumberData = self.fetchPhoneNumber(phoneNumber)
            self.send(Message(text=str(phoneNumberData)), thread_id=thread_id, thread_type=thread_type)


client = FastHandleBot('</>', '</>', imei="<imei>", session_cookies="<session_cookies>")
client.listen()