from edge.api import *
from edge.output import *
import sys
import time
from datetime import datetime, timedelta

BOOKED = False
ATTEMPTS = 0

CLASS, START, END = sys.argv[1:]
DATE = (datetime.now() + timedelta(days=2)).strftime('%d_%m_%Y')

while BOOKED is False and ATTEMPTS <= 10:

	booking = ClassBooker()
	booking.authenticate()
	booking.search(CLASS, DATE, START, END)

	soup = BeautifulSoup(booking.search_result.text)

	result = soup.find("span", {"id": "basketControl_1_1"})
	if result is None:
		result = soup.find("a", {"id": "basketControl_1_1"})

	if result.text == "Full":
		available = False
		time.sleep(60)
		ATTEMPTS += 1
	elif result.text == "Add to Basket":
		available = True
	else:
		raise AvailabilityError()

	if available:
		booking.add_to_basket()
		booking.checkout()
		booking.confirm()
		BOOKED = True
		date_time = parse_dates(DATE, booking.search_data[0]['time'])
		add_class_to_calendar(booking.search_data[0]['class'], date_time)