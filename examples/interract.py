from zlapi import ZaloAPI
from zlapi.models import *

client = ZaloAPI('</>', '</>', imei="<imei>", session_cookies="<session_cookies>")

thread_id = "1234567890"
thread_type = ThreadType.GROUP

# Will send a message to the thread
client.send(Message(text="<message>"), thread_id=thread_id, thread_type=thread_type)

# Will send a message with reply to the thread
client.replyMessage(Message(text="<reply message>"), "<msg object to reply>", thread_id=thread_id, thread_type=thread_type)

# Will send a message with a mention
client.send(
    Message(
        text="This is a @mention", mention=Mention("<User ID>", length=8, offset=10)
    ),
    thread_id=thread_id,
    thread_type=thread_type,
)

# Will send a message with a multi mentions
mention1 = Mention("<User ID 1>", length=9, offset=10, auto_format=False)
mention2 = Mention("<User ID 2>", length=9, offset=21, auto_format=False)
mention3 = Mention("<User ID 3>", length=9, offset=31, auto_format=False)
mention = MultiMention([mention1, mention2, mention3])
client.send(
    Message(
        text="This is a @mention1, @mention2, @mention3", mention=mention)
    ),
    thread_id=thread_id,
    thread_type=thread_type,
)

# Will send a message with a style
# Bold Style
client.send(
    Message(
        text="This is a bold message", style=MessageStyle(style="bold", length=22)
    ),
    thread_id=thread_id,
    thread_type=thread_type,
)

# Font Style
client.send(
    Message(
        text="This is a big message", style=MessageStyle(style="font", size="50", length=21)
    ),
    thread_id=thread_id,
    thread_type=thread_type,
)

# Color Style
client.send(
    Message(
        text="This is a red message", style=MessageStyle(style="color", color="ff0000", length=21)
    ),
    thread_id=thread_id,
    thread_type=thread_type,
)

# Will send a message with a multi styles
bold = MessageStyle(style="bold", length=4, offset=0, auto_format=False)
italic = MessageStyle(style="italic", length=6, offset=5, auto_format=False)
underline = MessageStyle(style="underline", length=9, offset=12, auto_format=False)
strike = MessageStyle(style="strike", length=6, offset=22, auto_format=False)
color = MessageStyle(style="color", color="#ff0000", length=5, offset=29, auto_format=False)
bigfont = MessageStyle(style="font", size="50", length=3, offset=35, auto_format=False)
smallfont = MessageStyle(style="font", size="10", length=5, offset=39, auto_format=False)
style = MultiMsgStyle([bold, italic, underline, strike, color, bigfont, smallfont])
client.send(
    Message(
        text="Bold Italic Underline Strike Color Big Small - This is a message with all styles", style=style)
    ),
    thread_id=thread_id,
    thread_type=thread_type,
)


# Will send the image located at `<image path>`
client.sendLocalImage(
    "<image path>",
    message=Message(text="This is a local image"),
    thread_id=thread_id,
    thread_type=thread_type,
)


# Only do these actions if the thread is a group
if thread_type == ThreadType.GROUP:
    # Will remove the user with ID `<user id>` from the thread
    client.kickUsersFromGroup("<user id>", thread_id=thread_id)

    # Will add the user with ID `<user id>` to the thread
    client.addUsersToGroup("<user id>", thread_id=thread_id)

    # Will add the users with IDs `<1st user id>`, `<2nd user id>` and `<3th user id>` to the thread
    client.addUsersToGroup(
        ["<1st user id>", "<2nd user id>", "<3rd user id>"], thread_id=thread_id
    )


# Will set the typing status of the thread
client.setTypingStatus(
    thread_id=thread_id, thread_type=thread_type
)