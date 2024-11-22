# -*- coding: UTF-8 -*-
import attr
import random
import asyncio
import aiohttp

from .. import _util, _exception

class State(object):
	def __init__(cls):
		cls._config = {}
		cls._headers = _util.HEADERS
		cls._cookies = _util.COOKIES
		cls.cloud_id = None
		cls.user_imei = None
		cls._loggedin = False
	
	def is_logged_in(cls):
		return cls._loggedin
	
	def set_cookies(cls, cookies):
		cls._cookies = cookies
	
	def set_secret_key(cls, secret_key):
		cls._config["secret_key"] = secret_key
	
	async def get_cookies(cls):
		return cls._cookies
	
	async def get_secret_key(cls):
		return cls._config.get("secret_key")
	
	async def _get(cls, *args, **kwargs):
		async with aiohttp.ClientSession() as session:
			async with session.get(*args, **kwargs, headers=cls._headers, cookies=cls._cookies) as response:
				return await response.json(content_type=None)
		
	async def _post(cls, *args, **kwargs):
		async with aiohttp.ClientSession() as session:
			async with session.post(*args, **kwargs, headers=cls._headers, cookies=cls._cookies) as response:
				return await response.json(content_type=None)
	
	async def login(cls, phone, password, imei, session_cookies=None, user_agent=None):
		if cls._cookies and cls._config.get("secret_key"):
			cls._loggedin = True
			return
			
		if user_agent:
			cls._headers["User-Agent"] = user_agent
			
		if cls._cookies:
			params = {
				"zpw_ver": 647,
				"type": 30,
				"imei": imei,
				"computer_name": "Web",
				"ts": _util.now(),
				"nretry": 0
			}
			try:
				data = await cls._get("https://wpa.chat.zalo.me/api/login/getLoginInfo", params=params)
				
				if data.get("error_code") == 0:
					cls._config = data.get("data")
					
					if cls._config.get("zpw_enk"):
						cls.user_imei = imei
						cls.user_id = cls._config.get("send2me_id")
						cls._config["secret_key"] = cls._config.get("zpw_enk")
						
					else:
						cls._loggedin = False
						raise _exception.ZaloLoginError("Unable to get `secret key`.")
						
				else:
					error = data.get("error_code")
					content = data.get("error_message")
					raise _exception.ZaloLoginError(f"Error #{error} when logging in: {content}")
			
			except _exception.ZaloLoginError as e:
				raise _exception.ZaloLoginError(str(e))
				
			except Exception as e:
				raise _exception.ZaloLoginError(f"An error occurred while logging in! {str(e)}")
		
		else:
			raise _exception.LoginMethodNotSupport("Login method is not supported yet")
		
	
