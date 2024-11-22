# -*- coding: UTF-8 -*-
import attr
import random
import requests, json

from . import _util, _exception

headers = {
	"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
	"Accept": "application/json, text/plain, */*",
	"sec-ch-ua": "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
	"sec-ch-ua-mobile": "?0",
	"sec-ch-ua-platform": "\"Linux\"",
	"origin": "https://chat.zalo.me",
	"sec-fetch-site": "same-site",
	"sec-fetch-mode": "cors",
	"sec-fetch-dest": "empty",
	"Accept-Encoding": "gzip",
	"referer": "https://chat.zalo.me/",
	"accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
}
class State(object):
	def __init__(cls):
		cls._config = {}
		cls._headers = _util.HEADERS
		cls._cookies = _util.COOKIES
		cls._session = requests.Session()
		cls.cloud_id = None
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
				url = f"https://wpa.chat.zalo.me/api/login/getLoginInfo?imei={imei}&type=30&client_version=645&computer_name=Web&ts={_util.now()}"
				response = requests.get(url, headers=headers, cookies=cls._cookies)
				data = response.json()
				zpw = data["data"]["zpw_ws"]
				uid = data["data"]["uid"]
				phone = data["data"]["phone_number"]
				key = data["data"]["zpw_enk"]
				
				content = {
					"data": {
						"phone_number": str(phone),
						"secret_key": str(key),
						"send2me_id": str(uid),
						"zpw_ws": zpw,
					},
				"error_code": 0
				}
				
				if content.get("error_code") == 0:
					cls._config = content.get("data")
					
					if cls._config.get("secret_key"):
						cls._loggedin = True
						cls.cloud_id = cls._config.get("send2me_id")
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
		
	
