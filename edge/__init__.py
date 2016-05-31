from api import *

try:
	from output import *
except ImportError, e:
	print("Unable to load OUTPUT (Google Calendar)")
	print(e)