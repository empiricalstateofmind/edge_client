from edge.api import *
import os
import sys

BOOKED = False
ATTEMPTS = 0

CODE, DATE, START, END = sys.argv[1:]

while not BOOKED and ATTEMPTS <= 10:

	booking = ClassBooker()
	booking.authenticate()
	booking.search(CODE, DATE, START, END)

	soup = BeautifulSoup(booking.search_result.text)
	result = soup.find("span", {"id": "basketControl_1_1"})

	if result.text == "Full":
		available = False
		print("Class is FULL")
		time.sleep(60)
		ATTEMPTS += 1
	else:
		available = True

	if available:
		booking.add_to_basket()
		booking.checkout()
		booking.confirm()
		BOOKED = True
