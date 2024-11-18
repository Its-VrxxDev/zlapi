# -*- coding: UTF-8 -*-
import random
import websockets

from ..Async import _state
from .. import _util
from ..models import *
from .._package import *
from ..logging import Logging
from websockets.client import connect
from concurrent.futures import ThreadPoolExecutor
		
pool = ThreadPoolExecutor()
logger = Logging(theme="catppuccin-mocha", log_text_color="black")

class ZaloAPI(object):
	def __init__(self, phone, password, imei=None, cookies=None, user_agent=None, auto_login=True, prefix=""):
		"""Initialize and log in the client.
		
		Args:
			imei (str): The device imei is logged into Zalo
			phone (str): Zalo account phone number
			password (str): Zalo account password
			prefix (str): Bot prefix
			auto_login (bool): Automatically log in when initializing ZaloAPI (Default: True)
			user_agent (str): Custom user agent to use when sending requests. If `None`, user agent will be chosen from a premade list
			cookies (dict): Cookies from a previous session (Required if logging in with cookies)
			
		Raises:
			ZaloLoginError: On failed login
			LoginMethodNotSupport: If method login not support
		"""
		self.prefix = prefix
		self.register_commands = {}
		self.register_messages = []
		self.conversation_handlers = {}
		
		self._state = _state.State()
		self._condition = threading.Event()
		self._listening = False
		self._start_fix = True
		
		if auto_login:
			if (
				not cookies 
				or not self.set_session(cookies) 
				or not self.is_logged_in()
			):
				asyncio.run(self.login(phone, password, imei, user_agent))
	
	def uid(self):
		"""The ID of the client."""
		return self.uid
	
	"""
	REGISTER COMMANDS EVENTS
	"""
	
	@staticmethod
	def check_commands_input(commands, method_name):
		if not isinstance(commands, list) or not all(isinstance(item, str) for item in commands):
			raise ValueError(f'{method_name}: Commands filter should be a list of strings. Unknown type supplied to "commands".')

	@staticmethod
	def add_register_handler(func):
		@functools.wraps(func)
		async def wrapper(self, ctx):
			await func(self, ctx)
			
			if ctx.author_id in self.conversation_handlers:
				handler_info = self.conversation_handlers[ctx.author_id]
				del self.conversation_handlers[ctx.author_id]
				return await handler_info["handler"](ctx, *handler_info["args"], **handler_info["kwargs"])
			
			if str(ctx.message) in self.register_commands:
				await self.register_commands[str(ctx.message)](ctx)
			
			for funcheck, condition in self.register_messages:
				if condition(str(ctx.message)):
					await funcheck(ctx)

		return wrapper
	
	
	def register_handler(self, func=None, commands=None):
		def decorator(handler_func):
			if commands is not None:
				self.check_commands_input(commands, "register_handler")
				
				for command in commands:
					self.register_commands[self.prefix + command] = handler_func
			
			if func:
				self.register_messages.append((handler_func, func))

			return handler_func
		
		return decorator
	
	
	def register_next_step_handler(self, func, ctx, *args, **kwargs):
		if not ctx.author_id:
			print("Could not find message sender id, function not registered!")
			return
		else:
			self.conversation_handlers[ctx.author_id] = {"handler": func, "args": args, "kwargs": kwargs}
	
	
	def event(self, func):
		setattr(self, func.__name__, func)
	
	
	def run_in_thread(self, func, *args, **kwargs):
		def run_async():
			loop = asyncio.new_event_loop()
			asyncio.set_event_loop(loop)
			loop.run_until_complete(func(*args, **kwargs))
			loop.close()
		
		pool.submit(run_async)
	
		
	async def load_extension(self, name, package=None):
		if package is None:
			package = __package__
		
		try:
			module = importlib.import_module(name, package)
		except ImportError as e:
			raise ImportError(f"Failed to load extension {name}: {e}")
		
		if not hasattr(module, "setup"):
			print(f"Skipping {name} as it does not have a setup function")
			return
		
		setup_func = module.setup
		
		if inspect.iscoroutinefunction(setup_func):
			
			await setup_func(self)
		
		else:
			
			setup_func(self)
		
		return module
	
	"""
	END REGISTER COMMANDS EVENTS
	"""
	
	"""
	INTERNAL REQUEST METHODS
	"""
	
	async def _get(self, *args, **kwargs):
		return await self._state._get(*args, **kwargs)
		
	async def _post(self, *args, **kwargs):
		return await self._state._post(*args, **kwargs)
	
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
	
	def is_logged_in(self):
		"""Get data from config to check the login status.

		Returns:
			bool: True if the client is still logged in
		"""
		return self._state.is_logged_in()
		
	async def get_session(self):
		"""Retrieve session cookies.
			
		Returns:
			dict: A dictionary containing session cookies
		"""
		return await self._state.get_cookies()
		
	def set_session(self, cookies):
		"""Load session cookies.
		
		Warning:
			Error sending requests if session cookie is wrong
			
		Args:
			cookies (dict): A dictionary containing session cookies
			
		Returns:
			Bool: False if ``cookies`` does not contain proper cookies
		"""
		try:
			if not isinstance(cookies, dict):
				return False
			# Load cookies into current session
			self._state.set_cookies(cookies)
			self.uid = self._state.user_id
		except Exception as e:
			print("Failed loading session")
			return False
		return True
	
	async def get_secret_key(self):
		"""Retrieve secret key to encode/decode payload.
			
		Returns:
			str: A secret key string with base64 encode
		"""
		return await self._state.get_secret_key()
		
	def set_secret_key(self, secret_key):
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
	
	async def login(self, phone, password, imei, user_agent=None):
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
		
		await self.on_logging_in()
		
		await self._state.login(
			phone,
			password,
			imei,
			user_agent=user_agent
		)
		try:
			self._imei = self._state.user_imei
			self.uid = (await self.fetch_account_info()).profile.get("userId", self._state.user_id)
		except:
			self._imei = None
			self.uid = self._state.user_id
		
		await self.on_logged_in(self._state._config.get("phone_number"))
		
	"""
	END LOGIN METHODS
	"""
	
	"""
	ATTACHMENTS METHODS
	"""
	
	async def _uploadImage(self, filePath, thread_id, thread_type):
		"""Upload images to Zalo.
			
		Args:
			filePath (str): Image path to upload
			thread_id (int | str): User/Group ID to upload to.
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
			"zpw_ver": 647,
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
		
		data = await self._post(url, params=params, data=files)
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
	
	async def fetch_account_info(self):
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
			"zpw_ver": 647,
			"zpw_type": 30,
			"os": 8,
			"browser": 0
		}
		
		data = await self._get("https://tt-profile-wpa.chat.zalo.me/api/social/profile/me-v2", params=params)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def fetch_phone_number(self, phoneNumber, language="vi"):
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
			"zpw_ver": 647,
			"zpw_type": 30,
			"params": self._encode({
				"phone": phone,
				"avatar_size": 240,
				"language": language,
				"imei": self._imei,
				"reqSrc": 85
			})
		}
		
		data = await self._get("https://tt-friend-wpa.chat.zalo.me/api/friend/profile/get", params=params)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	async def fetch_user_info(self, userId):
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
			"zpw_ver": 647,
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
		
		data = await self._post("https://tt-profile-wpa.chat.zalo.me/api/social/friend/getprofiles/v2", params=params, data=payload)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def fetch_group_info(self, groupId):
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
			"zpw_ver": 647,
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
		
		data = await self._post("https://tt-group-wpa.chat.zalo.me/api/group/getmg-v2", params=params, data=payload)
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
			
			return Group.fromDict(results, None)
		
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def fetch_all_friends(self):
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
			"zpw_ver": 647,
			"zpw_type": 30,
			"nretry": 0
		}
		
		data = await self._get("https://profile-wpa.chat.zalo.me/api/social/friend/getfriends", params=params)
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
		
	async def fetch_all_groups(self):
		"""Fetch all group IDs are joining and chatting.
		
		Returns:
			object: `Group` all group IDs
			any: If response is not all group IDs
		
		Raises:
			ZaloAPIException: If request failed
		"""
		
		params = {
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/group/getlg/v4", params=params)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	"""
	END FETCH METHODS
	"""
	
	"""
	GET METHODS
	"""
	
	async def get_last_msgs(self):
		"""Get last message the client"s friends/group chat room.
			
		Returns:
			object: `User` last msg data
			dict: A dictionary containing error_code, response if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": "647",
			"zpw_type": "30",
			"params": self._encode({
				"threadIdLocalMsgId": json.dumps({}),
				"imei": self._imei
			})
		}
		
		data = await self._get("https://tt-convers-wpa.chat.zalo.me/api/preloadconvers/get-last-msgs", params=params)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def get_recent_group(self, groupId):
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
			"zpw_ver": 647,
			"zpw_type": 30,
			"nretry": 0,
		}
		
		data = await self._get("https://tt-group-cm.chat.zalo.me/api/cm/getrecentv2", params=params)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def _getGroupBoardList(self, board_type, page, count, last_id, last_type, groupId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._get("https://groupboard-wpa.chat.zalo.me/api/board/list", params=params)
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
			
			results = Group.fromDict(results, None) if results.get("error_code") == 0 else results
			
			return results
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def get_group_board_list(self, groupId, page=1, count=20, last_id=0, last_type=0):
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
		response = await self._getGroupBoardList(0, page, count, last_id, last_type, groupId)
		
		return response
	
	async def get_group_pinmsg(self, groupId, page=1, count=20, last_id=0, last_type=0):
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
		response = await self._getGroupBoardList(2, page, count, last_id, last_type, groupId)
		
		return response
	
	async def get_group_note(self, groupId, page=1, count=20, last_id=0, last_type=0):
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
		response = await self._getGroupBoardList(1, page, count, last_id, last_type, groupId)
		
		return response
	
	async def get_group_poll(self, groupId, page=1, count=20, last_id=0, last_type=0):
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
		response = await self._getGroupBoardList(3, page, count, last_id, last_type, groupId)
		
		return response
	
	"""
	END GET METHODS
	"""
	
	"""
	ACCOUNT ACTION METHODS
	"""
	
	async def change_account_setting(self, name, dob, gender, biz={}, language="vi"):
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
			"zpw_ver": 647,
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
		
		data = await self._post("https://tt-profile-wpa.chat.zalo.me/api/social/profile/update", params=params, data=payload)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def change_account_avatar(self, filePath, width=500, height=500, language="vn", size=None):
		"""Upload/Change account avatar.
		
		Args:
			filePath (str): A path to the image to upload/change avatar
			size (int): Avatar image size (default = auto)
			width (int): Width of avatar image
			height (int): height of avatar image
			language (int | str): Zalo Website language ? (idk)
		
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
			"zpw_ver": 647,
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
		
		data = await self._post("https://tt-files-wpa.chat.zalo.me/api/profile/upavatar", params=params, data=files)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	"""
	END ACCOUNT ACTION METHODS
	"""
	
	"""
	USER ACTION METHODS
	"""
	
	async def send_friend_request(self, userId, msg, language="vi"):
		"""Send friend request to a user by ID.
			
		Args:
			userId (int | str): User ID to send friend request
			msg (str): Friend request message
			language (str): Response language or Zalo interface language

		Returns:
			object: `User` Friend requet response
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"toid": str(userId),
				"msg": msg,
				"reqsrc": 30,
				"imei": self._imei,
				"language": language,
				"srcParams": json.dumps({
					"uidTo": str(userId)
				})
			})
		}
		
		data = await self._post("https://tt-friend-wpa.chat.zalo.me/api/friend/sendreq", params=params, data=payload)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def accept_friend_request(self, userId, language="vi"):
		"""Accept friend request from user by ID.
			
		Args:
			userId (int | str): User ID to accept friend request
			language (str): Response language or Zalo interface language

		Returns:
			object: `User` Friend accept requet response
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"fid": str(userId),
				"language": language
			})
		}
		
		data = await self._post("https://tt-friend-wpa.chat.zalo.me/api/friend/accept", params=params, data=payload)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def block_view_feed(self, userId, isBlockFeed):
		"""Block/Unblock friend view feed by ID.
			
		Args:
			userId (int | str): User ID to block/unblock view feed
			isBlockFeed (int): Block/Unblock friend view feed (1 = True | 0 = False)
		
		Returns:
			object: `User` Friend requet response
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"fid": str(userId),
				"isBlockFeed": isBlockFeed,
				"imei": self._imei
			})
		}
		
		data = await self._post("https://tt-friend-wpa.chat.zalo.me/api/friend/feed/block", params=params, data=payload)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def block_user(self, userId):
		"""Block user by ID.
			
		Args:
			userId (int | str): User ID to block
		
		Returns:
			object: `User` Block response
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"fid": str(userId),
				"imei": self._imei
			})
		}
		
		data = await self._post("https://tt-friend-wpa.chat.zalo.me/api/friend/block", params=params, data=payload)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def unblock_user(self, userId):
		"""Unblock user by ID.
			
		Args:
			userId (int | str): User ID to unblock
		
		Returns:
			object: `User` Unblock response
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"fid": str(userId),
				"imei": self._imei
			})
		}
		
		data = await self._post("https://tt-friend-wpa.chat.zalo.me/api/friend/unblock", params=params, data=payload)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	"""
	END USER ACTION METHODS
	"""
	
	"""
	GROUP ACTION METHODS
	"""
	
	async def create_group(self, name=None, description=None, members=[], nameChanged=1, createLink=1):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/group/create/v2", params=params)
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
	
	async def change_group_avatar(self, filePath, groupId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._post("https://tt-files-wpa.chat.zalo.me/api/group/upavatar", params=params, data=files)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def change_group_name(self, groupName, groupId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"gname": groupName,
				"grid": str(groupId)
			})
		}
		
		data = await self._post("https://tt-group-wpa.chat.zalo.me/api/group/updateinfo", params=params, data=payload)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def changeGroupDesc(self, groupDesc, groupId):
		"""Not Available Yet"""
	
	async def change_group_setting(self, groupId, defaultMode="default", **kwargs):
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
			defSetting = (await self.fetch_group_info(groupId)).gridInfoMap
			defSetting = defSetting[str(groupId)]["setting"]
			
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/group/setting/update", params=params)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def change_group_owner(self, newAdminId, groupId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/group/change-owner", params=params)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def add_users_to_group(self, user_ids, groupId):
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
		
		if user_ids and isinstance(user_ids, list):
			members = [str(user) for user in user_ids]
		else:
			members = [str(user_ids)]
			
		if members:
			for i in members:
				memberTypes.append(-1)
		
		params = {
			"zpw_ver": 647,
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
		
		data = await self._post("https://tt-group-wpa.chat.zalo.me/api/group/invite/v2", params=params, data=payload)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def kick_users_in_group(self, members, groupId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"grid": str(groupId),
				"members": members
			})
		}
		
		data = await self._post("https://tt-group-wpa.chat.zalo.me/api/group/kickout", params=params, data=payload)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def block_users_in_group(self, members, groupId):
		"""blocked members in group by ID.
		
		Client must be the Owner of the group.
		
		Args:
			members (str | list): One or More member IDs to block
			groupId (int | str): Group ID to block member from
			
		Returns:
			object: `Group` block members response
			dict: A dictionary/object containing error responses
			
		Raises:
			ZaloAPIException: If request failed
		"""
		if isinstance(members, list):
			members = [str(member) for member in members]
		else:
			members = [str(members)]
		
		params = {
			"zpw_ver": 647,
			"zpw_type": 30,
			"params": self._encode({
				"grid": str(groupId),
				"members": members
			})
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/group/blockedmems/add", params=params)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def unblock_users_in_group(self, members, groupId):
		"""unblock members in group by ID.
		
		Client must be the Owner of the group.
		
		Args:
			members (str | list): One or More member IDs to unblock
			groupId (int | str): Group ID to unblock member from
			
		Returns:
			object: `Group` unblock members response
			dict: A dictionary/object containing error responses
			
		Raises:
			ZaloAPIException: If request failed
		"""
		if isinstance(members, list):
			members = [str(member) for member in members]
		else:
			members = [str(members)]
		
		params = {
			"zpw_ver": 647,
			"zpw_type": 30,
			"params": self._encode({
				"grid": str(groupId),
				"members": members
			})
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/group/blockedmems/remove", params=params)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def add_group_admins(self, members, groupId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/group/admins/add", params=params)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	async def remove_group_admins(self, members, groupId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/group/admins/remove", params=params)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def pin_group_msg(self, pinMsg, groupId):
		"""Pin message in group by ID.
		
		Args:
			pinMsg (Message): Message Object to pin
			groupId (int | str): Group ID to pin message
		
		Returns:
			object: `Group` pin message status
			dict: A dictionary containing error_code & responses if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"grid": str(groupId),
				"type": 2,
				"color": -14540254,
				"emoji": "📌",
				"startTime": -1,
				"duration": -1,
				"repeat": 0,
				"src": -1,
				"imei": self._imei,
				"pinAct": 1
			}
		}
		
		if pinMsg.msgType == "webchat":
			
			payload["params"]["params"] = json.dumps({
				"client_msg_id": pinMsg.cliMsgId,
				"global_msg_id": pinMsg.msgId,
				"senderUid": str(int(pinMsg.uidFrom) or self.uid),
				"senderName": pinMsg.dName,
				"title": pinMsg.content,
				"msg_type": _util.getClientMessageType(pinMsg.msgType)
			})
		
		elif pinMsg.msgType == "chat.voice":
			
			payload["params"]["params"] = json.dumps({
				"client_msg_id": pinMsg.cliMsgId,
				"global_msg_id": pinMsg.msgId,
				"senderUid": str(int(pinMsg.uidFrom) or self.uid),
				"senderName": pinMsg.dName,
				"msg_type": _util.getClientMessageType(pinMsg.msgType)
			})
		
		elif pinMsg.msgType in ["chat.photo", "chat.video.msg"]:
			
			payload["params"]["params"] = json.dumps({
				"client_msg_id": pinMsg.cliMsgId,
				"global_msg_id": pinMsg.msgId,
				"senderUid": str(int(pinMsg.uidFrom) or self.uid),
				"senderName": pinMsg.dName,
				"thumb": pinMsg.content.thumb,
				"title": pinMsg.content.description,
				"msg_type": _util.getClientMessageType(pinMsg.msgType)
			})
		
		elif pinMsg.msgType == "chat.sticker":
			
			payload["params"]["params"] = json.dumps({
				"client_msg_id": pinMsg.cliMsgId,
				"global_msg_id": pinMsg.msgId,
				"senderUid": str(int(pinMsg.uidFrom) or self.uid),
				"senderName": pinMsg.dName,
				"extra": json.dumps({
					"id": pinMsg.content.id,
					"catId": pinMsg.content.catId,
					"type": pinMsg.content.type
				}),
				"msg_type": _util.getClientMessageType(pinMsg.msgType)
			})
		
		elif pinMsg.msgType in ["chat.recommended", "chat.link"]:
			
			extra = json.loads(pinMsg.content.params)
			payload["params"]["params"] = json.dumps({
				"client_msg_id": pinMsg.cliMsgId,
				"global_msg_id": pinMsg.msgId,
				"senderUid": str(int(pinMsg.uidFrom) or self.uid),
				"senderName": pinMsg.dName,
				"href": pinMsg.content.href,
				"thumb": pinMsg.content.thumb or "",
				"title": pinMsg.content.title,
				"linkCaption": "https://vrxx1337.vercel.app",
				"redirect_url": extra.get("redirect_url", ""),
				"streamUrl": extra.get("streamUrl", ""),
				"artist": extra.get("artist", ""),
				"stream_icon": extra.get("stream_icon", ""),
				"type": 2,
				"extra": json.dumps({
					"action": pinMsg.content.action,
					"params": json.dumps({
						"mediaTitle": extra.get("mediaTitle", ""),
						"artist": extra.get("artist", ""),
						"src": extra.get("src", ""),
						"stream_icon": extra.get("stream_icon", ""),
						"streamUrl": extra.get("streamUrl", ""),
						"type": 2
					})
				}),
				"msg_type": _util.getClientMessageType(pinMsg.msgType)
			})
		
		elif pinMsg.msgType == "chat.location.new":
			
			payload["params"]["params"] = json.dumps({
				"client_msg_id": pinMsg.cliMsgId,
				"global_msg_id": pinMsg.msgId,
				"senderUid": str(int(pinMsg.uidFrom) or self.uid),
				"senderName": pinMsg.dName,
				"msg_type": _util.getClientMessageType(pinMsg.msgType),
				"title": pinMsg.content.title or pinMsg.content.description
			})
		
		elif pinMsg.msgType == "share.file":
			
			extra = json.loads(pinMsg.content.params)
			payload["params"]["params"] = json.dumps({
				"client_msg_id": pinMsg.cliMsgId,
				"global_msg_id": pinMsg.msgId,
				"senderUid": str(int(pinMsg.uidFrom) or self.uid),
				"senderName": pinMsg.dName,
				"title": pinMsg.content.title,
				"extra": json.dumps({
					"fileSize": "7295",
					"checksum": extra.get("checksum", ""),
					"fileExt": extra.get("fileExt", ""),
					"tWidth": extra.get("tWidth", 0),
					"tHeight": extra.get("tHeight", 0),
					"duration": extra.get("duration", 0),
					"fType": extra.get("fType", 0),
					"fdata": extra.get("fdata", ""),
				}),
				"msg_type": _util.getClientMessageType(pinMsg.msgType)
			})
		
		elif pinMsg.msgType == "chat.gif":
			
			payload["params"]["params"] = json.dumps({
				"client_msg_id": pinMsg.cliMsgId,
				"global_msg_id": pinMsg.msgId,
				"senderUid": str(int(pinMsg.uidFrom) or self.uid),
				"senderName": pinMsg.dName,
				"thumb": pinMsg.content.thumb,
				"msg_type": _util.getClientMessageType(pinMsg.msgType)
			})
		
		payload["params"] = self._encode(payload["params"])
		data = await self._post("https://groupboard-wpa.chat.zalo.me/api/board/topic/createv2", params=params, data=payload)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def unpin_group_msg(self, pinId, pinTime, groupId):
		"""Unpin message in group by ID.
		
		Args:
			pinId (int | str): Pin ID to unpin
			pinTime (int): Pin start time
			groupId (int | str): Group ID to unpin message
		
		Returns:
			object: `Group` unpin message status
			dict: A dictionary containing error_code & responses if failed
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30,
			"params": self._encode({
				"grid": str(groupId),
				"imei": self._imei,
				"topic": {
					"topicId": str(pinId),
					"topicType": 2
				},
				"boardVersion": int(pinTime)
			})
		}
		
		data = await self._get("https://groupboard-wpa.chat.zalo.me/api/board/unpinv2", params=params)
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
				
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def delete_group_msg(self, msgId, ownerId, clientMsgId, groupId):
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
			"zpw_ver": 647,
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
		
		data = await self._post("https://tt-group-wpa.chat.zalo.me/api/group/deletemsg", params=params, data=payload)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def view_group_pending(self, groupId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/group/pending-mems/list", params=params)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def handle_group_pending(self, members, groupId, isApprove=True):
		"""Approve/Deny pending users to the group from the group"s approval.
		
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/group/pending-mems/review", params=params)
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
				
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def view_poll_detail(self, pollId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		data = await self._get("https://tt-group-wpa.chat.zalo.me/api/poll/detail", params=params)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def create_poll(
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
			hideVotePreview (bool): Hide voting results when haven"t voted
			isAnonymous (bool): Hide poll voters
			
		Returns:
			object: `Group` poll create data
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
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
		
		data = await self._post("https://tt-group-wpa.chat.zalo.me/api/poll/create", params=params, data=payload)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def lock_poll(self, pollId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"poll_id": int(pollId),
				"imei": self._imei
			})
		}
		
		data = await self._post("https://tt-group-wpa.chat.zalo.me/api/poll/end", params=params, data=payload)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def disperse_group(self, groupId):
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": self._encode({
				"grid": str(groupId),
				"imei": self._imei
			})
		}
		
		data = await self._post("https://tt-group-wpa.chat.zalo.me/api/group/disperse", params=params, data=payload)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	"""
	END GROUP ACTION METHODS
	"""
	
	"""
	SEND METHODS
	"""
	
	async def send(self, message, thread_id, thread_type=ThreadType.USER, mark_message=None, ttl=0):
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
			return await self.send_mention_message(message, thread_id, ttl)
		else:
			return await self.send_message(message, thread_id, thread_type, mark_message, ttl)
	
	async def send_message(self, message, thread_id, thread_type, mark_message=None, ttl=0):
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
			"zpw_ver": 647,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"message": message.text,
				"clientId": _util.now(),
				"imei": self._imei,
				"ttl": ttl,
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
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def reply_message(self, message, replyMsg, thread_id, thread_type, ttl=0):
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
			"zpw_ver": 647,
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
				"qmsgType": _util.getClientMessageType(replyMsg.msgType),
				"qmsg": replyMsg.content,
				"qmsgTs": replyMsg.ts,
				"qmsgAttach": json.dumps({}),
				"qmsgTTL": 0,
				"ttl": ttl
			}
		}
		
		if not isinstance(replyMsg.content, str):
			payload["params"]["qmsg"] = ""
			payload["params"]["qmsgAttach"] = json.dumps(replyMsg.content.toDict())
		
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
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_mention_message(self, message, groupId, ttl=0):
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
			"zpw_ver": 647,
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
				"ttl": ttl
			}
		}
		
		if message.style:
			payload["params"]["textProperties"] = message.style
		
		payload["params"] = self._encode(payload["params"])
		
		data = await self._post("https://tt-group-wpa.chat.zalo.me/api/group/mention", params=params, data=payload)
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
			
			return Group.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def undo_message(self, msgId, cliMsgId, thread_id, thread_type):
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
			"zpw_ver": 647,
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
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_reaction(self, messageObject, reactionIcon, thread_id, thread_type, reactionType=75):
		"""Reaction message by ID.
			
		Args:
			messageObject (Message): Message Object to reaction
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
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"react_list": [{
					"message": json.dumps({
						"rMsg": [{
							"gMsgID": int(messageObject.msgId),
							"cMsgID": int(messageObject.cliMsgId),
							"msgType": _util.getClientMessageType(messageObject.msgType)
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
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_multi_reaction(self, reactionObj, reactionIcon, thread_id, thread_type, reactionType=75):
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
			"zpw_ver": 647,
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
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_remote_file(self, fileUrl, thread_id, thread_type, fileName="default", fileSize=None, extension="vrxx", ttl=0):
		"""Send File to a User/Group with url.
			
		Args:
			fileUrl (str): File url to send
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			fileName (str): File name to send
			fileSize (int): File size to send
			extension (str): type of file to send (py, txt, mp4, ...)
			
		Returns:
			object: `User/Group` (Returns msg ID just sent)
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		try:
			async with aiohttp.ClientSession() as session:
				async with session.get(fileUrl) as response:
					if response.status == 200:
						print(type(await response.read()))
						fileSize = fileSize if fileSize else int(response.headers.get("Content-Length", len(await response.read())))
					else:
						fileSize = fileSize if fileSize else 0
					
					fileChecksum = hashlib.md5(await response.read()).hexdigest()
		
		except Exception:
			raise ZaloAPIException("Unable to get url content")
		
		has_extension = fileName.rsplit(".")
		extension = has_extension[-1:][0] if len(has_extension) >= 2 else extension
		
		params = {
			"zpw_ver": 647,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"fileId": str(int(_util.now())),
				"checksum": fileChecksum,
				"checksumSha": "",
				"extension": extension,
				"totalSize": fileSize,
				"fileName": fileName,
				"clientId": _util.now(),
				"fType": 1,
				"fileCount": 0,
				"fdata": "{}",
				"fileUrl": fileUrl,
				"zsource": 401,
				"ttl": ttl
			}
		}
		
		if thread_type == ThreadType.USER:
			url = "https://tt-files-wpa.chat.zalo.me/api/message/asyncfile/msg"
			payload["params"]["toid"] = str(thread_id)
			payload["params"]["imei"] = self._imei
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-files-wpa.chat.zalo.me/api/group/asyncfile/msg"
			payload["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_remote_video(self, videoUrl, thumbnailUrl, duration, thread_id, thread_type, width=1280, height=720, message=None, ttl=0):
		"""Send (Forward) video to a User/Group with url.
		
		Warning:
			This is a feature created through the forward function.
			Because Zalo Web does not allow viewing videos.
		
		Args:
			videoUrl (str): Video link to send
			thumbnailUrl (str): Thumbnail link for video
			duration (int | str): Time for video (ms)
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			width (int): Width of the video
			height (int): Height of the video
			message (Message): Message to send with video
		
		Returns:
			object: `User/Group` (Returns msg ID just sent)
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		try:
			async with aiohttp.ClientSession() as session:
				async with session.head(videoUrl) as response:
					if response.status == 200:
						fileSize = int(response.headers.get("Content-Length", len(await response.read())))
					else:
						fileSize = 0
		
		except Exception as e:
			raise ZaloAPIException(f"Unable to get url content: {e}")
		
		params = {
			"zpw_ver": 647,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"clientId": str(_util.now()),
				"ttl": ttl,
				"zsource": 704,
				"msgType": 5,
				"msgInfo": json.dumps({
					"videoUrl": str(videoUrl),
					"thumbUrl": str(thumbnailUrl),
					"duration": int(duration),
					"width": int(width),
					"height": int(height),
					"fileSize": fileSize,
					"properties": {
						"color": -1,
						"size": -1,
						"type": 1003,
						"subType": 0,
						"ext": {
							"sSrcType": -1,
							"sSrcStr": "",
							"msg_warning_type": 0
						}
					},
					"title": message.text or "" if message else ""
				})
			}
		}
		
		if message and message.mention:
			payload["params"]["mentionInfo"] = message.mention
		
		if thread_type == ThreadType.USER:
			url = "https://tt-files-wpa.chat.zalo.me/api/message/forward"
			payload["params"]["toId"] = str(thread_id)
			payload["params"]["imei"] = self._imei
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-files-wpa.chat.zalo.me/api/group/forward"
			payload["params"]["visibility"] = 0
			payload["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_remote_voice(self, voiceUrl, thread_id, thread_type, fileSize=None, ttl=0):
		"""Send voice by url.
			
		Args:
			voiceUrl (str): Voice link to send
			thread_id (int | str): User/Group ID to change status in
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			fileSize (int | str): Voice content length (size) to send
		
		Returns:
			object: `User/Group` response
		
		Raises:
			ZaloAPIException: If request failed
		"""
		async with aiohttp.ClientSession() as session:
			async with session.get(voiceUrl) as response:
				if response.status == 200:
					fileSize = fileSize if fileSize else int(response.headers.get("Content-Length", len(await response.read())))
				else:
					fileSize = fileSize if fileSize else 0
		
		params = {
			"zpw_ver": 647,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"ttl": ttl,
				"zsource": -1,
				"msgType": 3,
				"clientId": str(_util.now()),
				"msgInfo": json.dumps({
					"voiceUrl": str(voiceUrl),
					"m4aUrl": str(voiceUrl),
					"fileSize": int(fileSize)
				})
			}
		}
		
		if thread_type == ThreadType.USER:
			url = "https://tt-files-wpa.chat.zalo.me/api/message/forward"
			payload["params"]["toId"] = str(thread_id)
			payload["params"]["imei"] = self._imei
		else:
			url = "https://tt-files-wpa.chat.zalo.me/api/group/forward"
			payload["params"]["visibility"] = 0
			payload["params"]["grid"] = str(thread_id)
		
		payload["params"] = self._encode(payload["params"])
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_remote_image(self, imageUrl, thread_id, thread_type, width=2560, height=2560, message=None, ttl=0, custom_payload=None):
		"""Send Image to a User/Group with url.
			
		Args:
			imageUrl (str): Image url to send
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			width (int): Image width to send
			height (int): Image height to send
			message (Message): Message to send with image
			
		Returns:
			object: `User/Group` objects response
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30,
			"nretry": 0
		}
		
		if custom_payload:
			if thread_type == ThreadType.USER:
				url = "https://tt-files-wpa.chat.zalo.me/api/message/photo_original/send"
			elif thread_type == ThreadType.GROUP:
				url = "https://tt-files-wpa.chat.zalo.me/api/group/photo_original/send"
			else:
				raise ZaloUserError("Thread type is invalid")
			
			payload = custom_payload
		
		else:
			try:
				async with aiohttp.ClientSession() as session:
					async with session.head(imageUrl) as response:
						if response.status == 200:
							fileSize = int(response.headers.get("Content-Length", len(await response.read())))
						else:
							fileSize = 344622
			
			except Exception as e:
				raise ZaloAPIException(f"Unable to get url content: {e}")
			
			payload = {
				"params": {
					"photoId": int(_util.now() * 2),
					"clientId": int(_util.now() - 1000),
					"desc": message.text if message else "" or "",
					"width": width,
					"height": height,
					"rawUrl": str(imageUrl),
					"thumbUrl": str(imageUrl),
					"hdUrl": str(imageUrl),
					"thumbSize": str(fileSize),
					"fileSize": str(fileSize),
					"hdSize": str(fileSize),
					"zsource": -1,
					"jcp": json.dumps({"sendSource": 1, "convertible": "jxl"}),
					"ttl": ttl,
					"imei": self._imei
				}
			}
			
			if message and message.mention:
				payload["params"]["mentionInfo"] = message.mention
			
			if thread_type == ThreadType.USER:
				url = "https://tt-files-wpa.chat.zalo.me/api/message/photo_original/send"
				payload["params"]["toid"] = str(thread_id)
				payload["params"]["normalUrl"] = imageUrl
			elif thread_type == ThreadType.GROUP:
				url = "https://tt-files-wpa.chat.zalo.me/api/group/photo_original/send"
				payload["params"]["grid"] = str(thread_id)
				payload["params"]["oriUrl"] = imageUrl
			else:
				raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_local_image(self, imagePath, thread_id, thread_type, width=2560, height=2560, message=None, ttl=0, custom_payload=None):
		"""Send Image to a User/Group with local file.
			
		Args:
			imagePath (str): Image directory to send
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			width (int): Image width to send
			height (int): Image height to send
			message (Message): Message to send with image
			
		Returns:
			object: `User/Group` objects response
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30,
			"nretry": 0
		}
		
		if custom_payload:
			if thread_type == ThreadType.USER:
				url = "https://tt-files-wpa.chat.zalo.me/api/message/photo_original/send"
			elif thread_type == ThreadType.GROUP:
				url = "https://tt-files-wpa.chat.zalo.me/api/group/photo_original/send"
			else:
				raise ZaloUserError("Thread type is invalid")
			
			payload = custom_payload
		
		else:
			uploadImage = await self._uploadImage(imagePath, thread_id, thread_type)
			
			payload = {
				"params": {
					"photoId": uploadImage.get("photoId", int(_util.now() * 2)),
					"clientId": uploadImage.get("clientFileId", int(_util.now() - 1000)),
					"desc": message.text if message else "" or "",
					"width": width,
					"height": height,
					"rawUrl": uploadImage["normalUrl"],
					"thumbUrl": uploadImage["thumbUrl"],
					"hdUrl": uploadImage["hdUrl"],
					"thumbSize": "53932",
					"fileSize": "247671",
					"hdSize": "344622",
					"zsource": -1,
					"jcp": json.dumps({"sendSource": 1, "convertible": "jxl"}),
					"ttl": ttl,
					"imei": self._imei
				}
			}
		
			if message and message.mention:
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
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_multi_local_image(self, imagePathList, thread_id, thread_type, width=2560, height=2560, message=None, ttl=0):
		"""Send Image to a User/Group with local file.
			
		Args:
			imagePathList (list): List image directory to send
			width (int): Image width to send
			height (int): Image height to send
			message (Message): Message to send with image
			multiple (Boolen): Send multiple images at once.
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` objects
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		uploadData = []
		
		if not isinstance(imagePathList, list) or len(imagePathList) < 1:
			raise ZaloUserError("image path must be a list to be able to send multiple at once.")
		
		groupLayoutId = str(_util.now())
		
		for i, imagePath in enumerate(imagePathList):
			uploadImage = await self._uploadImage(imagePath, thread_id, thread_type)
		
			payload = {
				"params": {
					"photoId": uploadImage.get("photoId", int(_util.now() * 2)),
					"clientId": uploadImage.get("clientFileId", int(_util.now() - 1000)),
					"desc": message.text if message else "" or "",
					"width": width,
					"height": height,
					"groupLayoutId": groupLayoutId,
					"totalItemInGroup": len(imagePathList),
					"isGroupLayout": 1,
					"idInGroup": i,
					"rawUrl": uploadImage["normalUrl"],
					"thumbUrl": uploadImage["thumbUrl"],
					"hdUrl": uploadImage["hdUrl"],
					"thumbSize": "53932",
					"fileSize": "247671",
					"hdSize": "344622",
					"zsource": -1,
					"jcp": json.dumps({"sendSource": 1, "convertible": "jxl"}),
					"ttl": ttl,
					"imei": self._imei
				}
			}
		
			if message and message.mention:
				payload["params"]["mentionInfo"] = message.mention
			
			if thread_type == ThreadType.USER:
				payload["params"]["toid"] = str(thread_id)
				payload["params"]["normalUrl"] = uploadImage["normalUrl"]
			elif thread_type == ThreadType.GROUP:
				payload["params"]["grid"] = str(thread_id)
				payload["params"]["oriUrl"] = uploadImage["normalUrl"]
			else:
				raise ZaloUserError("Thread type is invalid")
			
			data = await self.send_local_image(imagePath, thread_id, thread_type, width, height, message, custom_payload=payload)
			uploadData.append(data.toDict())
		
		return (
			Group.fromDict(uploadData, None) 
			if thread_type == ThreadType.GROUP else 
			User.fromDict(uploadData, None)
		)
	
	async def send_local_gif(self, gifPath, thumbnailUrl, thread_id, thread_type, gifName="vrxx.gif", width=500, height=500, ttl=0):
		"""Send Gif to a User/Group with local file.
			
		Args:
			gifPath (str): Gif directory to send
			gifName (str): Gif name to send
			width (int): Gif width to send
			height (int): Gif height to send
			thumbnailUrl (str): Thumbnail of gif to send
			thread_id (int | str): User/Group ID to send to.
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			
		Returns:
			object: `User/Group` objects
			dict: A dictionary containing error responses
		
		Raises:
			ZaloAPIException: If request failed
		"""
		if not os.path.exists(gifPath):
			raise ZaloUserError(f"{gifPath} not found")
			
		files = [("chunkContent", open(gifPath, "rb"))]
		fileSize = len(open(gifPath, "rb").read())
		gifName = gifName if gifName else gifPath if "/" not in gifPath else gifPath.rstrip("/")[1]
		fileChecksum = hashlib.md5(open(gifPath, "rb").read()).hexdigest()
		
		params = {
			"zpw_ver": 647,
			"zpw_type": 30,
			"type": 1,
			"params": {
				"clientId": str(_util.now()),
				"fileName": gifName,
				"totalSize": fileSize,
				"width": width,
				"height": height,
				"msg": "abcxyz",
				"type": 1,
				"ttl": ttl,
				"thumb": str(thumbnailUrl),
				"checksum": fileChecksum,
				"totalChunk": 1,
				"chunkId": 1
			}
		}
		
		if thread_type == ThreadType.USER:
			url = "https://tt-files-wpa.chat.zalo.me/api/message/gif"
			params["params"]["toid"] = str(thread_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-files-wpa.chat.zalo.me/api/group/gif"
			params["params"]["visibility"] = 0
			params["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		params["params"] = self._encode(params["params"])
		
		data = await self._post(url, params=params, data=files)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_sticker(self, stickerId, cateId, thread_id, thread_type, ttl=0):
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
			"zpw_ver": 647,
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
				"ttl": ttl,
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
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
		
	async def send_custom_sticker(
		self,
		staticImgUrl,
		animationImgUrl,
		thread_id,
		thread_type,
		reply=None,
		width=None,
		height=None,
		contentId=None,
		ttl=0
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
		width = int(width) if width else 0
		height = int(height) if height else 0
		params = {
			"zpw_ver": 647,
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
				"width": width,
				"height": height,
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
				"contentId": contentId or _util.now(),
				"thumb_height": width,
				"thumb_width": height,
				"webp": json.dumps({
					"width": width,
					"height": height,
					"url": animationImgUrl
				}),
				"zsource": -1,
				"ttl": ttl
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
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_link(self, linkUrl, title, thread_id, thread_type, thumbnailUrl=None, domainUrl=None, desc=None, message=None, ttl=0):
		"""Send link to a User/Group with url.
			
		Args:
			linkUrl (str): Link url to send
			domainUrl (str): Main domain of Link to send (eg: github.com)
			thread_id (int | str): User/Group ID to send link to
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
			thumbnailUrl (str): Thumbnail link url for card to send
			title (str): Title for card to send
			desc (str): Description for card to send
			message (Message): Message object to send with the link
			
		Returns:
			object: `User/Group` message id response
			dict: A dictionary containing error responses
			
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"msg": message.text if message else "" or "",
				"href": linkUrl,
				"src": domainUrl or "",
				"title": str(title),
				"desc": desc or "",
				"thumb": thumbnailUrl or "",
				"type": 0,
				"media": json.dumps({
					"type": 0,
					"count": 0,
					"mediaTitle": "",
					"artist": "",
					"streamUrl": "",
					"stream_icon": ""
				}),
				"ttl": ttl,
				"clientId": _util.now()
			}
		}
		
		if message and message.mention:
			payload["params"]["mentionInfo"] = message.mention
		
		if thread_type == ThreadType.USER:
			url = "https://tt-chat4-wpa.chat.zalo.me/api/message/link"
			payload["params"]["toid"] = str(thread_id)
		elif thread_type == ThreadType.GROUP:
			url = "https://tt-group-wpa.chat.zalo.me/api/group/sendlink"
			payload["params"]["imei"] = self._imei
			payload["params"]["grid"] = str(thread_id)
		else:
			raise ZaloUserError("Thread type is invalid")
		
		payload["params"] = self._encode(payload["params"])
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_report(self, user_id, reason=0, content=None):
		"""Send report to Zalo.
		
		Args:
			reason (int): Reason for reporting
				1 = Nội dung nhạy cảm
				2 = Làm phiền
				3 = Lừa đảo
				0 = custom
			content (str): Report content (work if reason = custom)
			user_id (int | str): User ID to report
		
		Returns:
			object: `User` send report response
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30
		}
		
		payload = {
			"params": {
				"idTo": str(user_id),
				"objId": "person.profile"
			}
		}
		
		content = content if content and not reason else "" if not content and not reason else ""
		if content:
			payload["params"]["content"] = content
		
		payload["params"]["reason"] = str( random.randint(1, 3) if not content else reason )
		payload["params"] = self._encode(payload["params"])
		
		data = await self._post("https://tt-profile-wpa.chat.zalo.me/api/report/abuse-v2", params=params, data=payload)
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
			
			return User.fromDict(results, None)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def send_business_card(self, userId, qrCodeUrl, thread_id, thread_type, phone=None, ttl=0):
		"""Send business card by user ID.
			
		Args:
			userId (int | str): Business card user ID
			qrCodeUrl (str): QR Code link with business card profile information
			phone (int | str): Send business card with phone number
			thread_id (int | str): User/Group ID to change status in
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
		
		Returns:
			object: `User/Group` send business card response
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
			"zpw_type": 30,
			"nretry": 0
		}
		
		payload = {
			"params": {
				"ttl": ttl,
				"msgType": 6,
				"clientId": str(_util.now()),
				"msgInfo": {
					"contactUid": str(userId),
					"qrCodeUrl": str(qrCodeUrl)
				}
			}
		}
		
		if phone:
			payload["params"]["msgInfo"]["phone"] = str(phone)
		
		if thread_type == ThreadType.USER:
			url = "https://tt-files-wpa.chat.zalo.me/api/message/forward"
			payload["params"]["toId"] = str(thread_id)
			payload["params"]["imei"] = self._imei
		else:
			url = "https://tt-files-wpa.chat.zalo.me/api/group/forward"
			payload["params"]["visibility"] = 0
			payload["params"]["grid"] = str(thread_id)
		
		payload["params"]["msgInfo"] = json.dumps(payload["params"]["msgInfo"])
		payload["params"] = self._encode(payload["params"])
		
		data = await self._post(url, params=params, data=payload)
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
				Group.fromDict(results, None) 
				if thread_type == ThreadType.GROUP else 
				User.fromDict(results, None)
			)
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	"""
	END SEND METHODS
	"""
	
	async def set_typing(self, thread_id, thread_type):
		"""Set users typing status.
			
		Args:
			thread_id (int | str): User/Group ID to change status in
			thread_type (ThreadType): ThreadType.USER, ThreadType.GROUP
		
		Raises:
			ZaloAPIException: If request failed
		"""
		params = {
			"zpw_ver": 647,
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
		
		data = await self._post(url, params=params, data=payload)
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			results = self._decode(results)
			return True
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def mark_as_delivered(self, ctx):
		"""Mark a message as delivered.
		
		Args (Context):
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
		msgId = ctx.message_id
		method = ctx.message_object.msgType
		senderId = ctx.author_id
		cliMsgId = ctx.message_object.cliMsgId
		thread_id = ctx.thread_id
		thread_type = ctx.thread_type
		
		destination_id = "0" if thread_type == ThreadType.USER else thread_id
		
		params = {
			"zpw_ver": 647,
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
		
		data = await self._post(url, params=params, data=payload)
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			context = ContextObject.fromDict({"msgId": msgId, "thread_id": thread_id, "thread_type": thread_type})
			await self.on_message_delivered(context)
			return True
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	async def mark_as_read(self, ctx):
		"""Mark a message as read.
		
		Args (Context):
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
		msgId = ctx.message_id
		method = ctx.message_object.msgType
		senderId = ctx.author_id
		cliMsgId = ctx.message_object.cliMsgId
		thread_id = ctx.thread_id
		thread_type = ctx.thread_type
		
		destination_id = "0" if thread_type == ThreadType.USER else thread_id
		
		params = {
			"zpw_ver": 647,
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
		
		data = await self._post(url, params=params, data=payload)
		results = data.get("data") if data.get("error_code") == 0 else None
		if results:
			context = ContextObject.fromDict({"msgId": msgId, "thread_id": thread_id, "thread_type": thread_type})
			await self.on_marked_seen(context)
			return True
			
		error_code = data.get("error_code")
		error_message = data.get("error_message") or data.get("data")
		raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")
	
	"""
	LISTEN METHODS
	"""
	
	async def _listen_req(self, delay=1, reconnect=5):
		self._condition.clear()
		HasRead = set()
		
		while not self._condition.is_set():
			try:
				await self.on_listening()
				self._listening = True
				
				while not self._condition.is_set():
					ListenTime = int((time.time() - 10) * 1000)
					
					if len(HasRead) > 10000000:
						HasRead.clear()
					
					messages = await self.get_last_msgs()
					groupmsg = messages.groupMsgs
					messages = messages.msgs
					
					loop = asyncio.get_event_loop()
					for message in messages + groupmsg:
						if int(message["ts"]) >= ListenTime and message["msgId"] not in HasRead:
							
							HasRead.add(message["msgId"])
							msgObj = MessageObject.fromDict(message, None)
							
							if message in messages:
								
								context = {"message_id": msgObj.msgId, "author_id": str(int(msgObj.uidFrom) or self.uid), "message": msgObj.content, "message_object": msgObj, "thread_id": str(int(msgObj.uidFrom) or msgObj.idTo), "thread_type": ThreadType.USER}
								context = ContextObject.fromDict(context)
								loop.create_task(self.onMessage(context))
							
							else:
								
								context = {"message_id": msgObj.msgId, "author_id": str(int(msgObj.uidFrom) or self.uid), "message": msgObj.content, "message_object": msgObj, "thread_id": str(int(msgObj.idTo) or msgObj.idTo), "thread_type": ThreadType.GROUP}
								context = ContextObject.fromDict(context)
								loop.create_task(self.onMessage(context))
					
					await asyncio.sleep(delay)
			
			except asyncio.CancelledError:
				self._condition.set()
				logger.warning("Stop Listen Because KeyboardInterrupt Exception!")
				break
			
			except Exception as e:
				await self.on_error_callback(e)
			
			await asyncio.sleep(reconnect)
	
	
	async def _listen_ws(self, thread=False, reconnect=5):
		self._condition.clear()
		params = {"zpw_ver": 647, "zpw_type": 30, "t": _util.now()}
		url = self._state._config["zpw_ws"][0] + "?" + urllib.parse.urlencode(params)
		
		user_agent = self._state._headers.get("User-Agent") or _util.HEADERS["User-Agent"]
		raw_cookies = _util.dict_to_raw_cookies(await self._state.get_cookies())
		
		if not raw_cookies:
			raise ZaloUserError("Unable to load cookies! Probably due to incorrect cookie format (cookies must be dict)")
		
		headers = {
			"Accept-Encoding": "gzip, deflate, br, zstd",
			"Accept-Language": "en-US,en;q=0.9",
			"Cache-Control": "no-cache",
			"Connection": "Upgrade",
			"Host": urllib.parse.urlparse(url).netloc,
			"Origin": "https://chat.zalo.me",
			"Pargma": "no-cache",
			"Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
			"Sec-Websocket-Version": "13",
			"Upgrade": "websocket",
			"User-Agent": user_agent,
			"Cookie": raw_cookies
		}
		
		while not self._condition.is_set():
			try:
				async with connect(url, extra_headers=headers, ping_timeout=None) as ws:
					loop = asyncio.get_event_loop()
					await self.on_listening()
					self._listening = True
					
					while not self._condition.is_set():
						try:
							
							data = await asyncio.wait_for(ws.recv(), timeout=60)
							
							if not isinstance(data, bytes):
								continue
							
							encodedHeader = data[:4]
							n, cmd, s = _util.getHeader(encodedHeader)
							
							dataToDecode = data[4:]
							decodedData = dataToDecode.decode("utf-8")
							if not decodedData:
								continue
							
							parsed = json.loads(decodedData)
							if n == 1 and cmd == 1 and s == 1 and "key" in parsed:
								self.ws_key = parsed["key"]
								continue
							
							if not hasattr(self, "ws_key"):
								logger.error("Unable to decrypt data because key not found")
								continue
							
							parsedData = _util.zws_decode(parsed, self.ws_key)
							if n == 1 and cmd == 3000 and s == 0:
								logger.warning("Another connection is opened, closing this one")
								await ws.close()
							
							elif n == 1 and cmd == 501 and s == 0:
								userMsgs = parsedData["data"]["msgs"]
								
								for message in userMsgs:
									msgObj = MessageObject.fromDict(message, None)
									context = {"message_id": msgObj.msgId, "author_id": str(int(msgObj.uidFrom) or self.uid), "message": msgObj.content, "message_object": msgObj, "thread_id": str(int(msgObj.uidFrom) or msgObj.idTo), "thread_type": ThreadType.USER}
									context = ContextObject.fromDict(context)
									[
										loop.create_task(self.onMessage(context))
										if thread else
										await self.onMessage(context)
									]
							
							elif n == 1 and cmd == 521 and s == 0:
								groupMsgs = parsedData["data"]["groupMsgs"]
								
								for message in groupMsgs:
									
									try:
										messages = (await self.get_recent_group(message["idTo"]))["groupMsgs"]
										message = next((msg for msg in messages if msg["msgId"] == message["msgId"]), message)
									except:
										pass
									
									msgObj = MessageObject.fromDict(message, None)
									context = {"message_id": msgObj.msgId, "author_id": str(int(msgObj.uidFrom) or self.uid), "message": msgObj.content, "message_object": msgObj, "thread_id": str(int(msgObj.idTo) or msgObj.idTo), "thread_type": ThreadType.GROUP}
									context = ContextObject.fromDict(context)
									[
										loop.create_task(self.onMessage(context))
										if thread else
										await self.onMessage(context)
									]
							
							elif n == 1 and cmd in [502, 522, 504, 524] and s == 0:
								# Delivereds, Seen, Clear Unread, ...
								continue
							
							elif n == 1 and cmd == 602 and s == 0:
								# Typing Event
								continue
							
							elif n == 1 and cmd == 601 and s == 0:
								controls = parsedData["data"].get("controls", [])
								for control in controls:
									if control["content"]["act_type"] == "group":
										
										if control["content"]["act"] == "join_reject":
											continue
										
										groupEventData = json.loads(control["content"]["data"]) if isinstance(control["content"]["data"], str) else control["content"]["data"]
										groupEventType = _util.getGroupEventType(control["content"]["act"])
										context = {"event_data": groupEventData, "event_type": groupEventType}
										context = EventObject.fromDict(context)
										[
											loop.create_task(self.on_event(context))
											if thread else
											await self.on_event(context)
										]
								
								continue
							
							elif cmd == 612:
								reacts = parsedData["data"].get("reacts", [])
								reactGroups = parsedData["data"].get("reactGroups", [])
								
								for react in reacts:
									react["content"] = json.loads(react["content"])
									msgObj = MessageObject.fromDict(react, None)
									context = {"message_id": msgObj.msgId, "author_id": str(int(msgObj.uidFrom) or self.uid), "message": msgObj.content, "message_object": msgObj, "thread_id": str(int(msgObj.uidFrom) or msgObj.idTo), "thread_type": ThreadType.USER}
									context = ContextObject.fromDict(context)
									[
										loop.create_task(self.onMessage(context))
										if thread else
										await self.onMessage(context)
									]
								
								for reactGroup in reactGroups:
									reactGroup["content"] = json.loads(reactGroup["content"])
									msgObj = MessageObject.fromDict(reactGroup, None)
									context = {"message_id": msgObj.msgId, "author_id": str(int(msgObj.uidFrom) or self.uid), "message": msgObj.content, "message_object": msgObj, "thread_id": str(int(msgObj.idTo) or msgObj.idTo), "thread_type": ThreadType.GROUP}
									context = ContextObject.fromDict(context)
									[
										loop.create_task(self.onMessage(context))
										if thread else
										await self.onMessage(context)
									]
							
							else:
								continue
						
						except asyncio.CancelledError:
							self._condition.set()
							logger.warning("Stop Listen Because KeyboardInterrupt Exception!")
							pid = os.getpid()
							os.kill(pid, signal.SIGTERM)
						
						except asyncio.TimeoutError:
							break
						
						except (
							websockets.ConnectionClosedOK,
							websockets.ConnectionClosedError,
							websockets.exceptions.ConnectionClosedOK,
							websockets.exceptions.ConnectionClosedError
						):
							break
						
						except Exception as e:
							self._listening = False
							self._condition.set()
							await self.on_error_callback(e)
							break
			
			except Exception as e:
				self._listening = False
				self._condition.set()
				await self.on_error_callback(e)
				break
			
			await asyncio.sleep(reconnect)
			await self._listen_ws(thread, reconnect)
	
	
	def startListening(self, delay=1, thread=False, type="websocket", reconnect=5):
		"""Start listening from an external event loop.
		
		Args:
			delay (int): Delay time each time fetching a message
			test (bool): Listen `test` or `main` mode, Default: False (Main Mode)
			thread (bool): Handle messages within the thread (Default: False)
			type (str): Type of listening (Default: websocket)
		
		Raises:
			ZaloAPIException: If request failed
		"""
		self._condition.clear()
		if str(type).lower() == "websocket":
			
			if self._state._config.get("zpw_ws"):
				asyncio.run(self._listen_ws(thread))
				
			else:
				logger.debug("WebSocket url not found. Listen will switch to `requests` mode")
				asyncio.run(self._listen_req(delay))
		
		elif str(type).lower() == "requests":
			asyncio.run(self._listen_req(delay))
		
		else:
			raise ZaloUserError("Invalid listen type, only `websocket` or `requests`")
	
	def stopListening(self):
		"""Stop the listening loop."""
		self._listening = False
		self._condition.set()
	
	def listen(self, delay=1, thread=False, type="websocket", reconnect=5):
		"""Initialize and runs the listening loop continually.
		
		Args:
			delay (int): Delay time for each message fetch (Default: 1)
			thread (bool): Handle messages within the thread (Default: False)
			type (str): Type of listening (Default: websocket)
		
		"""
		self.startListening(delay, thread, type, reconnect)
	
	"""
	END LISTEN METHODS
	"""
	
	"""
	EVENTS
	"""
	
	async def on_logging_in(self, phone=None):
		"""Called when the client is logging in.
			
		Args:
			phone: The phone number of the client
		"""
		logger.debug("Logging in {}...".format(phone))
	
	
	async def on_logged_in(self, phone=None):
		"""Called when the client is successfully logged in.
			
		Args:
			phone: The phone number of the client
		"""
		logger.login("Login of {} successful.".format(phone))
	
	
	async def on_listening(self):
		"""Called when the client is listening."""
		logger.debug("Listening...")
	
	
	async def on_message_delivered(self, ctx):
		"""Called when the client is listening, and the client has successfully marked messages as delivered.
		
		Args (Context):
			msg_ids: The messages that are marked as delivered
			thread_id: Thread ID that the action was sent to
			thread_type (ThreadType): Type of thread that the action was sent to
			ts: A timestamp of the action
		"""
		logger.info(
			"Marked messages {} as delivered in [({}, {})] at {}.".format(
				ctx.msg_ids, ctx.thread_id, ctx.thread_type.name, int(_util.now() / 1000)
			)
		)
	
	
	async def on_marked_seen(self, ctx):
		"""Called when the client is listening, and the client has successfully marked messages as read/seen.
		
		Args (Context):
			msg_ids: The messages that are marked as read/seen
			thread_id: Thread ID that the action was sent to
			thread_type (ThreadType): Type of thread that the action was sent to
		"""
		logger.info(
			"Marked messages {} as seen in [({}, {})] at {}.".format(
				ctx.msg_ids, ctx.thread_id, ctx.thread_type.name, int(_util.now() / 1000)
			)
		)
	
	
	async def on_message(self, ctx):
		"""Called when the client is listening, and somebody sends a message.

		Args (Context):
			message_id (str): The message ID
			author_id: The ID of the author
			message (str | dict): The message content of the author
			message_object (Message): The message (As a `Message` object)
			thread_id (str): Thread ID that the message was sent to.
			thread_type (ThreadType): Type of thread that the message was sent to.
		"""
		logger.info("{} from {} in {}".format(ctx.message, ctx.thread_id, ctx.thread_type.name))
	
	async def on_event(self, ctx):
		"""Called when the client listening, and some events occurred.

		Args (Context):
			event_data (EventObject): Event data (As a `EventObject` object)
			event_type (EventType/GroupEventType): Event Type
		"""
	
	async def on_error_callback(self, error, ts=int(time.time())):
		"""Called when the module has some error.
		
		Args:
			error: Description of the error
			ts: A timestamp of the error (Default: auto)
		"""
		logger.error(f"An error occurred at {ts}: {error}")
		print(traceback.format_exc())
	
	@add_register_handler
	async def onMessage(self, ctx):
		await self.on_message(ctx)
	
	"""
	END EVENTS
	"""