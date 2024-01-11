from datetime import datetime, timedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def count_weekly_occurrences(date_full: str):
    """

    :param date_full: str
        either "[date1] [date2] [some text]"
        or "[date]   [some text]"
    :return: int
        number of occurrences of the event
    """
    dates = date_full.split(" ")
    # if only one date
    if len(dates[1]) == 0:
        return 1

    start_date, end_date = dates[0], dates[1]
    start = datetime.strptime(start_date, '%d.%m.%Y')
    end = datetime.strptime(end_date, '%d.%m.%Y')
    delta = end - start
    number_of_weeks = delta.days // 7 + 1
    return number_of_weeks


def transform_to_google_calendar_format(time_range: str, date: str):
    """
    :param time_range: str
        [hh.mm-hh.mm]
    :param date: str
        [dd.mm.yyyy]
    :return: str, str
        start time, end time in format
        [yyyy-mm-ddThh:mm:ss], [yyyy-mm-ddThh:mm:ss]
    """
    start_time_str, end_time_str = time_range.split('–')
    start_datetime_str = f"{date} {start_time_str}"
    end_datetime_str = f"{date} {end_time_str}"

    date_format = "%d.%m.%Y"
    new_date_format = "%Y-%m-%d"

    start_datetime = datetime.strptime(start_datetime_str, f"{date_format} %H.%M")
    end_datetime = datetime.strptime(end_datetime_str, f"{date_format} %H.%M")

    # Convert to the desired format
    google_calendar_start = start_datetime.strftime(f"{new_date_format}T%H:%M:%S")
    google_calendar_end = end_datetime.strftime(f"{new_date_format}T%H:%M:%S")

    return google_calendar_start, google_calendar_end


def construct_event(event_type: str, date_start: str, date_end: str, recs: int, loc: str):

    new_event = {
        'summary': str(event_type),
        'location': str(loc),
        'start': {
            'dateTime': str(date_start),
            'timeZone': 'Europe/Helsinki',
        },
        'end': {
            'dateTime': str(date_end),
            'timeZone': 'Europe/Helsinki',
        },
        'recurrence': [
            'RRULE:FREQ=WEEKLY;COUNT=' + str(recs)
        ],
    }
    return new_event


def send_event(event_type: str, date_full: str, time: str, location: str):
    """
    Gathers data, uses functions to parse it, and adds an event
    to the calendar
    :param event_type: str
        name of the event
    :param date_full: str
        unparsed date
    :param time: str
        unparsed time
    :param location: str
        event location
    :return:
    """
    start_date = date_full.split(" ")[0]
    recurrences = count_weekly_occurrences(date_full)
    s, e = transform_to_google_calendar_format(time, start_date)
    event = construct_event(event_type, s, e, recurrences, location)

    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    # The file token.json contain authorization tokens
    # watch 2mins from https://www.youtube.com/watch?v=vUOtS6zU40A&t=75s
    # to find out how to acquire these
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds)
    service.events().insert(calendarId='primary', body=event).execute()

