# -*- coding: UTF-8 -*-

import urllib
import json, base64
import time, datetime

from . import _exception
from Crypto.Cipher import AES

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
		
	except:
		raise _exception.EncodePayloadError("Key is incorrect!")
		
		
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
		
	except:
		raise _exception.DecodePayloadError("Key is incorrect!")
