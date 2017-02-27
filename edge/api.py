import requests
from config import *
from BeautifulSoup import BeautifulSoup # Could use re to remove dependency.

class AuthenticationError(Exception):
	"""Raised when a session has failed to authenticate."""
	pass

class AvailabilityError(Exception):
	"""Raised when the search terms return zero results."""
	pass

class BasketError(Exception):
	"""Raised when an error occurs adding item to basket."""
	pass

class ClassFullError(Exception):
	"""Raised when trying to add a class which is full to basket."""
	pass

LOGON = "https://sportsbookings.leeds.ac.uk/OnlineBookings/Account/LogOn"
SEARCH = "https://sportsbookings.leeds.ac.uk/OnlineBookings/Search/PerformSearch"
ADD_TO_BASKET = "https://sportsbookings.leeds.ac.uk/OnlineBookings/Search/AddEnrolmentToBasket"
CHECKOUT = "https://sportsbookings.leeds.ac.uk/payments"
CONFIRM = "https://sportsbookings.leeds.ac.uk/Payments/Response/FoC"
RECEIPT = "https://sportsbookings.leeds.ac.uk/Payments/Receipt"

# Hide password in ENV.
LOGON_PAYLOAD = {"UserName": SPIN_USER,
				 "Password": SPIN_PASS,
				 "RememberMe": "false",
				}

SEARCH_PAYLOAD = {"searchType": "1",
				  "SearchType": "1",
				  "SavedSearchName": "",
				  "SearchForActivity": "0",
				  "SearchForClass": "1",
				  "PersistSearchTimes": "False",
				  "SiteID": "1",
				  "Activity": "SESP",# "SESP", # or SE28 #H3_C is all classes
				  "SearchDate": "06/10/2015",
				  "EnglishDate": "6_10_2015",
				  "English_TimeFrom": "06_00",
				  "English_TimeTo": "21_00",
				  "HeadCount": "1",
				  "SaveSearch": "false",
				  "submitButton": "Search"
				 } 

BASKET_PAYLOAD = {"SiteNo": "1",
				  "ResultId": "1"}

CHECKOUT_PAYLOAD = {"PaymentDescription": "Online booking",
				   "BasketID": "",
				   "CallingApp": "Horizons",
				   "Culture": "en-GB",
				   "LinkBackUrlBase": "https://sportsbookings.leeds.ac.uk/OnlineBookings/",
				   "LinkBackUrlSuccess": "https://sportsbookings.leeds.ac.uk/OnlineBookings/",
				   "LinkBackUrlFail": "https://sportsbookings.leeds.ac.uk/OnlineBookings/Basket/ViewDetail",
				   "LinkBackUrlAmend": "https://sportsbookings.leeds.ac.uk/OnlineBookings/Basket/ViewDetail",
				   "LinkBackUrlContact": "http://sport.leeds.ac.uk/page.asp?section=82&sectionTitle=Contact+Us",
				   "Region": "7",
				   "PresumedPayerEmail": EDGE_EMAIL,
				   "TermsAccepted": "true",
				   "submitButton": "Checkout"
				  }

# Add class, date, and time validators

class ClassBooker(object):
	"""
	Handles all aspects of logging onto the EDGE classes.
	Includes logging on, availability checking, and class booking.
	"""

	def __init__(self):
		"""Initialises a requests Session."""
		self.session = requests.Session()
		return None

	def authenticate(self, user=None, password=None):
		"""Authenticates the session."""
		if user is not None:
			LOGON_PAYLOAD["UserName"] = user
		if password is not None:
			LOGON_PAYLOAD["Password"] = password
		self.auth = self.session.post(LOGON, data=LOGON_PAYLOAD)
		if 1 == 1:# Think of suitable condition
			return None
		else:
			raise AuthenticationError("Authenication failed")

	def search(self, activity, date, start_time, end_time):
		"""Searches for specified class."""
		SEARCH_PAYLOAD["Activity"] = activity
		SEARCH_PAYLOAD["EnglishDate"] = date
		SEARCH_PAYLOAD["SearchDate"] = '/'.join(date.split('_'))
		SEARCH_PAYLOAD["English_TimeFrom"] = start_time
		SEARCH_PAYLOAD["English_TimeTo"] = end_time
		self.search_result = self.session.post(SEARCH, data=SEARCH_PAYLOAD)
		soup = BeautifulSoup(self.search_result.text)
		self.results_table = soup.find("table", {"class": "ActivitySearchResults sortable"})
		if self.results_table is not None:
			self.results_table = self.results_table.tbody
			self._save_search()
			self._print_search()
			return None
		else:
			raise AvailabilityError("No classes returned with search terms")

	def add_to_basket(self, site_id=1, result_id=1):
		"""Adds activity to basket."""
		BASKET_PAYLOAD["SiteNo"] = str(site_id)
		BASKET_PAYLOAD["ResultId"] = str(result_id)
		self.basket = self.session.get(ADD_TO_BASKET, params=BASKET_PAYLOAD)
		if self.search_data[result_id-1]['status'] == 'Add to Basket':
			return None
		elif self.search_data[result_id-1]['status'] == 'Full':
			raise ClassFullError()
		else:
			raise BasketError()

	def checkout(self):
		"""Checkout the current basket."""
		soup = BeautifulSoup(self.basket.text)
		self.basket_id = soup.find("input", {"name": "BasketID"}).get("value")
		CHECKOUT_PAYLOAD["BasketID"] = self.basket_id
		checkout = self.session.post(CHECKOUT, CHECKOUT_PAYLOAD)
		return None

	def confirm(self):
		"""Confirm basket checkout."""
		self.confirmation = self.session.get(CONFIRM)
		return None

	def receipt(self):
		"""Get receipt for booking."""
		soup = BeautifulSoup(self.confirmation.text)
		self.transaction_id = soup.find("input", {"name": "BasketID"}).get("value")
		self.receipt = self.session.get(RECEIPT, {"TransactionID": self.transaction_id,
												  "BasketID": self.basket_id})
		return None

	def _save_search(self):
		self.search_data = []
		for row in self.results_table.findAll("tr"):
			cells = row.findAll('td')
			self.search_data.append({'class': cells[1].find(text=True),
									 'time': cells[0].find(text=True).replace('&#58;',''),
									 'status': cells[3].find(text=True)})
		return None

	def _print_search(self):
		print "SEARCH RESULTS"
		print "="*20 + "\n"
		for row in self.search_data:
			print row['class']
			print row['time']
			print row['status']
			print "-"*20
		return None

# # 1. Start session
# s = requests.Session()

# # 2. Authenticate
# r1 = s.post(LOGON, LOGON_PAYLOAD)

# # 3. Search
# # Search logic goes here - what do we want to look for?
# r2 = s.post(SEARCH, SEARCH_PAYLOAD, cookies=r1.cookies)

# # 4. Add to Basket
# # Availability checking logic goes here
# r3 = s.get(ADD_TO_BASKET, BASKET_PAYLOAD, cookies=r2.cookies)

# # 5. Checkout
# soup = bs.BeautifulSoup(r3.text)
# basket_id = soup.find("input",{"name":"BasketID"}).get("value")
# CHECKOUT_PAYLOAD["BasketID"] = basket_id
# r4 = s.post(CHECKOUT, CHECKOUT_PAYLOAD, cookies=r3.cookies)

# # 6. Confirm Booking?
# r5 = s.get(CONFIRM, cookies=r4.cookies)

# # This should be the response all being well.
# # We can pull the receipt to email if we can get the transaction id.
# GET2 = "https://sportsbookings.leeds.ac.uk/Payments/Receipt?TransactionID=532525&BasketId=6729b0be-c37f-431b-8b8f-186ef2027be2"

# # 7. Email/Cleanup
