# -*- coding: UTF-8 -*-

import os
import json
import time
import threading

from .models import *
from . import _util, _state
from concurrent.futures import ThreadPoolExecutor

thread = ThreadPoolExecutor(max_workers=9999)

class ZaloAPI(object):
	def __init__(self, phone, password, imei, session_cookies=None, user_agent=None, auto_login=True):
		"""Initialize and log in the client.
		
		Args:
			imei (str): The device imei is logged into Zalo
			phone (str): Zalo account phone number
			password (str): Zalo account password
			auto_login (bool): Automatically log in when initializing ZaloAPI (Default: True)
			user_agent (str): Custom user agent to use when sending requests. If `None`, user agent will be chosen from a premade list
			session_cookies (dict): Cookies from a previous session (Required if logging in with cookies)
			
		Raises:
			ZaloLoginError: On failed login
			LoginMethodNotSupport: If method login not support
		"""
		self._state = _state.State()
		self._condition = threading.Event()
		self._undefined = object()
		self._listening = False
		
		if auto_login:
			if (
				not session_cookies 
				or not self.setSession(session_cookies) 
				or not self.isLoggedIn()
			):
				self.login(phone, password, imei, user_agent)
		
	
	def uid(self):
		"""The ID of the client."""
		return self.uid
	
	"""
	INTERNAL REQUEST METHODS
	"""
	
	def _get(self, *args, **kwargs):
		return self._state._get(*args, **kwargs)
		
	def _post(self, *args, **kwargs):
		return self._state._post(*args, **kwargs)
	
	"""
	END INTERNAL REQUEST METHODS
	"""
	
	"""
	EXTENSIONS METHODS
	"""
	
	def _encode(self, params):
		return _util.zalo_encode(params, self._state._config.get("secret_key"))
		
	def _decode(self, params):
		return _util.zalo_decode(params, self._state._config.get("secret_key")) 
		
	"""
	END EXTENSIONS METHODS
	"""
	
	"""
	LOGIN METHODS
	"""
	
	def isLoggedIn(self):
		"""Get data from config to check the login status.

		Returns:
			bool: True if the client is still logged in
		"""
		return self._state.is_logged_in()
		
	def getSession(self):
		"""Retrieve session cookies.
			
		Returns:
			dict: A dictionary containing session cookies
		"""
		return self._state.get_cookies()
		
	def setSession(self, session_cookies):
		"""Load session cookies.
		
		Warning:
			Error sending requests if session cookie is wrong
			
		Args:
			session_cookies (dict): A dictionary containing session cookies
			
		Returns:
			Bool: False if ``session_cookies`` does not contain proper cookies
		"""
		try:
			if not isinstance(session_cookies, dict):
				return False
			# Load cookies into current session
			self._state.set_cookies(session_cookies)
			self.uid = self._state.user_id
		except Exception as e:
			print("Failed loading session")
			return False
		return True
	
	def getSecretKey(self):
		"""Retrieve secret key to encode/decode payload.
			
		Returns:
			str: A secret key string with base64 encode
		"""
		return self._state.get_secret_key()
		
	def setSecretKey(self, secret_key):
		"""Load secret key.
		
		Warning:
			Error (enc/de)code payload if secret key is wrong
			
		Args:
			secret_key (str): A secret key string with base64 encode
			
		Returns:
			bool: False if ``secret_key`` not correct to (en/de)code the payload
		"""
		try:
			self._state.set_secret_key(secret_key)
			
			return True
		except:
			return False
	
	def login(self, phone, password, imei, user_agent=None):
		"""Login the user, using ``phone`` and ``password``.
			
		If the user is already logged in, this will do a re-login.
				
		Args:
			imei (str): The device imei is logged into Zalo
			phone (str): Zalo account phone number
			password (str): Zalo account password
			user_agent (str): Custom user agent to use when sending requests. If `None`, user agent will be chosen from a premade list
			
		Raises:
			ZaloLoginError: On failed login
			LoginMethodNotSupport: If method login not support
		"""
		if not (phone and password):
			raise ZaloUserError("Phone and password not set")
		
		self.onLoggingIn()
		
		self._state.login(
			phone,
			password,
			imei,
			user_agent=user_agent
		)
		try:
			self._imei = self._state.user_imei
			self.uid = self.fetchAccountInfo().profile.get("userId", self._state.user_id)
		except:
			self._imei = None
			self.uid = self._state.user_id
		
		self.onLoggedIn(self._state._config.get("phone_number"))
		
	"""
	END LOGIN METHODS
	"""
	
	"""
	ATTACHMENTS METHODS
	"""
	
	def _uploadImage(self, filePath, thread_id, thread_type):
		"""Upload images to Zalo.
			
		Args:
			filePath (str): Image url to send
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			dict: A dictionary containing the image info just uploaded
			dict: A dictionary containing error_code, response if failed
			
		Raises:
			ZaloAPIException: If request failed
		"""
		if not os.path.exists(filePath):
			raise ZaloUserError(f"{filePath} not found")
			
		files = [("chunkContent", open(filePath, "rb"))]
		fileSize = len(open(filePath, "rb").read())
		fileName = filePath if "/" not in filePath else filePath.rstrip("/")[1]
		
		params = {
			"params": {
				"totalChunk": 1,
				"fileName": fileName,
				"clientId": _util.now(),
				"totalSize": fileSize,
				"imei": self._imei,
				"isE2EE": 0,
				"jxl": 0,
				"chunkId": 1
			},
			"zpw_ver": 634,
			"zpw_type": 30,
		}
		
		if thread_type == ThreadType.USER:
			url = "https://tt-files-wpa.chat.zalo.me/api/message/photo_original/upload"
			params["type"] = 2
			params["params"]["toid"] = str(thread_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-files-wpa.chat.zalo.me/api/group/photo_original/upload"
			params["type"] = 11
			params["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		params["params"] = self._encode(params["params"])
		
		response = self._post(url, params=params, files=files)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(data["data"])
			results = results.get("data") if results.get("error_code") == 0 else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return results
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	"""
	END ATTACHMENTS METHODS
	"""
	
	"""
	FETCH METHODS
	"""
	
	def fetchAccountInfo(self):
		"""fetch account information of the client 
		
		Returns:
			object: `User` client info
			dict: A dictionary containing error_code, response if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"params": self._encode({
				"avatar_size": 120,
				"imei": self._imei
			}),
			"zpw_ver": 634,
			"zpw_type": 30,
			"os": 8,
			"browser": 0
		}
		
		response = self._get("https://tt-profile-wpa.chat.zalo.me/api/social/profile/me-v2", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("error_code") == 0 else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return User.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def fetchPhoneNumber(self, phoneNumber, language="vi"):
		"""Fetch user info by Phone Number.
		
		Not available with hidden phone numbers
		
		Args:
			phoneNumber (int | str): Phone number to fetch information
			language (str): Language for response (not sure | Default: vi)
		
		Returns:
			object: `User` user(s) info
			dict: A dictionary containing error_code, response if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		
		phone = "84" + str(phoneNumber) if str(phoneNumber)[:1] != "0" else "84" + str(phoneNumber)[1:]
		
		params = {
			"zpw_ver": 634,
			"zpw_type": 30,
			"params": self._encode({
				"phone": phone,
				"avatar_size": 240,
				"language": language,
				"imei": self._imei,
				"reqSrc": 85
			})
		}
		
		response = self._get("https://tt-friend-wpa.chat.zalo.me/api/friend/profile/get", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return User.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	def fetchUserInfo(self, userId):
		"""Fetch user info by ID.
		
		Args:
			userId (int | str | list): User(s) ID to get info
		
		Returns:
			object: `User` user(s) info
			dict: A dictionary containing error_code, response if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"phonebook_version": int(_util.now() / 1000),
				"friend_pversion_map": [],
				"avatar_size": 120,
				"language": "vi",
				"show_online_status": 1,
				"imei": self._imei
			}
		}
		
		if isinstance(userId, list):
			for i in range(len(userId)):
				userId[i] = str(userId[i]) + "_0"
			payload["params"]["friend_pversion_map"] = userId
			
		else:
			payload["params"]["friend_pversion_map"].append(str(userId) + "_0")
			
		payload["params"] = self._encode(payload["params"])
		
		response = self._post("https://tt-profile-wpa.chat.zalo.me/api/social/friend/getprofiles/v2", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("error_code") == 0 else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return User.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def fetchGroupInfo(self, groupId):
		"""Fetch group info by ID.
		
		Args:
			groupId (int | str | dict): Group(s) ID to get info
		
		Returns:
			object: `Group` group info
			dict: A dictionary containing error_code, response if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"gridVerMap": {}
			}
		}
		
		if isinstance(groupId, dict):
			for i in groupId:
				payload["params"]["gridVerMap"][str(i)] = 0
		else:
			payload["params"]["gridVerMap"][str(groupId)] = 0
			
		payload["params"]["gridVerMap"] = json.dumps(payload["params"]["gridVerMap"])
		payload["params"] = self._encode(payload["params"])
		
		response = self._post("https://tt-group-wpa.chat.zalo.me/api/group/getmg-v2", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("error_code") == 0 else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
		
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def fetchAllFriends(self):
		"""Fetch all users the client is currently chatting with (only friends).
		
		Returns:
			object: `User` all friend IDs
			any: If response is not list friends
			
		Raises:
			ZaloAPIException: If request failed
		"""
		
		params = {
			"params": self._encode({
				"incInvalid": 0,
				"page": 1,
				"count": 20000,
				"avatar_size": 120,
				"actiontime": 0
			}),
			"zpw_ver": 634,
			"zpw_type": 30,
			"nretry": 0
		}
		
		response = self._get("https://profile-wpa.chat.zalo.me/api/social/friend/getfriends", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			datas = []
			if results.get("data"):
				for data in results.get("data"):
					datas.append(User(**data))
			
			return datas
					
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	def fetchAllGroups(self):
		"""Fetch all group IDs are joining and chatting.
		
		Returns:
			object: `Group` all group IDs
			any: If response is not all group IDs
		
		Raises:
			ZaloAPIException: If request failed
		"""
		
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._get("https://tt-group-wpa.chat.zalo.me/api/group/getlg/v4", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("error_code") == 0 else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	"""
	END FETCH METHODS
	"""
	
	"""
	GET METHODS
	"""
	
	def getLastMsgs(self):
		"""Get last message the client's friends/group chat room.
			
		Returns:
			object: `User` last msg data
			dict: A dictionary containing error_code, response if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": "634",
			"zpw_type": "30",
			"params": self._encode({
				"threadIdLocalMsgId": json.dumps({}),
				"imei": self._imei
			})
		}
		
		response = self._get("https://tt-convers-wpa.chat.zalo.me/api/preloadconvers/get-last-msgs", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("error_code") == 0 else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return User.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def getRecentGroup(self, groupId):
		"""Get recent messages in group by ID.
			
		Args:
			groupId (int | str): Group ID to get recent msgs
			
		Returns:
			object: `Group` List msg data in groupMsgs
			dict: A dictionary containing error_code, response if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"params": self._encode({
				"groupId": str(groupId),
				"globalMsgId": 10000000000000000,
				"count": 50,
				"msgIds": [],
				"imei": self._imei,
				"src": 1
			}),
			"zpw_ver": 634,
			"zpw_type": 30,
			"nretry": 0,
		}
		
		response = self._get("https://tt-group-cm.chat.zalo.me/api/cm/getrecentv2", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = json.loads(results.get("data")) if results.get("error_code") == 0 else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def _getGroupBoardList(self, board_type, page, count, last_id, last_type, groupId):
		params = {
			"params": self._encode({
				"group_id": str(groupId),
				"board_type": board_type,
				"page": page,
				"count": count,
				"last_id": last_id,
				"last_type": last_type,
				"imei": self._imei
			}),
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._get("https://groupboard-wpa.chat.zalo.me/api/board/list", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = Group(**json.loads(results.get("data"))) if results.get("error_code") == 0 else results
			
			return results
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def getGroupBoardList(self, groupId, page=1, count=20, last_id=0, last_type=0):
		"""Get group board list (pinmsg, note, poll) by ID.
			
		Args:
			groupId (int | str): Group ID to get board list
			page (int): Number of pages to retrieve data from
			count (int): Amount of data to retrieve per page (5 poll, ..)
			last_id (int): Default (no description)
			last_type (int): Default (no description)
			
		Returns:
			object: `Group` board data in group
			dict: A dictionary containing error_code, response if failed
			
		Raises:
			ZaloAPIException: If request failed
		"""
		response = self._getGroupBoardList(0, page, count, last_id, last_type, groupId)
		
		return response
	
	def getGroupPinMsg(self, groupId, page=1, count=20, last_id=0, last_type=0):
		"""Get group pinned messages by ID.
			
		Args:
			groupId (int | str): Group ID to get pinned messages
			page (int): Number of pages to retrieve data from
			count (int): Amount of data to retrieve per page (5 message, ..)
			last_id (int): Default (no description)
			last_type (int): Default (no description)
			
		Returns:
			object: `Group` pinned messages in group
			dict: A dictionary containing error_code, response if failed
			
		Raises:
			ZaloAPIException: If request failed
		"""
		response = self._getGroupBoardList(2, page, count, last_id, last_type, groupId)
		
		return response
	
	def getGroupNote(self, groupId, page=1, count=20, last_id=0, last_type=0):
		"""Get group notes by ID.
			
		Args:
			groupId (int | str): Group ID to get notes
			page (int): Number of pages to retrieve data from
			count (int): Amount of data to retrieve per page (5 notes, ..)
			last_id (int): Default (no description)
			last_type (int): Default (no description)
			
		Returns:
			object: `Group` notes in group
			dict: A dictionary containing error_code, response if failed
			
		Raises:
			ZaloAPIException: If request failed
		"""
		response = self._getGroupBoardList(1, page, count, last_id, last_type, groupId)
		
		return response
	
	def getGroupPoll(self, groupId, page=1, count=20, last_id=0, last_type=0):
		"""Get group polls by ID.
			
		Args:
			groupId (int | str): Group ID to get polls
			page (int): Number of pages to retrieve data from
			count (int): Amount of data to retrieve per page (5 poll, ..)
			last_id (int): Default (no description)
			last_type (int): Default (no description)
			
		Returns:
			object: `Group` polls in group
			dict: A dictionary containing error_code, response if failed
			
		Raises:
			ZaloAPIException: If request failed
		"""
		response = self._getGroupBoardList(3, page, count, last_id, last_type, groupId)
		
		return response
	
	"""
	END GET METHODS
	"""
	
	"""
	ACCOUNT ACTION METHODS
	"""
	
	def changeAccountSetting(self, name, dob, gender, biz={}, language="vi"):
		"""Change account information.
		
		Args:
			name (str): The new account name
			dob (str): Date of birth wants to change (format: year-month-day)
			gender (int | str): Gender wants to change (0 = Male, 1 = Female)
			biz (unknown): idk this
			language (str): Zalo language wants to change (default = vn)
		
		Returns:
			object: `User` change account setting status
			dict: A dictionary containing error_code, response if failed
			
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"profile": json.dumps({
					"name": name,
					"dob": dob,
					"gender": int(gender)
				}),
				"biz": json.dumps(biz),
				"language": language
			})
		}
		
		response = self._post("https://tt-profile-wpa.chat.zalo.me/api/social/profile/update", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return User.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def changeAccountAvatar(self, filePath, width=500, height=500, language="vn", size=None):
		"""Upload/Change account avatar.
		
		Args:
			filePath (str): A path to the image to upload/change avatar
			groupId (int | str): Group ID to upload/change avatar
			
		Returns:
			object: `User` Account avatar change status
			None: If requet success/failed depending on the case
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		if not os.path.exists(filePath):
			raise ZaloUserError(f"{filePath} not found")
		
		size = os.stat(filePath).st_size if not size else size
		files = [("fileContent", open(filePath, "rb"))]
		
		params = {
			"zpw_ver": 634,
			"zpw_type": 30,
			"params": self._encode({
				"avatarSize": 120,
				"clientId": str(self.uid) + _util.formatTime("%H:%M %d/%m/%Y"),
				"language": language,
				"metaData": json.dumps({
					"origin": {
						"width": width,
						"height": height
					},
					"processed": {
						"width": width,
						"height": height,
						"size": size
					}
				})
			})
		}
		
		response = self._post("https://tt-files-wpa.chat.zalo.me/api/profile/upavatar", params=params, files=files)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return User.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	"""
	END ACCOUNT ACTION METHODS
	"""
	
	"""
	GROUP ACTION METHODS
	"""
	
	def createGroup(self, name=None, description=None, members=[], nameChanged=1, createLink=1):
		"""Create a new group.
			
		Args:
			name (str): The new group name
			description (str): Description of the new group
			members (str | list): List/String member IDs add to new group
			nameChanged (int - auto): Will use default name if disabled (0), else (1)
			createLink (int - default): Create a group link? Default = 1 (True)
			
		Returns:
			object: `Group` new group response
			dict: A dictionary containing error_code, response if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		memberTypes = []
		nameChanged = 1 if name else 0
		name = name or "Default Group Name"
		
		if members and isinstance(members, list):
			members = [str(member) for member in members]
		else:
			members = [str(members)]
			
		if members:
			for i in members:
				memberTypes.append(-1)
			
		params = {
			"params": self._encode({
				"clientId": _util.now(),
				"gname": name,
				"gdesc": description,
				"members": members,
				"memberTypes": memberTypes,
				"nameChanged": nameChanged,
				"createLink": createLink,
				"clientLang": "vi",
				"imei": self._imei,
				"zsource": 601
			}),
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._get("https://tt-group-wpa.chat.zalo.me/api/group/create/v2", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return results
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def changeGroupAvatar(self, filePath, groupId):
		"""Upload/Change group avatar by ID.
		
		Client must be the Owner of the group
		(If the group does not allow members to upload/change)
			
		Args:
			filePath (str): A path to the image to upload/change avatar
			groupId (int | str): Group ID to upload/change avatar
			
		Returns:
			object: `Group` Group avatar change status
			None: If requet success/failed depending on the case
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		if not os.path.exists(filePath):
			raise ZaloUserError(f"{filePath} not found")
			
			
		files = [("fileContent", open(filePath, "rb"))]
		
		params = {
			"params": self._encode({
				"grid": str(groupId),
				"avatarSize": 120,
				"clientId": "g" + str(groupId) + _util.formatTime("%H:%M %d/%m/%Y"),
				"originWidth": 640,
				"originHeight": 640,
				"imei": self._imei
			}),
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._post("https://tt-files-wpa.chat.zalo.me/api/group/upavatar", params=params, files=files)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def changeGroupName(self, groupName, groupId):
		"""Set/Change group name by ID.
		
		Client must be the Owner of the group
		(If the group does not allow members to change group name)
			
		Args:
			groupName (str): Group name to change
			groupId (int | str): Group ID to change name
			
		Returns:
			object: `Group` Group name change status
			None: If requet success/failed depending on the case
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"gname": groupName,
				"grid": str(groupId)
			})
		}
		
		response = self._post("https://tt-group-wpa.chat.zalo.me/api/group/updateinfo", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def changeGroupDesc(self, groupDesc, groupId):
		"""Not Available Yet"""
	
	def changeGroupSetting(self, groupId, defaultMode="default", **kwargs):
		"""Update group settings by ID.
		
		Client must be the Owner/Admin of the group.
		
		Warning:
			Other settings will default value if not set. See `defaultMode`
		
		Args:
			groupId (int | str): Group ID to update settings
			defaultMode (str): Default mode of settings
			
				default: Group default settings
				anti-raid: Group default settings for anti-raid
			
			**kwargs: Group settings kwargs, Value: (1 = True, 0 = False)
			
				blockName: Không cho phép user đổi tên & ảnh đại diện nhóm
				signAdminMsg: Đánh dấu tin nhắn từ chủ/phó nhóm
				addMemberOnly: Chỉ thêm members (Khi tắt link tham gia nhóm)
				setTopicOnly: Cho phép members ghim (tin nhắn, ghi chú, bình chọn)
				enableMsgHistory: Cho phép new members đọc tin nhắn gần nhất
				lockCreatePost: Không cho phép members tạo ghi chú, nhắc hẹn
				lockCreatePoll: Không cho phép members tạo bình chọn
				joinAppr: Chế độ phê duyệt thành viên
				bannFeature: Default (No description)
				dirtyMedia: Default (No description)
				banDuration: Default (No description)
				lockSendMsg: Không cho phép members gửi tin nhắn
				lockViewMember: Không cho phép members xem thành viên nhóm
				blocked_members: Danh sách members bị chặn
		
		Returns:
			object: `Group` Group settings change status
			None: If requet success/failed depending on the case
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		if defaultMode == "anti-raid":
			defSetting = {
				"blockName": 1,
				"signAdminMsg": 1,
				"addMemberOnly": 0,
				"setTopicOnly": 1,
				"enableMsgHistory": 1,
				"lockCreatePost": 1,
				"lockCreatePoll": 1,
				"joinAppr": 1,
				"bannFeature": 0,
				"dirtyMedia": 0,
				"banDuration": 0,
				"lockSendMsg": 0,
				"lockViewMember": 0,
			}
		else:
			defSetting = self.fetchGroupInfo(groupId).gridInfoMap
			defSetting = defaultSettings[str(groupId)]["setting"]
			
		blockName = kwargs.get("blockName", defSetting.get("blockName", 1))
		signAdminMsg = kwargs.get("signAdminMsg", defSetting.get("signAdminMsg", 1))
		addMemberOnly = kwargs.get("addMemberOnly", defSetting.get("addMemberOnly", 0))
		setTopicOnly = kwargs.get("setTopicOnly", defSetting.get("setTopicOnly", 1))
		enableMsgHistory = kwargs.get("enableMsgHistory", defSetting.get("enableMsgHistory", 1))
		lockCreatePost = kwargs.get("lockCreatePost", defSetting.get("lockCreatePost", 1))
		lockCreatePoll = kwargs.get("lockCreatePoll", defSetting.get("lockCreatePoll", 1))
		joinAppr = kwargs.get("joinAppr", defSetting.get("joinAppr", 1))
		bannFeature = kwargs.get("bannFeature", defSetting.get("bannFeature", 0))
		dirtyMedia = kwargs.get("dirtyMedia", defSetting.get("dirtyMedia", 0))
		banDuration = kwargs.get("banDuration", defSetting.get("banDuration", 0))
		lockSendMsg = kwargs.get("lockSendMsg", defSetting.get("lockSendMsg", 0))
		lockViewMember = kwargs.get("lockViewMember", defSetting.get("lockViewMember", 0))
		blocked_members = kwargs.get("blocked_members", [])
		
		params = {
			"params": self._encode({
				"blockName": blockName,
				"signAdminMsg": signAdminMsg,
				"addMemberOnly": addMemberOnly,
				"setTopicOnly": setTopicOnly,
				"enableMsgHistory": enableMsgHistory,
				"lockCreatePost": lockCreatePost,
				"lockCreatePoll": lockCreatePoll,
				"joinAppr": joinAppr,
				"bannFeature": bannFeature,
				"dirtyMedia": dirtyMedia,
				"banDuration": banDuration,
				"lockSendMsg": lockSendMsg,
				"lockViewMember": lockViewMember,
				"blocked_members": blocked_members,
				"grid": str(groupId),
				"imei":self._imei
			}),
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._get("https://tt-group-wpa.chat.zalo.me/api/group/setting/update", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def changeGroupOwner(self, newAdminId, groupId):
		"""Change group owner (yellow key) by ID.
		
		Client must be the Owner of the group.
			
		Args:
			newAdminId (int | str): members ID to changer owner
			groupId (int | str): ID of the group to changer owner
			
		Returns:
			object: `Group` Group owner change status
			None: If requet success/failed depending on the case
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"params": self._encode({
				"grid": str(groupId),
				"newAdminId": str(newAdminId),
				"imei": self._imei,
				"language": "vi"
			}),
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._get("https://tt-group-wpa.chat.zalo.me/api/group/change-owner", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def addUsersToGroup(self, user_ids, groupId):
		"""Add friends/users to a group.
			
		Args:
			user_ids (str | list): One or more friend/user IDs to add
			groupId (int | str): Group ID to add friend/user to
		
		Returns:
			object: `Group` add friend/user data
			dict: A dictionary containing error_code, response if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		memberTypes = []
		
		if members and isinstance(members, list):
			members = [str(friend) for friend in friend_ids]
		else:
			members = [str(friend_ids)]
			
		if members:
			for i in members:
				memberTypes.append(-1)
		
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"grid": str(groupId),
				"members": members,
				"memberTypes": memberTypes,
				"imei": self._imei,
				"clientLang": "vi"
			})
		}
		
		response = self._post("https://tt-group-wpa.chat.zalo.me/api/group/invite/v2", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def kickUsersFromGroup(self, members, groupId):
		"""Kickout members in group by ID.
		
		Client must be the Owner of the group.
		
		Args:
			members (str | list): One or More member IDs to kickout
			groupId (int | str): Group ID to kick member from
			
		Returns:
			object: `Group` kick data
			dict: A dictionary/object containing error responses
			
		Raises:
			ZaloAPIException: If request failed
		"""
		if isinstance(members, list):
			members = [str(member) for member in members]
		else:
			members = [str(members)]
			
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"grid": str(groupId),
				"members": members
			})
		}
		
		response = self._post("https://tt-group-wpa.chat.zalo.me/api/group/kickout", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def addGroupAdmins(self, members, groupId):
		"""Add admins to the group (white key).
		
		Client must be the Owner of the group.
			
		Args:
			members (str | list): One or More member IDs to add
			groupId (int | str): Group ID to add admins
			
		Returns:
			object: `Group` Group admins add status
			None: If requet success/failed depending on the case
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		if isinstance(members, list):
			members = [str(member) for member in members]
		else:
			members = [str(members)]
			
		params = {
			"params": self._encode({
				"grid": str(groupId),
				"members": members,
				"imei": self._imei
			}),
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._get("https://tt-group-wpa.chat.zalo.me/api/group/admins/add", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	def removeGroupAdmins(self, members, groupId):
		"""Remove admins in the group (white key) by ID.
		
		Client must be the Owner of the group.
			
		Args:
			members (str | list): One or More admin IDs to remove
			groupId (int | str): Group ID to remove admins
			
		Returns:
			object: `Group` Group admins remove status
			None: If requet success/failed depending on the case
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		if isinstance(members, list):
			members = [str(member) for member in members]
		else:
			members = [str(members)]
			
		params = {
			"params": self._encode({
				"grid": str(groupId),
				"members": members,
				"imei": self._imei
			}),
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._get("https://tt-group-wpa.chat.zalo.me/api/group/admins/remove", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def deleteGroupMsg(self, msgId, ownerId, clientMsgId, groupId):
		"""Delete message in group by ID.
		
		Args:
			groupId (int | str): Group ID to delete message
			msgId (int | str): Message ID to delete
			ownerId (int | str): Owner ID of the message to delete
			clientMsgId (int | str): Client message ID to delete message
		
		Returns:
			object: `Group` delete message status
			dict: A dictionary containing error_code & responses if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"grid": str(groupId),
				"cliMsgId": _util.now(),
				"msgs": [{
					"cliMsgId": str(clientMsgId),
					"globalMsgId": str(msgId),
					"ownerId": str(ownerId),
					"destId": str(groupId)
				}],
				"onlyMe": 0
			})
		}
		
		response = self._post("https://tt-group-wpa.chat.zalo.me/api/group/deletemsg", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def viewGroupPending(self, groupId):
		"""See list of people pending approval in group by ID.
		
		Args:
			groupId (int | str): Group ID to view pending members
			
		Returns:
			object: `Group` pending responses
			dict: A dictionary containing error_code & responses if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"params": self._encode({
				"grid": str(groupId),
				"imei": self._imei
			}),
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._get("https://tt-group-wpa.chat.zalo.me/api/group/pending-mems/list", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def handleGroupPending(self, members, groupId, isApprove=True):
		"""Approve/Deny pending users to the group from the group's approval.
		
		Client must be the Owner of the group.
		
		Args:
			members (str | list): One or More member IDs to handle
			groupId (int | str): ID of the group to handle pending members
			isApprove (bool): Approve/Reject pending members (True | False)
			
		Returns:
			object: `Group` handle pending responses
			dict: A dictionary/object containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		if isinstance(members, list):
			members = [str(member) for member in members]
		else:
			members = [str(members)]
		
		params = {
			"params": self._encode({
				"grid": str(groupId),
				"members": members,
				"isApprove": 1 if isApprove else 0
			}),
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._get("https://tt-group-wpa.chat.zalo.me/api/group/pending-mems/review", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
				
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def viewPollDetail(self, pollId):
		"""View poll data by ID.
		
		Args:
			pollId (int | str): Poll ID to view detail
			
		Returns:
			object: `Group` poll data
			dict: A dictionary containing error_code & response if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"params": self._encode({
				"poll_id": int(pollId),
				"imei":self._imei
			}),
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		response = self._get("https://tt-group-wpa.chat.zalo.me/api/poll/detail", params=params)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def createPoll(
		self,
		question,
		options,
		groupId,
		expiredTime=0,
		pinAct=False,
		multiChoices=True,
		allowAddNewOption=True,
		hideVotePreview=False,
		isAnonymous=False
	):
		"""Create poll in group by ID.
		
		Client must be the Owner of the group.
		
		Args:
			question (str): Question for poll
			options (str | list): List options for poll
			groupId (int | str): Group ID to create poll from
			expiredTime (int): Poll expiration time (0 = no expiration)
			pinAct (bool): Pin action (pin poll)
			multiChoices (bool): Allows multiple poll choices
			allowAddNewOption (bool): Allow members to add new options
			hideVotePreview (bool): Hide voting results when haven't voted
			isAnonymous (bool): Hide poll voters
			
		Returns:
			object: `Group` poll create data
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"group_id": str(groupId),
				"question": question,
				"options": [],
				"expired_time": expiredTime,
				"pinAct": pinAct,
				"allow_multi_choices": multiChoices,
				"allow_add_new_option": allowAddNewOption,
				"is_hide_vote_preview": hideVotePreview,
				"is_anonymous": isAnonymous,
				"poll_type": 0,
				"src": 1,
				"imei": self._imei
			}
		}
		
		if isinstance(options, list):
			payload["params"]["options"] = options
		else:
			payload["params"]["options"].append(str(options))
		
		payload["params"] = self._encode(payload["params"])
		
		response = self._post("https://tt-group-wpa.chat.zalo.me/api/poll/create", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def lockPoll(self, pollId):
		"""Lock/end poll in group by ID.
		
		Client must be the Owner of the group.
		
		Args:
			pollId (int | str): Poll ID to lock
			
		Returns:
			None: If requet success
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"poll_id": int(pollId),
				"imei": self._imei
			})
		}
		
		response = self._post("https://tt-group-wpa.chat.zalo.me/api/poll/end", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def disperseGroup(self, groupId):
		"""Disperse group by ID.
		
		Client must be the Owner of the group.
			
		Args:
			groupId (int | str): Group ID to disperse
			
		Returns:
			None: If requet success
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"grid": str(groupId),
				"imei": self._imei
			})
		}
		
		response = self._post("https://tt-group-wpa.chat.zalo.me/api/group/disperse", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("error_code") == 0 else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	"""
	END GROUP ACTION METHODS
	"""
	
	"""
	SEND METHODS
	"""
	
	def send(self, message, thread_id, thread_type=ThreadType.USER, mark_message=None):
		"""Send message to a thread.
			
		Args:
			message (Message): Message to send
			thread_id (int | str): User/Group ID to send to
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` (Returns msg ID just sent)
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		thread_id = str(int(thread_id) or self.uid)
		if message.mention:
			return self.sendMentionMessage(message, thread_id)
		else:
			return self.sendMessage(message, thread_id, thread_type, mark_message)
	
	def sendMessage(self, message, thread_id, thread_type, mark_message=None):
		"""Send message to a thread (user/group).
			
		Args:
			message (Message): Message to send
			mark_message (str): Send messages as `Urgent` or `Important` mark
			thread_id (int | str): User/Group ID to send to
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` (Returns msg ID just sent)
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"message": message.text,
				"clientId": _util.now(),
				"imei": self._imei,
				"ttl": 0,
			}
		}
		
		if mark_message and mark_message.lower() in ["important", "urgent"]:
			markType = 1 if mark_message.lower() == "important" else 2
			payload["params"]["metaData"] = {"urgency": markType}
		
		if message.style:
			payload["params"]["textProperties"] = message.style
			
		if thread_type == ThreadType.USER:
			url = "https://tt-chat2-wpa.chat.zalo.me/api/message/sms"
			payload["params"]["toid"] = str(thread_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-group-wpa.chat.zalo.me/api/group/sendmsg"
			payload["params"]["visibility"] = 0
			payload["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return (
				Group.fromDict(results, self._undefined) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, self._undefined)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def replyMessage(self, message, replyMsg, thread_id, thread_type):
		"""Reply message in group by ID.
			
		Args:
			message (Message): Message Object
			replyMsg (Message): Message Object to reply
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` (Returns msg ID just sent)
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"message": message.text,
				"clientId": _util.now(),
				"qmsgOwner": str(int(replyMsg.uidFrom) or self.uid),
				"qmsgId": replyMsg.msgId,
				"qmsgCliId": replyMsg.cliMsgId,
				"qmsgType": 1,
				"qmsg": replyMsg.content,
				"qmsgTs": replyMsg.ts,
				"qmsgAttach": json.dumps({"properties": {"color":0,"size":0,"type":0,"subType":0,"ext": {"shouldParseLinkOrContact":0}}}),
				"qmsgTTL": 0,
				"ttl": 0
			}
		}
		
		if message.style:
			payload["params"]["textProperties"] = message.style
			
		if message.mention:
			payload["params"]["mentionInfo"] = message.mention
		
		if thread_type == ThreadType.USER:
			url = "https://tt-chat2-wpa.chat.zalo.me/api/message/quote"
			payload["params"]["toid"] = str(thread_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-group-wpa.chat.zalo.me/api/group/quote"
			payload["params"]["visibility"] = 0
			payload["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return (
				Group.fromDict(results, self._undefined) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, self._undefined)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def sendMentionMessage(self, message, groupId):
		"""Send message to a group with mention by ID.
			
		Args:
			mention (str): Mention format data to send
			message (Message): Message to send
			groupId: Group ID to send to.
			
		Returns:
			object: `User/Group` (Returns msg ID just sent)
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"grid": str(groupId),
				"message": message.text,
				"mentionInfo": message.mention,
				"clientId": _util.now(),
				"visibility": 0,
				"ttl": 0
			}
		}
		
		if message.style:
			payload["params"]["textProperties"] = message.style
		
		payload["params"] = self._encode(payload["params"])
		
		response = self._post("https://tt-group-wpa.chat.zalo.me/api/group/mention", params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return Group.fromDict(results, self._undefined)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def undoMessage(self, msgId, cliMsgId, thread_id, thread_type):
		"""Undo message from the client by ID.
			
		Args:
			msgId (int | str): Message ID to undo
			cliMsgId (int | str): Client Msg ID to undo
			thread_id (int | str): User/Group ID to undo message
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` undo message status
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"msgId": str(msgId),
				"cliMsgIdUndo": str(cliMsgId),
				"clientId": _util.now()
			} 
		}
		
		if thread_type == ThreadType.USER:
			url = "https://tt-chat3-wpa.chat.zalo.me/api/message/undo"
			payload["params"]["toid"] = str(thread_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-group-wpa.chat.zalo.me/api/group/undomsg"
			payload["params"]["grid"] = str(thread_id)
			payload["params"]["visibility"] = 0
			payload["params"]["imei"] = self._imei
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return (
				Group.fromDict(results, self._undefined) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, self._undefined)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def sendReaction(self, msgId, clientMsgId, reactionIcon, thread_id, thread_type, reactionType=75, msgType=1):
		"""Reaction message by ID.
			
		Args:
			msgId (int | str): Message ID to reaction
			clientMsgId (int | str): Client message ID to defind reaction
			reactionIcon (str): Icon/Text to reaction
			thread_id (int | str): Group/User ID contain message to reaction
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` message reaction data
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"react_list": [{
					"message": json.dumps({
						"rMsg": [{
							"gMsgID": int(msgId),
							"cMsgID": int(clientMsgId),
							"msgType": int(msgType)
						}],
						"rIcon": reactionIcon,
						"rType": reactionType,
						"source": 6
					}),
					"clientId": _util.now()
				}],
				"imei": self._imei
			}
		}
		
		if thread_type == ThreadType.USER:
			url = "https://reaction.chat.zalo.me/api/message/reaction"
			payload["params"]["toid"] = str(thread_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://reaction.chat.zalo.me/api/group/reaction"
			payload["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return (
				Group.fromDict(results, self._undefined) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, self._undefined)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def sendMultiReaction(self, reactionObj, reactionIcon, thread_id, thread_type, reactionType=75):
		"""Reaction message by ID.
			
		Args:
			reactionObj (MessageReaction): Message(s) data to reaction
			reactionIcon (str): Icon/Text to reaction
			thread_id (int | str): Group/User ID contain message to reaction
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` message reaction data
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"react_list": [{
					"message": {
						"rMsg": [],		
						"rIcon": reactionIcon,
						"rType": reactionType,
						"source": 6
					},
					"clientId": _util.now()
				}],
				"imei": self._imei
			}
		}
		
		if isinstance(reactionObj, dict):
			payload["params"]["react_list"][0]["message"]["rMsg"].append(reactionObj)
		elif isinstance(reactionObj, list):
			payload["params"]["react_list"][0]["message"]["rMsg"] = reactionObj
		else:
			raise ZaloUserError("Reaction type is invalid")
		
		if thread_type == ThreadType.USER:
			url = "https://reaction.chat.zalo.me/api/message/reaction"
			payload["params"]["toid"] = str(thread_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://reaction.chat.zalo.me/api/group/reaction"
			payload["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"]["react_list"][0]["message"] = json.dumps(payload["params"]["react_list"][0]["message"])
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return (
				Group.fromDict(results, self._undefined) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, self._undefined)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def sendRemoteFile(self, fileUrl, thread_id, thread_type, fileName="default", fileSize=None) -> object:
		"""Send File to a User/Group with url.
			
		Args:
			fileUrl (str): File url to send
			fileName (str): File name to send
			fileSize (int): File size to send
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` (Returns msg ID just sent)
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		
	def sendLocalImage(self, imagePath, message, thread_id, thread_type, imageWidth=2560, imageHeight=2560):
		"""Send Image to a User/Group with local file.
			
		Args:
			imagePath (str): Image directory to send
			imageWidth (int): Image width to send
			imageHeight (int): Image height to send
			message (Message): Message object to send
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` objects
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		uploadImage = self._uploadImage(imagePath, thread_id, thread_type)
		
		params = {
			"zpw_ver": 634,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"photoId": uploadImage["photoId"], # 318373455858
				"clientId": uploadImage["clientFileId"],
				"desc": message.text or "",
				"width": imageWidth,
				"height": imageHeight,
				"rawUrl": uploadImage["normalUrl"],
				"thumbUrl": uploadImage["thumbUrl"],
				"hdUrl": uploadImage["hdUrl"],
				"thumbSize": "53932",
				"fileSize": "247671",
				"hdSize": "344622",
				"zsource": -1,
				"jcp": json.dumps({"sendSource": 1}),
				"ttl": 0,
				"imei": self._imei
			}
		}
		
		if message.mention:
			payload["params"]["mentionInfo"] = message.mention
			
		if thread_type == ThreadType.USER:
			url = "https://tt-files-wpa.chat.zalo.me/api/message/photo_original/send"
			payload["params"]["toid"] = str(thread_id)
			payload["params"]["normalUrl"] = uploadImage["normalUrl"]
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-files-wpa.chat.zalo.me/api/group/photo_original/send"
			payload["params"]["grid"] = str(thread_id)
			payload["params"]["oriUrl"] = uploadImage["normalUrl"]
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return (
				Group.fromDict(results, self._undefined) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, self._undefined)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def sendSticker(self, stickerId, cateId, thread_id, thread_type):
		"""Send Sticker to a User/Group.
			
		Args:
			stickerId (int | str): Sticker id to send
			cateId (int | str): Sticker category id to send
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` objects
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"stickerId": int(stickerId),
				"cateId": int(cateId),
				"type": 7,
				"clientId": _util.now(),
				"imei": self._imei,
				"ttl": 0,
			}
		}
		
		if thread_type == ThreadType.USER:
			url = "https://tt-chat2-wpa.chat.zalo.me/api/message/sticker"
			payload["params"]["zsource"] = 106
			payload["params"]["toid"] = str(thread_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-group-wpa.chat.zalo.me/api/group/sticker"
			payload["params"]["zsource"] = 103
			payload["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return (
				Group.fromDict(results, self._undefined) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, self._undefined)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	def sendCustomSticker(
		self,
		staticImgUrl,
		animationImgUrl,
		thread_id,
		thread_type,
		reply=None,
		width=None,
		height=None
	):
		"""Send custom (static/animation) sticker to a User/Group with url.
			
		Args:
			staticImgUrl (str): Image url (png, jpg, jpeg) format to create sticker
			animationImgUrl (str): Static/Animation image url (webp) format to create sticker
			thread_id (int | str): User/Group ID to send sticker to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			reply (int | str): Message ID to send stickers with quote
			width (int | str): Width of photo/sticker
			height (int | str): Height of photo/sticker
			
		Returns:
			object: `User/Group` sticker data
			dict: A dictionary containing error responses
			
		Raises:
			ZaloAPIException: If request failed
		"""
		width = int(width) if width else 498
		height = int(height) if height else 332
		params = {
			"zpw_ver": 634,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"clientId": _util.now(),
				"title": "",
				"oriUrl": staticImgUrl,
				"thumbUrl": staticImgUrl,
				"hdUrl": staticImgUrl,
				"width": width, #0
				"height": height, #0
				"properties": json.dumps({
					"subType": 0,
					"color": -1,
					"size": -1,
					"type": 3,
					"ext": json.dumps({
						"sSrcStr": "@STICKER",
						"sSrcType": 0
					})
				}),
				"contentId": _util.now(), #2842316716983420400
				"thumb_height": width,
				"thumb_width": height,
				"webp": json.dumps({
					"width": width, #0
					"height": height, #0
					"url": animationImgUrl
				}),
				"zsource": -1,
				"ttl": 0
			}
		}
		
		if reply:
			payload["params"]["refMessage"] = str(reply)
			
		if thread_type == ThreadType.USER:
			url = "https://tt-files-wpa.chat.zalo.me/api/message/photo_url"
			payload["params"]["toId"] = str(thread_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-files-wpa.chat.zalo.me/api/group/photo_url"
			payload["params"]["visibility"] = 0
			payload["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			results = results.get("data") if results.get("data") else results
			if results == None:
				results = {"error_code": 1337, "error_message": "Data is None"}
			
			if isinstance(results, str):
				try:
					results = json.loads(results)
				except:
					results = {"error_code": 1337, "error_message": results}
			
			return (
				Group.fromDict(results, self._undefined) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, self._undefined)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	"""
	END SEND METHODS
	"""
	
	def setTypingStatus(self, thread_id, thread_type):
		"""Set users typing status.
			
		Args:
			thread_id: User/Group ID to change status in.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"imei": self._imei
			}
		}
		
		if thread_type == ThreadType.USER:
			url = "https://tt-chat1-wpa.chat.zalo.me/api/message/typing"
			payload["params"]["toid"] = str(thread_id)
			payload["params"]["destType"] = 3
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-group-wpa.chat.zalo.me/api/group/typing"
			payload["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			return True
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def markAsDelivered(
		self,
		msgId,
		cliMsgId,
		senderId,
		thread_id,
		thread_type,
		seen=0,
		method="webchat"
	):
		"""Mark a message as delivered.
		
		Args:
			cliMsgId (int | str): Client message ID
			msgId (int | str): Message ID to set as delivered
			senderId (int | str): Message sender Id
			thread_id (int | str): User/Group ID to mark as delivered
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			bool: True
			
		Raises:
			ZaloAPIException: If request failed
		"""
		destination_id = "0" if thread_type == ThreadType.USER else thread_id
		
		params = {
			"zpw_ver": 634,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"msgInfos": {
					"seen": 0,
					"data": [{
						"cmi": str(cliMsgId),
						"gmi": str(msgId),
						"si": str(senderId),
						"di": str(destination_id),
						"mt": method,
						"st": 3,
						"at": 0,
						"ts": str(_util.now())
					}]
				}
			}
		}
		
		if thread_type == ThreadType.USER:
			url = "https://tt-chat3-wpa.chat.zalo.me/api/message/deliveredv2"
			payload["params"]["msgInfos"]["data"][0]["cmd"] = 501
		else:
			url = "https://tt-group-wpa.chat.zalo.me/api/group/deliveredv2"
			payload["params"]["msgInfos"]["data"][0]["cmd"] = 521
			payload["params"]["msgInfos"]["grid"] = str(destination_id)
			payload["params"]["imei"] = self._imei
		
		payload["params"]["msgInfos"] = json.dumps(payload["params"]["msgInfos"])
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			self.onMessageDelivered(msgId, thread_id, thread_type, _util.now())
			return True
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	def markAsRead(
		self,
		msgId,
		cliMsgId,
		senderId,
		thread_id,
		thread_type,
		method="webchat"
	):
		"""Mark a message as read.
		
		Args:
			cliMsgId (int | str): Client message ID
			msgId (int | str): Message ID to set as delivered
			senderId (int | str): Message sender Id
			thread_id (int | str): User/Group ID to mark as read
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			bool: True
			
		Raises:
			ZaloAPIException: If request failed
		"""
		destination_id = "0" if thread_type == ThreadType.USER else thread_id
		
		params = {
			"zpw_ver": 634,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"msgInfos": {
					"data": [{
						"cmi": str(cliMsgId),
						"gmi": str(msgId),
						"si": str(senderId),
						"di": str(destination_id),
						"mt": method,
						"st": 3,
						"ts": str(_util.now())
					}]
				},
				"imei": self._imei
			}
		}
		
		if thread_type == ThreadType.USER:
			url = "https://tt-chat1-wpa.chat.zalo.me/api/message/seenv2"
			payload["params"]["msgInfos"]["data"][0]["at"] = 7
			payload["params"]["msgInfos"]["data"][0]["cmd"] = 501
			payload["params"]["senderId"] = str(destination_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-group-wpa.chat.zalo.me/api/group/seenv2"
			payload["params"]["msgInfos"]["data"][0]["at"] = 0
			payload["params"]["msgInfos"]["data"][0]["cmd"] = 511
			payload["params"]["grid"] = str(destination_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"]["msgInfos"] = json.dumps(payload["params"]["msgInfos"])
		payload["params"] = self._encode(payload["params"])
		
		response = self._post(url, params=params, data=payload)
		data = response.json()
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			self.onMarkedSeen(msgId, thread_id, thread_type, _util.now())
			return True
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	"""
	LISTEN METHODS
	"""
	
	def _listen(self, delay=1):
		HasRead = set()
		while not self._condition.is_set():
			if len(HasRead) > 10000000:
				HasRead.clear()
			
			ListenTime = int((time.time() - 10) * 1000)
			messages = self.getLastMsgs()
			groupmsg = messages.groupMsgs
			messages = messages.msgs
			for message in messages:
				if int(message["ts"]) >= ListenTime and message["msgId"] not in HasRead:
					HasRead.add(message["msgId"])
					msgObj = MessageObject.fromDict(message, self._undefined)
					self.onMessage(msgObj.msgId, str(int(msgObj.uidFrom) or self.uid), msgObj.content, msgObj, str(int(msgObj.uidFrom) or msgObj.idTo), ThreadType.USER)
			
			for message in groupmsg:
				if int(message["ts"]) >= ListenTime and message["msgId"] not in HasRead:
					HasRead.add(message["msgId"])
					msgObj = MessageObject.fromDict(message, self._undefined)
					self.onMessage(msgObj.msgId, str(int(msgObj.uidFrom) or self.uid), msgObj.content, msgObj, str(int(msgObj.idTo) or self.uid), ThreadType.GROUP)
			
			time.sleep(delay)
			
	def _listen_test(self, delay=1):
		HasRead = set()
		Groups = [groupId for groupId in self.fetchAllGroups().gridVerMap]
		while not self._condition.is_set():
			if len(HasRead) > 10000000:
				HasRead.clear()
			
			ListenTime = _util.now()
			messages = self.getLastMsgs()
			messages = messages.msgs
			for message in messages:
				if int(message["ts"]) >= ListenTime and message["msgId"] not in HasRead:
					HasRead.add(message["msgId"])
					msgObj = MessageObject.fromDict(message, self._undefined)
					self.onMessage(msgObj.msgId, str(int(msgObj.uidFrom) or self.uid), msgObj.content, msgObj, str(int(msgObj.uidFrom) or msgObj.idTo), ThreadType.USER)
			
			for groupId in Groups:
				messages = self.getRecentGroup(groupId)
				try:
					messages = messages.groupMsgs
				except:
					messages = []
				
				for message in messages:
					if int(message["ts"]) >= ListenTime and message["msgId"] not in HasRead:
						HasRead.add(message["msgId"])
						msgObj = MessageObject.fromDict(message, self._undefined)
						self.onMessage(msgObj.msgId, str(int(msgObj.uidFrom) or self.uid), msgObj.content, msgObj, str(int(msgObj.idTo) or self.uid), ThreadType.GROUP)
			
			time.sleep(delay)
	
	def _listen_group(self):
		ListenTime = _util.now()
		Groups = [groupId for groupId in self.fetchAllGroups().gridVerMap]
		while not self._condition.is_set():
			for groupId in Groups:
				messages = self.getRecentGroup(groupId)
				messages = messages.groupMsgs
				for message in messages:
					if int(message["ts"]) >= ListenTime:
						msgObj = MessageObject.fromDict(message, self._undefined)
						self.onMessage(msgObj.msgId, str(int(msgObj.uidFrom) or self.uid), msgObj.content, msgObj, str(int(msgObj.idTo) or self.uid), ThreadType.GROUP)
			
			ListenTime = _util.now()
			time.sleep(1)
	
	def _listen_user(self):
		ListenTime = _util.now()
		while not self._condition.is_set():
			HasRead = []
			messages = self.getLastMsgs()
			messages = messages.msgs
			for message in messages:
				if int(message["ts"]) >= ListenTime and message["msgId"] not in HasRead:
					HasRead.append(message["msgId"])
					msgObj = MessageObject.fromDict(message, self._undefined)
					self.onMessage(msgObj.msgId, str(int(msgObj.uidFrom) or self.uid), msgObj.content, msgObj, str(int(msgObj.uidFrom) or msgObj.idTo), ThreadType.USER)
					
			HasRead = HasRead[-1:]
			ListenTime = _util.now()
			time.sleep(1)
			
	def startListening(self, delay=1, test=False, background=False):
		"""Start listening from an external event loop.
		
		Args:
			delay (int): Delay time each time fetching a message
			test (bool): Listen `test` or `main` mode, Default: False (Main Mode)
			background (bool): Background listening mode (Default: True)
		
		Raises:
			ZaloAPIException: If request failed
		"""
		self._condition.clear()
		if background:
			[
				thread.submit(self._listen, delay)
				if not background else
				thread.submit(self._listen_test, delay)
			]
			self.listening = True
		
		else:
			[
				self._listen(delay)
				if not background else
				self._listen_test(delay)
			]
	
	def stopListening(self):
		"""Stop the listening loop."""
		self.listening = False
		self._condition.set()
	
	def listen(self, delay=1, test=False, background=False):
		"""Initialize and runs the listening loop continually.
		
		Args:
			delay (int): Delay time for each message fetch (Default: 1)
			test (bool): Listen test mode (Default: False)
			background (bool): Listen in the background (Default: False)
		
		"""
		self.onListening()
		self.startListening(delay, test, background)
		if background:
			while self.listening:
				pass
			
			self.stopListening()
	
	"""
	END LISTEN METHODS
	"""
	
	"""
	EVENTS
	"""
	
	def onLoggingIn(self, phone=None):
		"""Called when the client is logging in.
			
		Args:
			phone: The phone number of the client
		"""
		print("Logging in {}...".format(phone))
		
	def onLoggedIn(self, phone=None):
		"""Called when the client is successfully logged in.
			
		Args:
			phone: The phone number of the client
		"""
		print("Login of {} successful.".format(phone))
	
	def onListening(self):
		"""Called when the client is listening."""
		print("Listening...")
		
	def onMessage(
		self,
		mid=None,
		author_id=None,
		message=None,
		message_object=None,
		thread_id=None,
		thread_type=ThreadType.USER
	):
		"""Called when the client is listening, and somebody sends a message.

		Args:
			mid: The message ID
			author_id: The ID of the author
			message: The message content of the author
			message_object: The message (As a `Message` object)
			thread_id: Thread ID that the message was sent to.
			thread_type (ThreadType): Type of thread that the message was sent to.
		"""
		print("{} from {} in {}".format(message, thread_id, thread_type.name))
	
	def onMessageDelivered(
		self,
		msg_ids=None,
		thread_id=None,
		thread_type=ThreadType.USER,
		ts=None
	):
		"""Called when the client is listening, and the client has successfully marked messages as delivered.
		
		Args:
			msg_ids: The messages that are marked as delivered
			thread_id: Thread ID that the action was sent to
			thread_type (ThreadType): Type of thread that the action was sent to
			ts: A timestamp of the action
		"""
		print(
			"Marked messages {} as delivered in [({}, {})] at {}.".format(
				msg_ids, thread_id, thread_type.name, int(ts / 1000)
			)
		)

	def onMarkedSeen(
		self,
		msg_ids=None,
		thread_id=None,
		thread_type=ThreadType.USER,
		ts=None
	):
		"""Called when the client is listening, and the client has successfully marked messages as read/seen.
		
		Args:
			msg_ids: The messages that are marked as read/seen
			thread_id: Thread ID that the action was sent to
			thread_type (ThreadType): Type of thread that the action was sent to
			ts: A timestamp of the action
		"""
		print(
			"Marked messages {} as seen in [({}, {})] at {}.".format(
				msg_ids, thread_id, thread_type.name, int(ts / 1000)
			)
		)
	
	"""
	END EVENTS
	"""