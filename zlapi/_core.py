import enum

class Enum(enum.Enum):
	"""Used internally by to support enumerations"""
		
	def __repr__(self):
		# For documentation:
		return "{}.{}".format(type(self).__name__, self.name)