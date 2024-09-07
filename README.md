![Logo](https://i.imgur.com/CMnA5Sh.jpeg "Logo")

## ``zlapi`` - Zalo API (Unofficial) for Python

[![Project version](https://img.shields.io/badge/pypi-v1.0.2-blue.svg "Project version")](https://pypi.org/project/zlapi/1.0.2)
[![Supported python versions: >= 3. and pypy](https://badgen.net/badge/python/>=3.,pypy?list=| "Supported python versions: >= 3. and pypy")](zlapi)
[![License: MIT License](https://img.shields.io/badge/license-MIT-lightgreen.svg "License: MIT License")](https://github.com/Its-VrxxDev/zlapi/blob/master/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-stop_updating-red.svg "Documentation")](https://vrxx1337.vercel.app/zlapi/docs/lastest)

### Language

- Sẽ hỗ trợ tài liệu Tiếng Việt sớm nhất có thể. Sài tạm google dịch nhé :)

### What is ``zlapi``?

A powerful and efficient library to interact with Zalo Website. 
This is *not* an official API, Zalo has that [over here](https://developers.zalo.me/docs) for chat bots. This library differs by using a normal Zalo account instead (More flexible).

``zlapi`` currently support:

- Custom style for message.
- Sending many types of messages, with files, stickers, mentions, etc.
- Fetching messages, threads and users info.
- Creating groups, setting the group, creating polls, etc.
- Listening for, an reacting to messages and other events in real-time.
- And there are many other things.
- ``async``/``await`` (Updated).

Essentially, everything you need to make an amazing Zalo Bot!


### Caveats

``zlapi`` works by imitating what the browser does, and thereby tricking Zalo into thinking it's accessing the website normally.

However, there's a catch! **Using this library may not comply with Zalo's Terms Of Service**, so be! We are not responsible if your account gets banned or disabled!


### What's New?

This is an updated version for ``zlapi`` to improve features and fix bugs (v1.0.2)

**Improvements**

- Various typo fixes and doc improvements.
- Add simple code style for module. Like ``telebot``, ``discord``, ...
- Add ``async``/``await`` for module.
- Add ``websocket`` type to listen function.
- Add ``run forever`` for listen function.
- Add send ``gif``, ``video``, ``voice``, ``business card``, ``multi image``.
- Add ``Block/Unblock`` members when kicked out of group.
- Add ``Pin/Unpin`` message in group.
- Add ``On Event`` function to handle group and user events.
- Add ``Parse Mode`` for [Message](#messages).

**Bugfixes**

- Fixed bug of the ``replyMessage`` function, only replying to normal messages.

- Fixed payload in function ``addUsersToGroup``.

</br>

## Installation

```bash
pip install zlapi
```

If you don't have [pip](https://pip.pypa.io/), [this guide](http://docs.python-guide.org/en/latest/starting/installation/) can guide you through the process.

You can also install directly from source, provided you have ``pip>=19.0``:

```bash
pip install git+https://github.com/Its-VrxxDev/zlapi.git
```

</br>

## How to get IMEI and Cookies?

### Download Extension

- [Click Here](https://drive.google.com/file/d/18_-8ruYOVa89JkHdr3muGj3kGWxwt6mc/view?usp=drive_link) to download the extension support getting IMEI & Cookies more conveniently.

### Extension Usage Tutorial

1. Enable the extension downloaded above.
2. Go to [https://chat.zalo.me](https://chat.zalo.me), Sign in to your account.
3. After successfully logging in, go back to extension and get IMEI, Cookies.

> [!TIP]
If you have opened the website ``chat.zalo.me`` but the extension does not have IMEI & Cookies, please click ``Refresh Page``.

#### Windows

[![](https://previews.jumpshare.com/thumb/815bc01b796dd6f1733c957c5af19493968eb06ccf48b6a5036cf7916c0a83965899fb056fe88c29f2bcb2f9f0f5ed5832801eede43aa22e94d5c7bc545ef9448bfbfd14044e807555841b406fdf069aa3acda441ff8675390fa0ff601ff0bcd)](https://jumpshare.com/embed/8SjFyd3EQlCMx1V7N1UQ)

</br>

#### Android

> - Use ``kiwibrowser`` instead of ``chrome`` to be able to use the extension.
> - If you are redirect when accessing ``https://chat.zalo.me``. [Watch this video](https://jumpshare.com/embed/l3LLjAWSAR8KQxvh9dzz)

[![](https://previews.jumpshare.com/thumb/815bc01b796dd6f1733c957c5af194938966297dbb29c75d038ac93e0691be4c741e5e2cbb689c41b8dfebde4ded3316844e23ec82425f377c248f1a57861470e76e9fe268bdf0803c7c14a61c9dc50769f92efb3803e5ae68c46d260d3407db)](https://jumpshare.com/embed/n56jtVQ7pwZDfR5ZtPft)

</br>

## Basic Usage

### Login Account Using Cookies

* ``Normal``/``Async`` code style

```py
# > Normal
# from zlapi import ZaloAPI

# > Async
# from zlapi.Async import ZaloAPI

from zlapi import ZaloAPI
from zlapi.models import *

imei = "<imei>"
cookies = {} # Cookies Dict
bot = ZaloAPI("<phone>", "<password>", imei=imei, session_cookies=cookies)
```

</br>

* ``Simple`` code style

```py
from zlapi.simple import ZaloAPI
from zlapi.models import *

imei = "<imei>"
cookies = {} # Cookies Dict
bot = ZaloAPI("</>", "</>", imei, cookies, prefix="<your bot prefix>")
```

</br>

### Listen Message, Event, ...

* You can enable thread mode for [On Message](#on-message) function (work with ``requests`` type) with ``thread=True``.

```py
bot.listen(thread=True)
```

* You can change the listen mode with ``type="<listen type>"``. Current module support ``websocket``, ``requests`` type (default type is **websocket**)

```py
bot.listen(type="<listen type>")
```

* If you don't want to have to rerun the bot script when something goes wrong in the **listen** function you can use ``run_forever=True``.

```py
bot.listen(run_forever=True)
```

</br>

* ``Normal``/``Async`` code style

```py
# > Normal
# from zlapi import ZaloAPI

# > Async
# from zlapi.Async import ZaloAPI

from zlapi import ZaloAPI
from zlapi.models import *

imei = "<imei>"
cookies = {} # Cookies Dict

bot = ZaloAPI("<phone>", "<password>", imei=imei, session_cookies=cookies)
# bot.listen(type="...")
bot.listen()
```

</br>

* ``Simple`` code style

```py
from zlapi.simple import ZaloAPI
from zlapi.models import *

imei = "<imei>"
cookies = {} # Cookies Dict

bot = ZaloAPI("</>", "</>", imei, cookies, prefix="<your bot prefix>")
bot.listen()
```

</br>

### Custom On Message Function

``onMessage`` function will be called when receiving a message from ``listen`` function. **So we can handle that message here.**

* ``Normal`` code style

```py
from zlapi import ZaloAPI
from zlapi.models import *

imei = "<imei>"
cookies = {} # Cookies Dict

class CustomBot(ZaloAPI):
    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        # Handle Message Here
        pass


bot = CustomBot("<phone>", "<password>", imei=imei, session_cookies=cookies)
bot.listen()
```

</br>

* ``Async`` code style

```py
from zlapi.Async import ZaloAPI
from zlapi.models import *

imei = "<imei>"
cookies = {} # Cookies Dict

class CustomBot(ZaloAPI):
    async def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        # Handle Message Here
        pass


bot = CustomBot("<phone>", "<password>", imei=imei, session_cookies=cookies)
bot.listen()
```

</br>

* ``Simple`` code style

```py
from zlapi.simple import ZaloAPI
from zlapi.models import *

imei = "<imei>"
cookies = {} # Cookies Dict
bot = ZaloAPI("</>", "</>", imei, cookies, prefix="<bot prefix>")


@bot.event
async def on_message(ctx):
    # Handle Message Here
    pass


bot.listen()
```

</br>

### Example Handle Message

<details>
<summary><b><i>Normal</b> code style</i></summary>

```py
from zlapi import ZaloAPI
from zlapi.models import *

imei = "<imei>"
cookies = {} # Cookies Dict

class CustomBot(ZaloAPI):
    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        if not isinstance(message, str):
            return

        if message == ".hi":
            print(f"{author_id} sent message .hi")


bot = CustomBot("<phone>", "<password>", imei=imei, session_cookies=cookies)
bot.listen()
```

> - If the message is not ``string`` do not process this message.
> - If the message is ``.hi`` will print author id of message to terminal.

</br>

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

```py
from zlapi.Async import ZaloAPI
from zlapi.models import *

imei = "<imei>"
cookies = {} # Cookies Dict

class CustomBot(ZaloAPI):
    async def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        if not isinstance(message, str):
            return

        if message == ".hi":
            print(f"{author_id} sent message .hi")


bot = CustomBot("<phone>", "<password>", imei=imei, session_cookies=cookies)
bot.listen()
```

> - If the message is not ``string`` do not process this message.
> - If the message is ``.hi`` will print author id of message to terminal.

</br>

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Method 1

  ```py
  from zlapi.simple import ZaloAPI
  from zlapi.models import *

  imei = "<imei>"
  cookies = {} # Cookies Dict
  bot = ZaloAPI("</>", "</>", imei, cookies, prefix="<bot prefix>")

  
  @bot.event
  async def on_message(ctx):
      if ctx.message == ".hi":
          print(f"{ctx.author_id} sent message .hi")


  bot.listen()
  ```

</br>

- Method 2

  ```py
  from zlapi.simple import ZaloAPI
  from zlapi.models import *

  imei = "<imei>"
  cookies = {} # Cookies Dict
  bot = ZaloAPI("</>", "</>", imei, cookies, prefix=".")


  @bot.register_handler(commands=["hi"])
  async def handle_hi(ctx):
      print(f"{ctx.author_id} sent message .hi")

  
  bot.listen()
  ```
  
  > - ``@bot.register_handler(commands=["hi"])`` is a decoration class used to register a command. When an incoming message matches the bot prefix + registered commands, the message will be processed.

</details>

</br>

<!-- fetchAccountInfo -->

### Fetch Account Information

This function will get the account information you are using in ``zlapi``.

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.fetchAccountInfo()
  ```

</br>

- Inside Module Function

  ```py
  self.fetchAccountInfo()
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.fetchAccountInfo())
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.fetchAccountInfo()
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.fetch_account_info())
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.fetch_account_info()
  ```

</details>

<!-- END FetchAccountInfo -->

</br>

<!-- fetchPhoneNumber -->

### Fetch Phone Number

This function will get user information using that user phone number.

> [!NOTE]
Can't get information of **hidden phone number** or **locked account**

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.fetchPhoneNumber("<phone number>")
  ```

</br>

- Inside Module Function

  ```py
  self.fetchPhoneNumber("<phone number>")
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.fetchPhoneNumber("<phone number>"))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.fetchPhoneNumber("<phone number>")
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.fetch_phone_number("<phone number>"))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.fetch_phone_number("<phone number>")
  ```

</details>

<!-- END FetchPhoneNumber -->

</br>

<!-- fetchUserInfo -->

### Fetch User Info

This function will get user information using that user ID.

> - In ``Normal``/``Async`` code style you can get user id with author_id argument
> - In ``Simple`` code style you can get user id with ctx.author_id argument
> - Or you can use user id if you already have one

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.fetchUserInfo(<user id>)
  ```

</br>

- Inside Module Function

  ```py
  self.fetchUserInfo(<user id>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.fetchUserInfo(<user id>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.fetchUserInfo(<user id>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.fetch_user_info(<user id>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.fetch_user_info(<user id>)
  ```

</details>

<!-- END FetchUserInfo -->

</br>

<!-- fetchGroupInfo -->

### Fetch Group Info

This function will get group information using that group ID.

> - In ``Normal``/``Async`` code style you can get user id with thread_id argument
> - In ``Simple`` code style you can get user id with ctx.thread_id argument
> - Or you can use group id if you already have one

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.fetchGroupInfo(<group id>)
  ```

</br>

- Inside Module Function

  ```py
  self.fetchGroupInfo(<group id>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.fetchGroupInfo(<group id>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.fetchGroupInfo(<group id>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.fetch_group_info(<group id>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.fetch_group_info(<user id>)
  ```

</details>

<!-- END FetchGroupInfo -->

</br>

<!-- fetchAllFriends -->

### Fetch All Friends

This function will get all the friends information of the account currently using the ``zlapi``.

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.fetchAllFriends()
  ```

</br>

- Inside Module Function

  ```py
  self.fetchAllFriends()
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.fetchAllFriends())
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.fetchAllFriends()
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.fetch_all_friends())
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.fetch_all_friends()
  ```

</details>

<!-- END FetchAllFriends -->

</br>

<!-- fetchAllGroups -->

### Fetch All Groups

This function will get all the groups id of the account currently using the ``zlapi``.

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.fetchAllGroups()
  ```

</br>

- Inside Module Function

  ```py
  self.fetchAllGroups()
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.fetchAllGroups())
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.fetchAllGroups()
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.fetch_all_groups())
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.fetch_all_groups()
  ```

</details>

<!-- END FetchAllGroups -->

</br>

<!-- changeAccountSetting -->

### Change Account Setting

This function will change setting of the account currently using the ``zlapi``.

> - Args:
>    - name (str): The new account name
>    - dob (str): Date of birth wants to change (format: year-month-day)
>    - gender (int | str): Gender wants to change (0 = Male, 1 = Female)

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.changeAccountSetting(<name>, <dob>, <gender>)
  ```

</br>

- Inside Module Function

  ```py
  self.changeAccountSetting(<name>, <dob>, <gender>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.changeAccountSetting(<name>, <dob>, <gender>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.changeAccountSetting(<name>, <dob>, <gender>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.change_account_setting(<name>, <dob>, <gender>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.change_account_setting(<name>, <dob>, <gender>)
  ```

</details>

<!-- END changeAccountSetting -->

</br>

<!-- changeAccountAvatar -->

### Change Account Avatar

This function will upload/change avatar of the account currently using the ``zlapi``.

> - Args:
>    - filePath (str): A path to the image to upload/change avatar
>    - size (int): Avatar image size (default = auto)
>	- width (int): Width of avatar image
>	- height (int): height of avatar image
>	- language (int | str): Zalo Website language ? (idk)

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.changeAccountAvatar(<filePath>)
  ```

</br>

- Inside Module Function

  ```py
  self.changeAccountAvatar(<filePath>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.changeAccountAvatar(<filePath>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.changeAccountAvatar(<filePath>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.change_account_avatar(<filePath>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.change_account_avatar(<filePath>)
  ```

</details>

<!-- END changeAccountAvatar -->

</br>

<!-- sendFriendRequest -->

### Send Friend Request

This function will send friend request to a user by ID.

> - Args:
>	- userId (int | str): User ID to send friend request
>	- msg (str): Friend request message
>	- language (str): Response language or Zalo interface language

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendFriendRequest(<userId>, <msg>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendFriendRequest(<userId>, <msg>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendFriendRequest(<userId>, <msg>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendFriendRequest(<userId>, <msg>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_friend_request(<userId>, <msg>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_friend_request(<userId>, <msg>)
  ```

</details>

<!-- END sendFriendRequest -->

</br>

<!-- acceptFriendRequest -->

### Accept Friend Request

This function will accept friend request from user by ID.

> - Args:
>	- userId (int | str): User ID to accept friend request
>	- language (str): Response language or Zalo interface language

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.acceptFriendRequest(<userId>)
  ```

</br>

- Inside Module Function

  ```py
  self.acceptFriendRequest(<userId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.acceptFriendRequest(<userId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.acceptFriendRequest(<userId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.accept_friend_request(<userId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.accept_friend_request(<userId>)
  ```

</details>

<!-- END acceptFriendRequest -->

</br>

<!-- blockViewFeed -->

### Block View Feed

This function will Block/Unblock friend view feed by ID.

> - Args:
>	- userId (int | str): User ID to block/unblock view feed
>	- isBlockFeed (int): Block/Unblock friend view feed (1 = True | 0 = False)

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.blockViewFeed(<userId>, <isBlockFeed>)
  ```

</br>

- Inside Module Function

  ```py
  self.blockViewFeed(<userId>, <isBlockFeed>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.blockViewFeed(<userId>, <isBlockFeed>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.blockViewFeed(<userId>, <isBlockFeed>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.block_view_feed(<userId>, <isBlockFeed>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.block_view_feed(<userId>, <isBlockFeed>)
  ```

</details>

<!-- END blockViewFeed -->

</br>

<!-- blockUser -->

### Block User

This function will block user by ID.

> - Args:
>	- userId (int | str): User ID to block

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.blockUser(<userId>)
  ```

</br>

- Inside Module Function

  ```py
  self.blockUser(<userId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.blockUser(<userId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.blockUser(<userId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.block_user(<userId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.block_user(<userId>)
  ```

</details>

<!-- END blockUser -->

</br>

<!-- unblockUser -->

### Unblock User

This function will unblock user by ID.

> - Args:
>	- userId (int | str): User ID to unblock

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.unblockUser(<userId>)
  ```

</br>

- Inside Module Function

  ```py
  self.unblockUser(<userId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.unblockUser(<userId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.unblockUser(<userId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.unblock_user(<userId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.unblock_user(<userId>)
  ```

</details>

<!-- END unblockUser -->

</br>

<!-- createGroup -->

### Create Group

This function will Create a new group.

> - Args:
>	- name (str): The new group name
>	- description (str): Description of the new group
>	- members (str | list): List/String member IDs add to new group
>	- nameChanged (int - auto): Will use default name if disabled (0), else (1)
>	- createLink (int - default): Create a group link? Default = 1 (True)
			

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.createGroup(<name>, <description>, <members>)
  ```

</br>

- Inside Module Function

  ```py
  self.createGroup(<name>, <description>, <members>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.createGroup(<name>, <description>, <members>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.createGroup(<name>, <description>, <members>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.create_group(<name>, <description>, <members>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.create_group(<name>, <description>, <members>)
  ```

</details>

<!-- END createGroup -->

</br>

<!-- changeGroupAvatar -->

### Change Group Avatar

This function will Upload/Change group avatar by ID.

> - Args:
>	- filePath (str): A path to the image to upload/change avatar
>	- groupId (int | str): Group ID to upload/change avatar

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.changeGroupAvatar(<filePath>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.changeGroupAvatar(<filePath>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.changeGroupAvatar(<filePath>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.changeGroupAvatar(<filePath>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.change_group_avatar(<filePath>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.change_group_avatar(<filePath>, <groupId>)
  ```

</details>

> [!NOTE]
Client must be the Owner of the group
(If the group does not allow members to upload/change)

<!-- END changeGroupAvatar -->

</br>

<!-- changeGroupName -->

### Change Group Name

This function will Set/Change group name by ID.

> - Args:
>	- groupName (str): Group name to change
>	- groupId (int | str): Group ID to change name

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.changeGroupName(<groupName>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.changeGroupName(<groupName>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.changeGroupName(<groupName>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.changeGroupName(<groupName>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.change_group_name(<groupName>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.change_group_name(<groupName>, <groupId>)
  ```

</details>

> [!NOTE]
Client must be the Owner of the group
(If the group does not allow members to upload/change)

<!-- END changeGroupName -->

</br>

<!-- changeGroupSetting -->

### Change Group Setting

This function will Update group settings by ID.

> - Args:
>	- groupId (int | str): Group ID to update settings
>	- defaultMode (str): Default mode of settings
>			
>		- default: Group default settings
>		- anti-raid: Group default settings for anti-raid
>			
>	- **kwargs: Group settings kwargs, Value: (1 = True, 0 = False)
>			
>		- blockName: Không cho phép user đổi tên & ảnh đại diện nhóm
>		- signAdminMsg: Đánh dấu tin nhắn từ chủ/phó nhóm
>		- addMemberOnly: Chỉ thêm members (Khi tắt link tham gia nhóm)
>		- setTopicOnly: Cho phép members ghim (tin nhắn, ghi chú, bình chọn)
>		- enableMsgHistory: Cho phép new members đọc tin nhắn gần nhất
>		- lockCreatePost: Không cho phép members tạo ghi chú, nhắc hẹn
>		- lockCreatePoll: Không cho phép members tạo bình chọn
>		- joinAppr: Chế độ phê duyệt thành viên
>		- bannFeature: Default (No description)
>		- dirtyMedia: Default (No description)
>		- banDuration: Default (No description)
>		- lockSendMsg: Không cho phép members gửi tin nhắn
>		- lockViewMember: Không cho phép members xem thành viên nhóm
>		- blocked_members: Danh sách members bị chặn

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.changeGroupSetting(<groupId>, **kwargs)
  ```

</br>

- Inside Module Function

  ```py
  self.changeGroupSetting(<groupId>, **kwargs)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.changeGroupSetting(<groupId>, **kwargs))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.changeGroupSetting(<groupId>, **kwargs)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.change_group_setting(<groupId>, **kwargs))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.change_group_setting(<groupId>, **kwargs)
  ```

</details>

> [!WARNING]
Other settings will default value if not set. See `defaultMode`

<!-- END changeGroupSetting -->

</br>

<!-- changeGroupOwner -->

### Change Group Owner

This function will Change group owner by ID.

> - Args:
>	- newAdminId (int | str): members ID to changer owner
>	- groupId (int | str): ID of the group to changer owner

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.changeGroupOwner(<newAdminId>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.changeGroupOwner(<newAdminId>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.changeGroupOwner(<newAdminId>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.changeGroupOwner(<newAdminId>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.change_group_owner(<newAdminId>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.change_group_owner(<newAdminId>, <groupId>)
  ```

</details>

> [!NOTE]
Client must be the Owner of the group.

<!-- END changeGroupOwner -->

</br>

<!-- addUsersToGroup -->

### Add Users To Group

This function will Add friends/users to a group.

> - Args:
>	- user_ids (str | list): One or more friend/user IDs to add
>	- groupId (int | str): Group ID to add friend/user to

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.addUsersToGroup(<user_ids>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.addUsersToGroup(<user_ids>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.addUsersToGroup(<user_ids>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.addUsersToGroup(<user_ids>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.add_users_to_group(<user_ids>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.add_users_to_group(<user_ids>, <groupId>)
  ```

</details>

<!-- END addUsersToGroup -->

</br>

<!-- kickUsersInGroup -->

### Kick Users In Group

This function will Kickout members in group by ID.

> - Args:
>	- members (str | list): One or More member IDs to kickout
>	- groupId (int | str): Group ID to kick member from

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.kickUsersInGroup(<members>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.kickUsersInGroup(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.kickUsersInGroup(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.kickUsersInGroup(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.kick_users_in_group(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.kick_users_in_group(<members>, <groupId>)
  ```

</details>

> [!NOTE]
Client must be the Owner of the group.

<!-- END kickUsersInGroup -->

</br>

<!-- blockUsersInGroup -->

### Block Users In Group

This function will Blocked members in group by ID.

> - Args:
>	- members (str | list): One or More member IDs to block
>	- groupId (int | str): Group ID to block member from

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.blockUsersInGroup(<members>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.blockUsersInGroup(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.blockUsersInGroup(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.blockUsersInGroup(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.block_users_in_group(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.block_users_in_group(<members>, <groupId>)
  ```

</details>

> [!NOTE]
Client must be the Owner of the group.

<!-- END blockUsersInGroup -->

</br>

<!-- unblockUsersInGroup -->

### Unblock Users In Group

This function will Unblock members in group by ID.

> - Args:
>	- members (str | list): One or More member IDs to unblock
>	- groupId (int | str): Group ID to unblock member from

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.unblockUsersInGroup(<members>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.unblockUsersInGroup(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.unblockUsersInGroup(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.unblockUsersInGroup(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.unblock_users_in_group(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.unblock_users_in_group(<members>, <groupId>)
  ```

</details>

> [!NOTE]
Client must be the Owner of the group.

<!-- END unblockUsersInGroup -->

</br>

<!-- addGroupAdmins -->

### Add Group Admins

This function will Add admins to the group by ID.

> - Args:
>	- members (str | list): One or More member IDs to add
>	- groupId (int | str): Group ID to add admins

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.addGroupAdmins(<members>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.addGroupAdmins(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.addGroupAdmins(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.addGroupAdmins(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.add_group_admins(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.add_group_admins(<members>, <groupId>)
  ```

</details>

> [!NOTE]
Client must be the Owner of the group.

<!-- END addGroupAdmins -->

</br>

<!-- removeGroupAdmins -->

### Remove Group Admins

This function will Remove admins in the group by ID.

> - Args:
>	- members (str | list): One or More admin IDs to remove
>	- groupId (int | str): Group ID to remove admins

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.removeGroupAdmins(<members>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.removeGroupAdmins(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.removeGroupAdmins(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.removeGroupAdmins(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.remove_group_admins(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.remove_group_admins(<members>, <groupId>)
  ```

</details>

> [!NOTE]
Client must be the Owner of the group.

<!-- END removeGroupAdmins -->

</br>

<!-- pinGroupMsg -->

### Pin Group Message

This function will Pin message in group by ID.

> - Args:
>	- pinMsg (Message): Message Object to pin
>	- groupId (int | str): Group ID to pin message

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.pinGroupMsg(<pinMsg>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.pinGroupMsg(<pinMsg>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.pinGroupMsg(<pinMsg>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.pinGroupMsg(<pinMsg>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.pin_group_msg(<pinMsg>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.pin_group_msg(<pinMsg>, <groupId>)
  ```

</details>

<!-- END pinGroupMsg -->

</br>

<!-- unpinGroupMsg -->

### Unpin Group Message

This function will Unpin message in group by ID.

> - Args:
>	- pinId (int | str): Pin ID to unpin
>	- pinTime (int): Pin start time
>	- groupId (int | str): Group ID to unpin message

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.unpinGroupMsg(<pinId>, <pinTime>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.unpinGroupMsg(<pinId>, <pinTime>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.unpinGroupMsg(<pinId>, <pinTime>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.unpinGroupMsg(<pinId>, <pinTime>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.unpin_group_msg(<pinId>, <pinTime>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.unpin_group_msg(<pinId>, <pinTime>, <groupId>)
  ```

</details>

<!-- END unpinGroupMsg -->

</br>

<!-- deleteGroupMsg -->

### Delete Group Message

This function will Delete message in group by ID.

> - Args:
>	- msgId (int | str): Message ID to delete
>	- ownerId (int | str): Owner ID of the message to delete
>	- clientMsgId (int | str): Client message ID to delete message
>	- groupId (int | str): Group ID to delete message

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.deleteGroupMsg(<msgId>, <onwerId>, <clientMsgId>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.deleteGroupMsg(<msgId>, <onwerId>, <clientMsgId>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.deleteGroupMsg(<msgId>, <onwerId>, <clientMsgId>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.deleteGroupMsg(<msgId>, <onwerId>, <clientMsgId>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.delete_group_msg(<msgId>, <onwerId>, <clientMsgId>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.delete_group_msg(<msgId>, <onwerId>, <clientMsgId>, <groupId>)
  ```

</details>

<!-- END deleteGroupMsg -->

</br>

<!-- viewGroupPending -->

### View Group Pending

This function will Give list of people pending approval in group by ID.

> - Args:
>	- groupId (int | str): Group ID to view pending members

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.viewGroupPending(<groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.viewGroupPending(<groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.viewGroupPending(<groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.viewGroupPending(<groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.view_group_pending(<groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.view_group_pending(<groupId>)
  ```

</details>

<!-- END viewGroupPending -->

</br>

<!-- handleGroupPending -->

### Handle Group Pending

This function will Approve/Deny pending users to the group from the group's approval.

> - Args:
>	- members (str | list): One or More member IDs to handle
>	- groupId (int | str): ID of the group to handle pending members
>	- isApprove (bool): Approve/Reject pending members (True | False)

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.handleGroupPending(<members>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.handleGroupPending(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.handleGroupPending(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.handleGroupPending(<members>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.handle_group_pending(<members>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.handle_group_pending(<members>, <groupId>)
  ```

</details>

<!-- END handleGroupPending -->

</br>

<!-- viewPollDetail -->

### View Poll Detail

This function will Give poll data by ID.

> - Args:
>	- pollId (int | str): Poll ID to view detail

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.viewPollDetail(<pollId>)
  ```

</br>

- Inside Module Function

  ```py
  self.viewPollDetail(<pollId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.viewPollDetail(<pollId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.viewPollDetail(<pollId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.view_poll_detail(<pollId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.view_poll_detail(<pollId>)
  ```

</details>

<!-- END viewPollDetail -->

</br>

<!-- createPoll -->

### Create Poll

This function will Create poll in group by ID.

> - Args:
>	- question (str): Question for poll
>	- options (str | list): List options for poll
>	- groupId (int | str): Group ID to create poll from
>	- expiredTime (int): Poll expiration time (0 = no expiration)
>	- pinAct (bool): Pin action (pin poll)
>	- multiChoices (bool): Allows multiple poll choices
>	- allowAddNewOption (bool): Allow members to add new options
>	- hideVotePreview (bool): Hide voting results when haven't voted
>	- isAnonymous (bool): Hide poll voters
			

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.createPoll(<question>, <options>, <groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.createPoll(<question>, <options>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.createPoll(<question>, <options>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.createPoll(<question>, <options>, <groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.create_poll(<question>, <options>, <groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.create_poll(<question>, <options>, <groupId>)
  ```

</details>

<!-- END createPoll -->

</br>

<!-- lockPoll -->

### Lock Poll

This function will Lock/end poll by ID.

> - Args:
>	- pollId (int | str): Poll ID to lock

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.lockPoll(<pollId>)
  ```

</br>

- Inside Module Function

  ```py
  self.lockPoll(<pollId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.lockPoll(<pollId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.lockPoll(<pollId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.lock_poll(<pollId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.lock_poll(<pollId>)
  ```

</details>

<!-- END lockPoll -->

</br>

<!-- disperseGroup -->

### Disperse Group

This function will Disperse group by ID.

> - Args:
>	- groupId (int | str): Group ID to disperse

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.disperseGroup(<groupId>)
  ```

</br>

- Inside Module Function

  ```py
  self.disperseGroup(<groupId>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.disperseGroup(<groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.disperseGroup(<groupId>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.disperse_group(<groupId>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.disperse_group(<groupId>)
  ```

</details>

<!-- END disperseGroup -->

</br>

<!-- send/sendMessage -->

### Send Message

This function will Send message to a thread (user/group).

> - Args:
>	- message (Message): ``Message`` Object to send
>	- thread_id (int | str): User/Group ID to send to
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- mark_message (str): Send messages as `Urgent` or `Important` mark

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function
  
  ```py
  bot.send(<message>, <thread_id>, <thread_type>)
  ```
  
  or
  
  ```py
  bot.sendMessage(<message>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.send(<message>, <thread_id>, <thread_type>)
  ```
  
  or
  
  ```py
  self.sendMessage(<message>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.send(<message>, <thread_id>, <thread_type>))
  ```
  
  or
  
  ```py
  asyncio.run(bot.sendMessage(<message>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.send(<message>, <thread_id>, <thread_type>)
  ```
  
  or
  
  ```py
  await self.sendMessage(<message>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send(<message>, <thread_id>, <thread_type>))
  ```
  
  or
  
  ```py
  asyncio.run(bot.send_message(<message>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send(<message>, <thread_id>, <thread_type>)
  ```
  
  or
  
  ```py
  await bot.send_message(<message>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END send/sendMessage -->

</br>

<!-- replyMessage -->

### Reply Message

This function will Reply message in thread (user/group).

> - Args:
>	- message (Message): ``Message Object`` to send
>	- replyMsg (Message): ``Message Object`` to reply
>	- thread_id (int | str): User/Group ID to send to.
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.replyMessage(<message>, <replyMsg>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.replyMessage(<message>, <replyMsg>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.replyMessage(<message>, <replyMsg>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.replyMessage(<message>, <replyMsg>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.reply_message(<message>, <replyMsg>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.reply_message(<message>, <replyMsg>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END replyMessage -->

</br>

<!-- undoMessage -->

### Undo Message

This function will Undo message from the client (self) by ID.

> - Args:
>	- msgId (int | str): Message ID to undo
>	- cliMsgId (int | str): Client Msg ID to undo
>	- thread_id (int | str): User/Group ID to undo message
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
			
<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.undoMessage(<msgId>, <cliMsgId>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.undoMessage(<msgId>, <cliMsgId>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.undoMessage(<msgId>, <cliMsgId>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.undoMessage(<msgId>, <cliMsgId>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.undo_message(<msgId>, <cliMsgId>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.undo_message(<msgId>, <cliMsgId>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END undoMessage -->

</br>

<!-- sendReaction -->

### Send Reaction

This function will Reaction message in thread (user/group) by ID.

> - Args:
>	- messageObject (Message): ``Message Object`` to reaction
>	- reactionIcon (str): Icon/Text to reaction
>	- thread_id (int | str): Group/User ID contain message to reaction
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendReaction(<messageObject>, <reactionIcon>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendReaction(<messageObject>, <reactionIcon>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendReaction(<messageObject>, <reactionIcon>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendReaction(<messageObject>, <reactionIcon>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_reaction(<messageObject>, <reactionIcon>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_reaction(<messageObject>, <reactionIcon>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendReaction -->

</br>

<!-- sendMultiReaction -->

### Send Multiple Reactions

This function will Reaction multi message in thread (user/group) by ID.

> - Args:
>	- reactionObj (MessageReaction): Message(s) data to reaction
>	- reactionIcon (str): Icon/Text to reaction
>	- thread_id (int | str): Group/User ID contain message to reaction
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendMultiReaction(<reactionObj>, <reactionIcon>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendMultiReaction(<reactionObj>, <reactionIcon>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendMultiReaction(<reactionObj>, <reactionIcon>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendMultiReaction(<reactionObj>, <reactionIcon>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_multi_reaction(<reactionObj>, <reactionIcon>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_multi_reaction(<reactionObj>, <reactionIcon>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendMultiReaction -->

</br>

<!-- sendRemoteFile -->

### Send Remote File

This function will Send File to a User/Group with url.

> - Args:
>	- fileUrl (str): File url to send
>	- thread_id (int | str): User/Group ID to send to.
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- fileName (str): File name to send
>	- fileSize (int): File size to send
>	- extension (str): type of file to send (py, txt, mp4, ...)

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendRemoteFile(<fileUrl>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendRemoteFile(<fileUrl>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendRemoteFile(<fileUrl>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendRemoteFile(<fileUrl>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_remote_file(<fileUrl>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_remote_file(<fileUrl>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendRemoteFile -->

</br>

<!-- sendRemoteVideo -->

### Send Remote Video

This function will Send video to a User/Group with url.

> - Args:
>	- videoUrl (str): Video link to send
>	- thumbnailUrl (str): Thumbnail link for video
>	- duration (int | str): Time for video (ms)
>	- thread_id (int | str): User/Group ID to send to.
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- width (int): Width of the video
>	- height (int): Height of the video
>	- message (Message): ``Message Object`` to send with video

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendRemoteVideo(<videoUrl>, <thumbnailUrl>, <duration>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendRemoteVideo(<videoUrl>, <thumbnailUrl>, <duration>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendRemoteVideo(<videoUrl>, <thumbnailUrl>, <duration>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendRemoteVideo(<videoUrl>, <thumbnailUrl>, <duration>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_remote_video(<videoUrl>, <thumbnailUrl>, <duration>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_remote_video(<videoUrl>, <thumbnailUrl>, <duration>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendRemoteVideo -->

</br>

<!-- sendRemoteVoice -->

### Send Remote Voice

This function will Send voice to a User/Group with url.

> - Args:
>	- voiceUrl (str): Voice link to send
>	- thread_id (int | str): User/Group ID to change status in
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- fileSize (int | str): Voice content length (size) to send

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendRemoteVoice(<voiceUrl>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendRemoteVoice(<voiceUrl>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendRemoteVoice(<voiceUrl>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendRemoteVoice(<voiceUrl>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_remote_voice(<voiceUrl>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_remote_voice(<voiceUrl>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendRemoteVoice -->

</br>

<!-- sendLocalImage -->

### Send Local Image

This function will Send Image to a User/Group with local file.

> - Args:
>	- imagePath (str): Image directory to send
>	- thread_id (int | str): User/Group ID to send to.
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- width (int): Image width to send
>	- height (int): Image height to send
>	- message (Message): ``Message Object`` to send with image

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendLocalImage(<imagePath>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendLocalImage(<imagePath>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendLocalImage(<imagePath>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendLocalImage(<imagePath>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_local_image(<imagePath>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_local_image(<imagePath>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendLocalImage -->

</br>

<!-- sendMultiLocalImage -->

### Send Multiple Local Image

This function will Send Multiple Image to a User/Group with local file.

> - Args:
>	- imagePathList (list): List image directory to send
>	- thread_id (int | str): User/Group ID to send to.
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- width (int): Image width to send
>	- height (int): Image height to send
>	- message (Message): ``Message Object`` to send with image

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendMultiLocalImage(<imagePathList>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendMultiLocalImage(<imagePathList>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendMultiLocalImage(<imagePathList>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendMultiLocalImage(<imagePathList>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_multi_local_image(<imagePathList>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_multi_local_image(<imagePathList>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendMultiLocalImage -->

</br>

<!-- sendLocalGif -->

### Send Local Gif

This function will Send Gif to a User/Group with local file.

> - Args:
>	- gifPath (str): Gif path to send
>	- thumbnailUrl (str): Thumbnail of gif to send
>	- thread_id (int | str): User/Group ID to send to.
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- gifName (str): Gif name to send
>	- width (int): Gif width to send
>	- height (int): Gif height to send

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendLocalGif(<gifPath>, <thumbnailUrl>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendLocalGif(<gifPath>, <thumbnailUrl>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendLocalGif(<gifPath>, <thumbnailUrl>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendLocalGif(<gifPath>, <thumbnailUrl>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_local_gif(<gifPath>, <thumbnailUrl>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_local_gif(<gifPath>, <thumbnailUrl>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendLocalGif -->

</br>

<!-- sendSticker -->

### Send Sticker

This function will Send Sticker to a User/Group.

> - Args:
>	- stickerType (int | str): Sticker type to send
>	- stickerId (int | str): Sticker id to send
>	- cateId (int | str): Sticker category id to send
>	- thread_id (int | str): User/Group ID to send to.
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendSticker(<stickerType>, <stickerId>, <cateId>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendSticker(<stickerType>, <stickerId>, <cateId>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendSticker(<stickerType>, <stickerId>, <cateId>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendSticker(<stickerType>, <stickerId>, <cateId>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_sticker(<stickerType>, <stickerId>, <cateId>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_sticker(<stickerType>, <stickerId>, <cateId>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendSticker -->

</br>

<!-- sendCustomSticker -->

### Send Custom Sticker

This function will Send custom (static/animation) sticker to a User/Group with url.

> - Args:
>	- staticImgUrl (str): Image url (png, jpg, jpeg) format to create sticker
>	- animationImgUrl (str): Static/Animation image url (webp) format to create sticker
>	- thread_id (int | str): User/Group ID to send sticker to.
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- reply (int | str): Message ID to send stickers with quote
>	- width (int | str): Width of photo/sticker
>	- height (int | str): Height of photo/sticker

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendCustomSticker(<staticImgUrl>, <animationImgUrl>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendCustomSticker(<staticImgUrl>, <animationImgUrl>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendCustomSticker(<staticImgUrl>, <animationImgUrl>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendCustomSticker(<staticImgUrl>, <animationImgUrl>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_custom_sticker(<staticImgUrl>, <animationImgUrl>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_custom_sticker(<staticImgUrl>, <animationImgUrl>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendCustomSticker -->

</br>

<!-- sendLink -->

### Send Link

This function will Send link to a User/Group with url.

> - Args:
>	- linkUrl (str): Link url to send
>	- title (str): Title for card to send
>	- thread_id (int | str): User/Group ID to send link to
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- thumbnailUrl (str): Thumbnail link url for card to send
>	- domainUrl (str): Main domain of Link to send (eg: github.com)
>	- desc (str): Description for card to send
>	- message (Message): ``Message Object`` to send with the link

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendLink(<linkUrl>, <title>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendLink(<linkUrl>, <title>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendLink(<linkUrl>, <title>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendLink(<linkUrl>, <title>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_link(<linkUrl>, <title>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_link(<linkUrl>, <title>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendLink -->

</br>

<!-- sendReport -->

### Send Report

This function will Send report to Zalo.

> - Args:
>	- thread_id (int | str): User/Group ID to report
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- reason (int): Reason for reporting
>			
>		- 1 = Nội dung nhạy cảm
>		- 2 = Làm phiền
>		- 3 = Lừa đảo
>		- 0 = custom
>			
>	- content (str): Report content (work if reason = custom)

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendReport(<thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendReport(<thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendReport(<thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendReport(<thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_report(<thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_report(<thread_id>, <thread_type>)
  ```

</details>

<!-- END sendReport -->

</br>

<!-- sendBusinessCard -->

### Send Business Card

This function will Send business card to thread (user/group) by user ID.

> - Args:
>	- userId (int | str): Business card user ID
>	- qrCodeUrl (str): QR Code link with business card profile information
>	- thread_id (int | str): User/Group ID to change status in
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``
>	- phone (int | str): Send business card with phone number

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.sendBusinessCard(<userId>, <qrCodeUrl>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.sendBusinessCard(<userId>, <qrCodeUrl>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.sendBusinessCard(<userId>, <qrCodeUrl>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.sendBusinessCard(<userId>, <qrCodeUrl>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.send_business_card(<userId>, <qrCodeUrl>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.send_business_card(<userId>, <qrCodeUrl>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END sendBusinessCard -->

</br>

<!-- setTypingStatus -->

### Set Typing Status

This function will Set users typing status.

> - Args:
>	- thread_id: User/Group ID to change status in.
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.setTyping(<thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.setTyping(<thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.setTyping(<thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.setTyping(<thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.set_typing(<thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.set_typing(<thread_id>, <thread_type>)
  ```

</details>

<!-- END setTypingStatus -->

</br>

<!-- markAsDelivered -->

### Mark Message As Delivered

This function will Mark a message as delivered.

> - Args:
>	- msgId (int | str): Message ID to set as delivered
>	- cliMsgId (int | str): Client message ID
>	- senderId (int | str): Message sender Id
>	- thread_id (int | str): User/Group ID to mark as delivered
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.markAsDelivered(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.markAsDelivered(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.markAsDelivered(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.markAsDelivered(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.mark_as_delivered(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.mark_as_delivered(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END markAsDelivered -->

</br>

<!-- markAsRead -->

### Mark Message As Read

This function will Mark a message as read.

> - Args:
>	- msgId (int | str): Message ID to set as delivered
>	- cliMsgId (int | str): Client message ID
>	- senderId (int | str): Message sender Id
>	- thread_id (int | str): User/Group ID to mark as read
>	- thread_type (ThreadType): ``ThreadType.USER``, ``ThreadType.GROUP``

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Outside Module Function

  ```py
  bot.markAsRead(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>)
  ```

</br>

- Inside Module Function

  ```py
  self.markAsRead(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Outside Module Function

  ```py
  asyncio.run(bot.markAsRead(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await self.markAsRead(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>)
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

- Outside Module Function
  
  ```py
  asyncio.run(bot.mark_as_read(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>))
  ```

</br>

- Inside Module Function (You can use ``await`` instead.)

  ```py
  await bot.mark_as_read(<msgId>, <cliMsgId>, <senderId>, <thread_id>, <thread_type>)
  ```

</details>

<!-- END markAsRead -->

</br>

<!-- listen -->

### Listen

This function will Initialize and runs the listening loop continually.

> - Args:
>	- delay (int): Delay time for each message fetch for ``requests`` type (Default: 1)
>	- thread (bool): Handle messages within the thread for ``requests`` type (Default: False)
>	- type (str): Type of listening (Default: websocket)
>	- reconnect (int): Delay interval when reconnecting

- Use Outside Of Function

```py
bot.listen()
```

<!-- END listen -->

</br>

<!-- onListening -->

### On Listening

This function is called when the client is listening.

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Inside Module Custom Class

  ```py
  def onListening(self):
      ....
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Inside Module Custom Class

  ```py
  async def onListening(self):
      ....
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>


- Outside Module Class

  ```py
  @bot.event
  async def on_listening():
      ....
  ```

</details>

<!-- END onListening -->

</br>

<!-- onMessage -->

### On Message

This function is called when the client is listening, and somebody sends a message.

> - Args:
>	- mid: The message ID
>	- author_id: The ID of the author
>	- message: The message content of the author
>	- message_object: The message (As a `Message` object)
>	- thread_id: Thread ID that the message was sent to.
>	- thread_type (ThreadType): Type of thread that the message was sent to.

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Inside Module Custom Class

  ```py
  def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
      ....
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Inside Module Custom Class

  ```py
  async def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
      ....
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

> - In simple type, all event or register_handler functions use args with context.
>
> - Args Context Example:
>    - ctx.message_id
>    - ctx.author_id
>    - ctx.message
>    - ctx.message_object
>    - ctx.thread_id
>    - ctx.thread_type

- Outside Module Class

  ```py
  @bot.event
  async def on_message(ctx):
      ....
  ```

</details>

<!-- END onMessage -->

</br>

<!-- onEvent -->

### On Event

This function is called when the client listening, and some events occurred.

> - Args:
>	- event_data (EventObject): Event data (As a `EventObject` object)
>	- event_type (EventType/GroupEventType): Event Type

<details>
<summary><b><i>Normal</b> code style</i></summary>

- Inside Module Custom Class

  ```py
  def onEvent(self, event_data, event_type):
      ....
  ```

</details>

<details>
<summary><b><i>Async</b> code style</i></summary>

- Inside Module Custom Class

  ```py
  async def onEvent(self, event_data, event_type):
      ....
  ```

</details>

<details>
<summary><b><i>Simple</b> code style</i></summary>

> - In simple type, all event or register_handler functions use args with context.
>
> - Args Context Example:
>    - ctx.event_data
>    - ctx.event_type

- Outside Module Class

  ```py
  @bot.event
  async def on_event(ctx):
      ....
  ```

</details>

<!-- END onEvent -->

</br>

<!-- Messages -->

### Messages

Represents a Zalo message.

> - Args:
>    - text (str): The actual message
>    - style (MessageStyle/MultiMsgStyle): A ``MessageStyle`` or ``MultiMsgStyle`` objects
>    - mention (Mention/MultiMention): A ``Mention`` or ``MultiMention`` objects
>    - parse_mode (str): Format messages in ``Markdown``, ``HTML`` style

```py
Message(text=<text>, mention=<mention>, style=<style>)
```

<!-- END Messages -->

</br>

<!-- MessageStyle -->

### Message Style

Style for message.

> - Args:
>    - offset (int): The starting position of the style. Defaults to 0.
>    - length (int): The length of the style. Defaults to 1.
>    - style (str): The type of style. Can be "font", "bold", "italic", "underline", "strike", or "color". Defaults to "font".
>    - color (str): The color of the style in hexadecimal format (e.g. "ffffff"). Only applicable when style is "color". Defaults to "ffffff".
>    - size (int | str): The font size of the style. Only applicable when style is "font". Defaults to "18".
>    - auto_format (bool): If there are multiple styles (used in ``MultiMsgStyle``) then set it to False. Default is True (1 style)

- Example

  - **bold** style with offset is 5, length is 10.
  
  ```py
  style = MessageStyle(offset=5, length=10, style="bold")
  ...
  ```
  
  </br>
  
  - color style with offset is 10, length is 5 and color="![#ff0000](https://placehold.co/20x15/ff0000/ff0000.png) `#ff0000`"
  
  ```py
  style = MessageStyle(offset=10, ``length=5``, style="color", color="ff0000")
  ...
  ```
  
  </br>
  
  - font style with offset is 15, length is 8 and size="24" (Customize font size to 24)
  
  ```py
  style = MessageStyle(offset=15, length=8, style="font", size="24")
  ...
  ```

<!-- END MessageStyle -->

</br>

<!-- MultiMsgStyle -->

### Multiple Message Style

Multiple style for message.

> - Args:
>    - listStyle (MessageStyle): A list of ``MessageStyle`` objects to be combined into a single style format.

```py
style = MultiMsgStyle([
    MessageStyle(offset=<text>, length=<mention>, style=<style>, color=<color>, size=<size>, auto_format=False),
    MessageStyle(offset=<text>, length=<mention>, style=<style>, color=<color>, size=<size>, auto_format=False),
    ...
])
```

<!-- END MultiMsgStyle -->

</br>

<!-- Mention -->

### Mention

Represents a @mention.

> - Args:
>    - uid (str): The user ID to be mentioned.
>    - length (int): The length of the mention. Defaults to 1.
>    - offset (int): The starting position of the mention. Defaults to 0.
>    - auto_format (bool): If there are multiple mention (used in ``MultiMention``) then set it to False. Default is True (1 mention).

```py
mention = Mention(uid=<uid>, length=<length>, offset=<offset>)
...
```

</br>

- Mention user id *1234567890* with offset is 10 and length is 5.

```py
mention = Mention("1234567890", length=5, offset=10)
...
```

<!-- END Mention -->

</br>

<!-- MultiMention -->

### Multiple Mention

Represents multiple @mentions.

> - Args:
>    - listMention (Mention): A list of ``Mention`` objects to be combined into a single mention format.

```py
mention = MultiMention([
    Mention(uid=<uid>, length=<length>, offset=<offset>, auto_format=False),
    Mention(uid=<uid>, length=<length>, offset=<offset>, auto_format=False),
    ...
])
```

</br>

- Mention user id *1234567890* with offset is 10 and length is 5.
- Mention user id *9876543210* with offset is 20 and length is 3.

```py
mention1 = Mention("1234567890", length=5, offset=10)
mention2 = Mention("9876543210", length=3, offset=20)
mention = MultiMention([mention1, mention2])
```

<!-- END MultiMention -->

</br>

## Example

See [examples](examples) folder to learn more about ``zlapi``.

</br>

## Acknowledgments

- This project was originally inspired by [fbchat](https://github.com/fbchat-dev/fbchat).
- listen ``websocket`` type taken from [zca-js](https://github.com/RFS-ADRENO/zca-js).

- Thanks for support:
  - [Crow](https://t.me/crowmatacc) for Hosting.
  - [Duy Hoang](https://t.me/Tcp_API) for the Video Tutorial.
  - [Nguyen Hong Anh Duc](https://t.me/ducknha) for the Example.
  - [Khang Phan](https://www.facebook.com/khang.phan27.info) for help fix the ``listen`` function error.

## Contact For Help

- <img src="https://upload.wikimedia.org/wikipedia/commons/8/83/Telegram_2019_Logo.svg" alt="Telegram Icon" width=20 height=15/> Telegram: [Vexx](https://t.me/vrxx1337)
- <img src="https://raw.githubusercontent.com/dheereshagrwal/colored-icons/master/public/logos/facebook/facebook.svg" alt="Facebook Icon" width=20 height=15/> Facebook: [Lê Quốc Việt](https://www.facebook.com/profile.php?id=100094031375075)
