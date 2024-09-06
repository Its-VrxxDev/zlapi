from munch import DefaultMunch
from dataclasses import dataclass

class User(DefaultMunch):
	def __repr__(self):
		attrs = [f"{key}={value!r}" for key, value in self.__dict__.items()]
		return f"User({', '.join(attrs)})"


class Group(DefaultMunch):
	def __repr__(self):
		attrs = [f"{key}={value!r}" for key, value in self.__dict__.items()]
		return f"Group({', '.join(attrs)})"


class ContextObject(DefaultMunch):
	def __repr__(self):
		attrs = [f"{key}={value!r}" for key, value in self.__dict__.items()]
		return f"Context({', '.join(attrs)})"


class MessageObject(DefaultMunch):
	def __repr__(self):
		attrs = [f"{key}={value!r}" for key, value in self.__dict__.items()]
		return f"Message({', '.join(attrs)})"


class EventObject(DefaultMunch):
	def __repr__(self):
		attrs = [f"{key}={value!r}" for key, value in self.__dict__.items()]
		return f"GroupEvent({', '.join(attrs)})"