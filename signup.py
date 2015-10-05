import requests
import config
from BeautifulSoup import BeautifulSoup # Could use re to remove dependency.

class AuthenticationError(exception):
	pass

class AvailabilityError(exception):
	pass

class BasketError(exception):
	pass

class ClassBooker(object):
	""" 
	Handles all aspects of logging onto the EDGE classes.
	Includes logging on, availability checking, and class booking. 
	"""

	LOGON = "https://sportsbookings.leeds.ac.uk/OnlineBookings/Account/LogOn"
	SEARCH = "https://sportsbookings.leeds.ac.uk/OnlineBookings/Search/PerformSearch"
	ADD_TO_BASKET = "https://sportsbookings.leeds.ac.uk/OnlineBookings/Search/AddEnrolmentToBasket"
	CHECKOUT = "https://sportsbookings.leeds.ac.uk/payments"
	CONFIRM = "https://sportsbookings.leeds.ac.uk/Payments/Response/FoC"
	RECEIPT = "https://sportsbookings.leeds.ac.uk/Payments/Receipt"

	# Hide password in ENV.
	LOGON_PAYLOAD = {"UserName":SPIN_USER,
					 "Password":SPIN_PASS,
					 "RememberMe":"false",
					}

	SEARCH_PAYLOAD = {"searchType":"1",
					  "SearchType":"1",
					  "SavedSearchName":"",
					  "SearchForActivity":"0",
					  "SearchForClass":"1",
					  "PersistSearchTimes":"False",
					  "SiteID":"1",
					  "Activity": "SEN6",# "SESP", # or SE28
					  "SearchDate": "02/10/2015",
					  "EnglishDate": "2_10_2015",
					  "English_TimeFrom": "06_00",
					  "English_TimeTo":"21_00",
					  "HeadCount":"1",
					  "SaveSearch":"false",
					  "submitButton":"Search"
					 } 

	BASKET_PAYLOAD = {"SiteNo":"1",
					  "ResultId":"1"}

	CHECKOUT_PAYLOAD = {"PaymentDescription":"Online booking",
					   "BasketID":"",
					   "CallingApp":"Horizons",
					   "Culture":"en-GB",
					   "LinkBackUrlBase":"https://sportsbookings.leeds.ac.uk/OnlineBookings/",
					   "LinkBackUrlSuccess":"https://sportsbookings.leeds.ac.uk/OnlineBookings/",
					   "LinkBackUrlFail":"https://sportsbookings.leeds.ac.uk/OnlineBookings/Basket/ViewDetail",
					   "LinkBackUrlAmend":"https://sportsbookings.leeds.ac.uk/OnlineBookings/Basket/ViewDetail",
					   "LinkBackUrlContact":"http://sport.leeds.ac.uk/page.asp?section=82&sectionTitle=Contact+Us",
					   "Region":"7",
					   "PresumedPayerEmail":"mmasm@leeds.ac.uk",
					   "TermsAccepted":"true",
					   "submitButton":"Checkout"
					  }

	def __init__(self):
		"""Initialises a requests Session"""				  
		self.session = requests.Session()
		return None

	def authenticate(self, user, password):
		"""Authenticates the session"""
		LOGON_PAYLOAD["UserName"] = user
		LOGON_PAYLOAD["Password"] = password
		self.auth = self.session.post(LOGON, LOGON_PAYLOAD)
		if 1==1: # Think of suitable condition
			return None
		else:
			raise AuthenticationError()

	def search(self, activity, date, start_time, end_time):
		"""Searches for specified class"""
		SEARCH_PAYLOAD["Activity"] = activity
		SEARCH_PAYLOAD["EnglishDate"] = date
		SEARCH_PAYLOAD["English_TimeFrom"] = start_time
		SEARCH_PAYLOAD["English_TimeTo"] = end_time
		self.search = self.session.post(SEARCH, SEARCH_PAYLOAD)
		if 1==1:
			return None
		else:
			raise AvailabilityError()

	def add_to_basket(self, site_id=1, result_id=1):
		"""Adds activity to basket"""
		BASKET_PAYLOAD["SiteNo"] = str(site_id)
		BASKET_PAYLOAD["ResultId"] = str(result_id)
		self.basket = self.session.get(ADD_TO_BASKET, BASKET_PAYLOAD)
		if 1==1:
			return None
		else:
			raise BasketError()

	def checkout(self):
		"""Checkout the current basket"""
		soup = BeautifulSoup(self.basket.text)
		self.basket_id = soup.find("input",{"name":"BasketID"}).get("value")
		CHECKOUT_PAYLOAD["BasketID"] = self.basket_id
		checkout = s.post(CHECKOUT, CHECKOUT_PAYLOAD)
		return None

	def confirm(self):
		"""Confirm basket checkout"""
		self.confirm = self.session.get(CONFIRM)
		return None

	def receipt(self):
		"""Get receipt for booking"""
		soup = BeautifulSoup(self.confirm.text)
		self.transaction_id = soup.find("input",{"name":"BasketID"}).get("value")
		self.receipt = self.session.get(RECEIPT, {"TransactionID": self.transaction_id,
												  "BasketID": self.basket_id})
		return None

# 1. Start session
s = requests.Session()

# 2. Authenticate
r1 = s.post(LOGON, LOGON_PAYLOAD)

# 3. Search
# Search logic goes here - what do we want to look for?
r2 = s.post(SEARCH, SEARCH_PAYLOAD, cookies=r1.cookies)

# 4. Add to Basket
# Availability checking logic goes here
r3 = s.get(ADD_TO_BASKET, BASKET_PAYLOAD, cookies=r2.cookies)

# 5. Checkout
soup = bs.BeautifulSoup(r3.text)
basket_id = soup.find("input",{"name":"BasketID"}).get("value")
CHECKOUT_PAYLOAD["BasketID"] = basket_id
r4 = s.post(CHECKOUT, CHECKOUT_PAYLOAD, cookies=r3.cookies)

# 6. Confirm Booking?
r5 = s.get(CONFIRM, cookies=r4.cookies)

# This should be the response all being well.
# We can pull the receipt to email if we can get the transaction id.
GET2 = "https://sportsbookings.leeds.ac.uk/Payments/Receipt?TransactionID=532525&BasketId=6729b0be-c37f-431b-8b8f-186ef2027be2"

# 7. Email/Cleanup