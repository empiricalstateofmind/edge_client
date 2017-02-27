from edge.api import *
from edge.output import *

import os
import sys
from datetime import datetime

if os.getenv("BOOKED") == 1:
	print "Exited early"
	exit(1)

CODE, DATE, START, END = sys.argv[1:]

booking = ClassBooker()
booking.authenticate()
booking.search(CODE, DATE, START, END)

soup = BeautifulSoup(booking.search_result.text)

result = soup.find("span", {"id": "basketControl_1_1"})
if result is None:
	result = soup.find("a", {"id": "basketControl_1_1"})

if result.text == "Full":
	available = False
	print "Class is FULL"
	print "Last checked: ", str(datetime.now())
elif result.text == "Add to Basket":
	available = True
else:
	raise AvailabilityError()

if available:
	booking.add_to_basket()
	booking.checkout()
	booking.confirm()
	os.putenv("BOOKED", 1)
	date_time = parse_dates(DATE, booking.search_data[0]['time'])
	add_class_to_calendar(booking.search_data[0]['class'], date_time)
