import json

from . import _util
from ._core import Enum
from ._parse_message import Parse

class Message:
	def __init__(self, text=None, style=None, mention=None, parse_mode=None):
		self.text = text
		self.style = str(style) if style else None
		self.mention = str(mention) if mention else None
		self.parse_mode = str(parse_mode) if parse_mode else None
		
		
		if parse_mode:
			styles = json.loads(self.style)["styles"] if self.style else []
			if self.parse_mode == "Markdown":
				
				self.text, self.parse_list = Parse(self.text, self.style, "Markdown")
				
			elif self.parse_mode == "HTML":
				
				self.text, self.parse_list = Parse(self.text, self.style, "HTML")
			
			else:
				raise ValueError("Invalid Parse Mode, Only Support `Markdown` & `HTML`")
			
			if len(self.parse_list) == 1 and not styles:
			
				element = self.parse_list[0]
				self.style = MessageStyle(
					offset=element["start"],
					length=element["length"],
					style=element["type"]
				)
		
			elif len(self.parse_list) < 1:
				pass
		
			else:
				
				for element in self.parse_list:
					style = MessageStyle(
						offset=element["start"],
						length=element["length"],
						style=element["type"],
						auto_format=False
					)
					styles.append(style)
			
				self.style = MultiMsgStyle(styles)
			
			self.style = str(self.style) if self.style else None
	
				
	
	def __repr__(self):
		return f"Message(text={self.text!r}, style={self.style!r}, mention={self.mention!r}, parse_mode={self.parse_mode!r})"


class MessageStyle:
	def __new__(self, offset=0, length=1, style="font", color="ffffff", size="18", auto_format=True):
		self.offset = offset
		self.length = length
		self.style = style
		if type(offset) != int and type(length) != int:
			raise ValueError("Invalid Length, Offset! Length and Offset must be integers")
		
		if style == "bold":
			self.style = "b"
		elif style == "italic":
			self.style = "i"
		elif style == "underline":
			self.style = "u"
		elif style == "strike":
			self.style = "s"
		elif style == "color":
			self.style = "c_" + str(color).replace("#", "")
		elif style == "font":
			self.style = "f_" + str(size)
		else:
			self.style = "f_18"
		
		if auto_format:
			self.styleFormat = json.dumps({
				"styles": [{
					"start": self.offset,
					"len": self.length,
					"st": self.style
				}],
				"ver": 0
			})
		else:
			self.styleFormat = {
				"start": self.offset,
				"len": self.length,
				"st": self.style
			}
		
		return self.styleFormat
		

class MultiMsgStyle:
	def __init__(self, listStyle):
		styles = []
		for style in listStyle:
			styles.append(style)
			
		self.styleFormat = json.dumps({
			"styles": styles,
				"ver": 0
		})
	
	def __str__(self):
		return self.styleFormat


class MessageReaction:
	def __new__(self, messageObject, auto_format=True):
		self.msgId = messageObject.msgId
		self.cliMsgId = messageObject.cliMsgId
		self.msgType = _util.getClientMessageType(messageObject.msgType)
		if not isinstance(msgType, int):
			raise ValueError("Msg Type must be int")
		
		if auto_format:
			self.reactionFormat = [{
				"gMsgID": int(self.msgId),
				"cMsgID": int(self.cliMsgId),
				"msgType": int(self.msgType)
			}]
			
		else:
			self.reactionFormat = {
				"gMsgID": int(self.msgId),
				"cMsgID": int(self.cliMsgId),
				"msgType": int(self.msgType)
			}
		
		return self.reactionFormat


class Mention:
	def __new__(self, uid, length=1, offset=0, auto_format=True):
		self.user_id = uid
		self.offset = offset
		self.length = length
		self.type = 1 if uid == "-1" else 0
		if type(offset) != int and type(length) != int:
			raise ValueError("Invalid Length, Offset! Length and Offset must be integers")
		
		if auto_format:
			self.mentionFormat = json.dumps([{
				"pos": self.offset,
				"len": self.length,
				"uid": self.user_id,
				"type": self.type
			}])
		else:
			self.mentionFormat = {
				"pos": self.offset,
				"len": self.length,
				"uid": self.user_id,
				"type": self.type
			}
			
		return self.mentionFormat


class MultiMention:
	def __init__(self, listMention):
		mentions = []
		for mention in listMention:
			mentions.append(mention)
			
		self.mentionFormat = json.dumps(mentions)
	
	def __str__(self):
		return self.mentionFormat