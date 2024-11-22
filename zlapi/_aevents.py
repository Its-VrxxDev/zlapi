from enum import auto
from ._core import Enum

class GroupEventType(Enum):
	JOIN_REQUEST = auto()
	JOIN = auto()
	LEAVE = auto()
	REMOVE_MEMBER = auto()
	BLOCK_MEMBER = auto()
	
	UPDATE_SETTING = auto()
	UPDATE = auto()
	NEW_LINK = auto()
	
	ADD_ADMIN = auto()
	REMOVE_ADMIN = auto()
	
	NEW_PIN_TOPIC = auto()
	UPDATE_PIN_TOPIC = auto()
	REORDER_PIN_TOPIC = auto()
	
	UPDATE_BOARD = auto()
	REMOVE_BOARD = auto()
	
	UPDATE_TOPIC = auto()
	UNPIN_TOPIC = auto()
	REMOVE_TOPIC = auto()
	
	UNKNOWN = auto()


class EventType(Enum):
	REACTION = auto()