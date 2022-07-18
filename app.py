from flask import Flask, jsonify, request, make_response, send_from_directory
from eventRepository import eventRepository
from icalendar import Calendar, Event, vCalAddress
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import requests
import datetime
from datetime import date
from pathlib import Path

app = Flask(__name__)
repo = eventRepository()

'''
Sample Request Body
{
    "summary"
    "start"
    "end"
}

'''

@app.route('/sync/google', methods=['POST'])
def sync_google():

    json_credentials = request.get_json()

    print(json_credentials)
    
    credentials = Credentials(
        token=json_credentials['token'],
        token_uri=json_credentials['token_uri'], 
        client_id=json_credentials['client_id'],
        client_secret=json_credentials['client_secret'],
    )

    try:
        service = build('calendar', 'v3', credentials=credentials)

        # Call the Calendar API
        time =  datetime.datetime.utcnow() - datetime.timedelta(weeks=+4)
        now = time.isoformat() + 'Z' #indicates UTC time
        print(now)
        print('Getting the upcoming 10 events')

        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=40, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        # Delete existing events from google calendar
        myquery = { "from_google": 1 }
        count = repo.delete_many(myquery)
        print(count)


        # Save synced events from google calendar
        for event in events:
            summary = event['summary']
            start = event['start'].get('dateTime')
            end = event['end'].get('dateTime')
            email = event['creator'].get('email')
                
            event_dict = {
                "title": summary,
                "start": start,
                "end": end,
                "email": email,
                "from_google": 1
            }

            repo.save(event_dict)

    except HttpError as error:
        print('An error occurred: %s' % error)

    response = jsonify(events)
    response.status_code = 200
    return response
    

@app.route('/calendar', methods=['GET'])
def get_events():
    events = repo.get_all()
    response = jsonify(events)
    response.status_code = 200
    return response



@app.route('/calendar/<string:event_id>', methods=['GET'])
def get_event(event_id):
    event = repo.get_id(event_id)
    response = jsonify(event)
    response.status_code = 200
    return response


@app.route('/calendar', methods=['POST'])
def save_event():
    event = request.get_json()
    new_event = repo.save(event)
    response = jsonify(repo.get_id(new_event))
    response.status_code = 201
    return response

@app.route('/calendar', methods=['PUT'])
def update_event():
    body = request.get_json()
    event_id = body["_id"]
    updated = repo.update(body)
    if updated >= 1:
        response = jsonify(repo.get_id(event_id))
        response.status_code = 200
    else:
        response = jsonify({"status_code": 404})
    return response


@app.route('/calendar/<string:event_id>', methods=['DELETE'])
def delete_event(event_id):
    deleted = repo.delete(event_id)
    if deleted >= 1:
        response = jsonify({"status_code": 200})
    else:
        response = jsonify({"status_code": 404})
    return response

@app.route('/calendar/ics')
def calendar_ics():

    #  Get the calendar data
    cal = Calendar()

    events = repo.get_all()
    print(events)

    for dbEvent in events:
        

        try: 

            event = Event()
            event.add('summary', dbEvent['title'])
            dtstart = datetime.datetime.strptime( str(dbEvent['start']), "%Y-%m-%dT%H:%M:%S%z")
            event.add('dtstart', dtstart)
            dtend = datetime.datetime.strptime(str(dbEvent['end']), "%Y-%m-%dT%H:%M:%S%z")
            event.add('dtend', dtend)

            organizer = vCalAddress(dbEvent['email'])

            event['organizer'] = organizer

            cal.add_component(event)
        
        except:
            print('invalid event')

    directory = str(Path(__file__).parent) + "\\"
    print("ics file will be generated at ", directory)
    f = open(os.path.join(directory, 'calendar.ics'), 'wb')
    f.write(cal.to_ical())
    f.close()

    path = os.path.join(directory)
    return send_from_directory(directory=path, path="calendar.ics", as_attachment=True)

if __name__ == '__main__':
    app.run(port=8080)
