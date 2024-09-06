# -*- coding: UTF-8 -*-

import time, datetime
import urllib.parse, json
import gzip, base64, zlib

from . import _exception
from Crypto.Cipher import AES
from ._aevents import GroupEventType

#: Default headers
HEADERS = {
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

#: Default cookies
COOKIES = {}


def now():
	return int(time.time() * 1000)
	
def formatTime(format, ftime=now()):
	dt = datetime.datetime.fromtimestamp(ftime / 1000)
	# vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
	# dt_vietnam = vietnam_tz.fromutc(dt)
	
	formatted_time = dt.strftime(format)
	
	return formatted_time


def getHeader(buffer):
	if len(buffer) < 4:
		raise ValueError("Invalid header")
	
	return [buffer[0], int.from_bytes(buffer[1:3], "little"), buffer[3]]


def getClientMessageType(msgType):
	if (msgType == "webchat"): return 1
	if (msgType == "chat.voice"): return 31
	if (msgType == "chat.photo"): return 32
	if (msgType == "chat.sticker"): return 36
	if (msgType == "chat.doodle"): return 37
	if (msgType == "chat.recommended"): return 38
	if (msgType == "chat.link"): return 38
	if (msgType == "chat.location.new"): return 43
	if (msgType == "chat.video.msg"): return 44
	if (msgType == "share.file"): return 46
	if (msgType == "chat.gif"): return 49
	
	return 1


def getGroupEventType(act):
	if (act == "join_request"): return GroupEventType.JOIN_REQUEST
	if (act == "join"): return GroupEventType.JOIN
	if (act == "leave"): return GroupEventType.LEAVE
	if (act == "remove_member"): return GroupEventType.REMOVE_MEMBER
	if (act == "block_member"): return GroupEventType.BLOCK_MEMBER
	if (act == "update_setting"): return GroupEventType.UPDATE_SETTING
	if (act == "update"): return GroupEventType.UPDATE
	if (act == "new_link"): return GroupEventType.NEW_LINK
	if (act == "add_admin"): return GroupEventType.ADD_ADMIN
	if (act == "remove_admin"): return GroupEventType.REMOVE_ADMIN
	
	return GroupEventType.UNKNOWN


def dict_to_raw_cookies(cookies_dict):
	try:
		cookie_string = "; ".join(f"{key}={value}" for key, value in cookies_dict.items())
		if not cookie_string:
			return None
		
		return cookie_string
		
	except:
		return None


def _pad(s, block_size):
	padding_length = block_size - len(s) % block_size
	
	return s + bytes([padding_length]) * padding_length
	

def _unpad(s, block_size):
	padding_length = s[-1]
	
	return s[:-padding_length]


def zalo_encode(params, key):
	try:
		key = base64.b64decode(key)
		iv = bytes.fromhex("00000000000000000000000000000000")
		cipher = AES.new(key, AES.MODE_CBC, iv)
		plaintext = json.dumps(params).encode()
		padded_plaintext = _pad(plaintext, AES.block_size)
		ciphertext = cipher.encrypt(padded_plaintext)
		
		return base64.b64encode(ciphertext).decode()
		
	except Exception as e:
		raise _exception.EncodePayloadError(f"Unable to encode payload! Error: {e}")
		
		
def zalo_decode(params, key):
	try:
		params = urllib.parse.unquote(params)
		key = base64.b64decode(key)
		iv = bytes.fromhex("00000000000000000000000000000000")
		cipher = AES.new(key, AES.MODE_CBC, iv)
		ciphertext = base64.b64decode(params.encode())
		padded_plaintext = cipher.decrypt(ciphertext)
		plaintext = _unpad(padded_plaintext, AES.block_size)
		plaintext = plaintext.decode("utf-8")
		
		if isinstance(plaintext, str):
			plaintext = json.loads(plaintext)
		
		return plaintext
		
	except Exception as e:
		raise _exception.DecodePayloadError(f"Unable to decode payload! Error: {e}")


def zws_decode(parsed, key):
	payload = parsed.get("data")
	encrypt_type = parsed.get("encrypt")
	if not payload or not key:
		return
	
	try:
		if encrypt_type == 0:
			
			decoded_data = payload
		
		elif encrypt_type == 1:
			
			decrypted_data = base64.b64decode(payload)
			decompressed_data = gzip.decompress(decrypted_data)
			decoded_data = decompressed_data.decode("utf-8")
		
		elif encrypt_type == 2:
			
			data_bytes = base64.b64decode(urllib.parse.unquote(payload))
			if len(data_bytes) >= 48:
				
				iv = data_bytes[:16]
				additional_data = data_bytes[16:32]
				data_source = data_bytes[32:]
				decryptor = AES.new(base64.b64decode(key), AES.MODE_GCM, nonce=iv)
				decryptor.update(additional_data)
				decrypted_data = decryptor.decrypt(data_source)[:-16]
				decompressed_data = zlib.decompress(decrypted_data, wbits=16)
				decoded_data = decompressed_data.decode("utf-8")
		
		else:
			
			decoded_data = None
		
		if not decoded_data:
			return
			
		return json.loads(decoded_data)
	
	except Exception as e:
		# return
		raise _exception.DecodePayloadError(f"Unable to decode payload! Error: {e}")