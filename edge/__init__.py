import api

try:
	import output
except ImportError, e:
	print "Unable to load OUTPUT (Google Calendar)"
	print e