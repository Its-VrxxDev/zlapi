``zlapi`` - Zalo API (Website) for Python
===========================================

.. image:: https://badgen.net/pypi/v/zlapi
    :target: https://pypi.python.org/pypi/zlapi
    :alt: Project version

.. image:: https://badgen.net/badge/python/>= 3.,pypy?list=|
    :target: zlapi
    :alt: Supported python versions: >= 3. and pypy

.. image:: https://badgen.net/pypi/license/zlapi
    :target: https://github.com/Its-VrxxDev/zlapi/tree/master/LICENSE
    :alt: License: MIT License

.. image:: https://readthedocs.org/projects/zlapi/badge/?version=stable
    :target: https://vrxx1337.dev/zlapi/docs/lastest
    :alt: Documentation


A powerful and efficient library to interact with Zalo Website. 
This is *not* an official API, Zalo has that `over here <https://developers.zalo.me/docs>`__ for chat bots. This library differs by using a normal Zalo account instead (More flexible).

``zlapi`` currently support:

- Custom style for message.
- Sending many types of messages, with files, stickers, mentions, etc.
- Fetching messages, threads and users info.
- Creating groups, setting the group, creating polls, etc.
- Listening for, an reacting to messages and other events in real-time.
- And there are many other things.
- ``async``/``await`` (Coming Soon).

Essentially, everything you need to make an amazing Zalo Bot!


Caveats
-------

``zlapi`` works by imitating what the browser does, and thereby tricking Zalo into thinking it's accessing the website normally.

However, there's a catch! **Using this library may not comply with Zalo's Terms Of Service!**, so be We are not responsible if your account gets banned or disabled!

.. inclusion-marker-intro-end
.. This message doesn't make sense in the docs at Read The Docs, so we exclude it

With that out of the way, you may go to `Docs <https://vrxx1337.dev/zlapi/docs/lastest/>`__ to see the full documentation!

.. inclusion-marker-installation-start


Installation
------------

.. code:: bash

    pip install zlapi

If you don't have `pip <https://pip.pypa.io/>`_, `this guide <http://docs.python-guide.org/en/latest/starting/installation/>`_ can guide you through the process.

You can also install directly from source, provided you have ``pip>=19.0``:

.. code:: bash

    pip install git+https://github.com/Its-VrxxDev/zlapi.git

.. inclusion-marker-installation-end


Example Usage
-------------

.. code:: py

    from zlapi import ZaloAPI
    from zlapi.models import *
    
    imei = "<imei>"
    cookies = "<cookies>"
    client = ZaloAPI("<phone>", "<password>", imei=imei, session_cookies=cookies)
    client.send(Message(text="Hi Myself!"), thread_id=client.uid, thread_type=ThreadType.USER)

More examples are available `here <https://github.com/Its-VrxxDev/zlapi/tree/main/examples>`__.

This project is a relocation
============================

This project is a project to be relocated from ``zaloapi`` because this module has been removed from Pypi and the reason is unknown.


Contact
-------

.. |teleicon| image:: https://upload.wikimedia.org/wikipedia/commons/8/83/Telegram_2019_Logo.svg
  :alt: Telegram Icon
  :width: 20px
  :height: 15px

.. |faceicon| image:: https://raw.githubusercontent.com/dheereshagrwal/colored-icons/master/public/logos/facebook/facebook.svg
  :alt: Facebook Icon
  :width: 20px
  :height: 15px

- |teleicon| Telegram: `Vexx <https://t.me/vrxx1337>`__
- |faceicon| Facebook: `Lê Quốc Việt <https://www.facebook.com/profile.php?id=100094031375075>`__


Acknowledgments
---------------

This project was originally inspired by `fbchat <https://github.com/fbchat-dev/fbchat>`__.
