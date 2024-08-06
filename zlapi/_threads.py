from ._core import Enum

class ThreadType(Enum):
	"""Used to specify what type of Zalo thread is being used."""
	
	USER = 0
	GROUP = 1