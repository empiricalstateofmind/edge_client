import httplib2
import os
from datetime import datetime, timedelta

from apiclient.discovery import build
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")
CREDENTIALS = os.path.join(os.path.dirname(__file__), "credentials.dat")
APPLICATION_NAME = 'Edge Signup'

# NOT SURE WHAT THIS DOES
#try:
#    import argparse
#    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#except ImportError:
#    flags = None

event = {
  'summary': 'Test',
  'location': 'The Edge, Leeds',
  'description': '',
  'start': {
    'dateTime': '2015-10-28T09:00:00',
    'timeZone': 'Europe/London',
  },
  'end': {
    'dateTime': '2015-10-28T17:00:00',
    'timeZone': 'Europe/London',
  },
  #'reminders': {
  #  'useDefault': False,
  #  'overrides': [
  #    {'method': 'email', 'minutes': 24 * 60},
  #  ],
  #},
}

# Example reminders
#      {'method': 'email', 'minutes': 24 * 60}
#      {'method': 'popup', 'minutes': 10}
# Example attendees
#  'attendees': [
#    {'email': 'email@email.com'},
#  ],
# Recurrence
#  'recurrence': [
#    'RRULE:FREQ=DAILY;COUNT=1'
#  ],


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """

    store = Storage(CREDENTIALS)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        #if flags:
        #    credentials = tools.run_flow(flow, store, flags)
        #else: # Needed only for compatability with Python 2.6
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + 'credentials.dat')
    return credentials

def get_service(credentials):
    http = credentials.authorize(httplib2.Http())
    service = build('calendar', 'v3', http=http)
    return service

def create_event(summary, start, end):
    event_body = event.copy()
    event_body['summary'] = summary
    start = start.strftime('%Y-%m-%dT%H:%M:%S')
    end = end.strftime('%Y-%m-%dT%H:%M:%S')
    event_body['start']['dateTime'] = start 
    event_body['end']['dateTime'] = end 
    return event_body  

def add_event(service, calendarId, event_body):
    event = service.events().insert(calendarId=calendarId, body=event_body).execute()
    return event

def get_calendars(service):
    calendars = service.calendarList().list().execute()
    calendarIds = {}
    for calendar in calendars['items']:
        calendarIds[calendar['summary']] = calendar['id']
    return calendarIds

def parse_dates(date, start):
    start = start.split('-')[0].strip()
    date_time = '-'.join([date,start])
    date_time = datetime.strptime(date_time, '%d_%m_%Y-%H%M')
    return date_time

def add_class_to_calendar(activity, date_time):
    credentials = get_credentials()
    service = get_service(credentials)
    calendars = get_calendars(service)
    event_body = create_event(activity, date_time, date_time + timedelta(minutes=45))
    event = add_event(service, calendars['Gym/Sports'], event_body)

if __name__ == '__main__':
    credentials = get_credentials()
    service = get_service(credentials)
    calendars = get_calendars(service)
    event_body = create_event('Spin', datetime.now(), datetime.now() + timedelta(minutes=45))
    event = add_event(service, calendars['Gym/Sports'], event_body)
    #event = service.events().insert(calendarId=calendars['Gym/Sports'], body=event_body).execute()
    #event = service.events().insert(calendarId='primary', body=event).execute()
    print 'Event created: %s' % (event.get('htmlLink'))