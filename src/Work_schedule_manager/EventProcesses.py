import re
import os
import math
import random
import logging
import datetime
import requests
import numpy as np
import pandas as pd
import win32com.client
from typing import Any, List
from bs4 import BeautifulSoup
from pandas.core.base import DataError
from pandas.core.frame import DataFrame

from services.utils.store import logger
logger = logging.getLogger(__file__.split('\\')[-1].split('.')[0])

class EventTerminal():

    def __init__(self, df: DataFrame) -> None:
        if df.shape[0] > 0:
            self.df = df
        else:
            raise DataError('Dataframe has to have some data in it')
        self.appointment_list = []
        self.quote_service_data = self.quote_service()

    def build_events(self, subject, location, recipients, attachments, body):
        og_subject = subject # Needed to do this since changing subject of if statement, changes it permanently
        for index, actual_row in self.df.iterrows():

            logger.debug(': actual_row.start_time_converted | Literal: %s | Type: %s', actual_row.start_time_converted, type(actual_row.start_time_converted))
            logger.debug(': df: %s', actual_row)
            start = datetime.datetime.strftime(actual_row.start_time_converted, '%Y-%m-%d %H:%M:%S') 
            end = datetime.datetime.strftime(actual_row.end_time_converted, '%Y-%m-%d %H:%M:%S')
            body_fields = {'duration': actual_row.duration,'quote': self.__get_random_quote()}
            
            # Request to know the job position (if there is) instead of boiler template name/else just boiler template
            if 'Alt Dept/Job' in actual_row.keys() and self._nan_check(actual_row['Alt Dept/Job']):
                subject = actual_row['Alt Dept/Job']
            else:
                subject = og_subject
                
            event_instance = self.Event(
                start_time_datetime=actual_row.start_time_converted,
                start_time=start, 
                subject=subject, 
                end_time=end, 
                location=location, 
                recipients=recipients, 
                attachments=attachments, 
                body=body, 
                body_fields=body_fields
            )
            self.appointment_list.append(event_instance)

    def send_events(self):
        """
        Sends events from the list of appointments
        Handles whenever an event is not deliverable, saving such to a folder named <var.file_name> defined in file named <variables_in>

        Output: None | Prints which appointments have been sent
        """
        error_count = 0
        dir_name = str(datetime.datetime.today())
        for index, event in enumerate(self.appointment_list):
            try:
                event.save_and_send()
                print('Saved and Sent', index)
            except Exception as e:
                print('Error', e)
                # TODO: Check why is it saving without thrown exception
                if error_count == 0:
                    os.mkdir(dir_name)
                event.save_in_location(os.path.join(os.path.abspath(__file__), dir_name, __file__), index)
                error_count += 1
                print(f'Error found on {index}')

    def __get_random_quote(self):
        try:
            random_quote_data = self.quote_service_data[random.randint(0,len(self.quote_service_data))]
        except IndexError:
            random_quote_data = self.quote_service_data[0]
        return random_quote_data['quote'] + '\n' + random_quote_data['author']

    def quote_service(self):
            random_page = random.randint(0, 100)
            URL = 'https://www.goodreads.com/quotes?page={0}'.format(random_page)

            req = requests.get(URL)
            soupy = BeautifulSoup(req.content, 'html.parser')

            results = soupy.find_all('div', class_='quote', recursive=True)
            data = []

            for elem in results:
                data_row = {}
                quoteText = elem.find('div', class_='quoteText')
                authorOrTitle = quoteText.find('span', class_='authorOrTitle')
                if None in (quoteText, authorOrTitle):
                    # print('Check ', quoteText)
                    # print('Wow ', authorOrTitle)
                    continue
                data_row['quote'] = re.compile(r"\“(.*?)\”").search(quoteText.text.strip()).group()
                data_row['author'] = authorOrTitle.text.strip(' \n\r,')
                data.append(data_row)
            
            return data

    @staticmethod
    def _nan_check(*value):
        """
        Check if value is nan
        """
        for val in value:
            try:
                if pd.isna(val) or math.isnan(val):
                    return False
            except TypeError:
                continue
        return True

    class Event(object):
        """
        COMObject Appointment object wrapper used for easier access to event data since the Outlook API items have to be specific explicitly
        """
        _fields = [('Subject','subject'),('Start time', 'start_time'), ('End time', 'end_time'), 
                   ('Duration', 'duration'), ('Location', 'location'), ('Recipients', 'recipients'), ('Body','body')]
        def __init__(self, start_time_datetime: datetime.datetime, start_time: str, subject: str, end_time: str, location: str, recipients: List[str], attachments: List[str], body: str, body_fields=None) -> None:
            self._start_time_datetime = start_time_datetime
            self._start_time = start_time
            self._duration = body_fields['duration']
            self._end_time = end_time
            self._subject = subject
            self._location = location
            self._recipients = recipients
            self._attachments = attachments
            self._body = body.format(**body_fields)
            self._oOutlook = win32com.client.Dispatch("Outlook.Application")
            self._COMObject_appt = self._create_event()

        def __str__(self) -> str:
            output = ''
            for i, field in enumerate(self._fields):
                show, key = field
                if i != 0:
                    output += ' ' * i + '└ ' + show + ': {' + key + '}\n'
                else:
                    output += show + ': {' + key + '}\n'
            return output.format(
                start_time=self._start_time, end_time=self._end_time, duration=self._duration, location=self._location, subject=self._subject, recipients=self._recipients, body=self._body
            )

        def save_in_location(self, location, name) -> None:
            self._COMObject_appt.SaveAs(location+'/'+str(name)+'.msg', 9)

        def save_and_send(self) -> None:
            """
            Each event has the attribute of sending itself, called by event terminal
            """
            self._COMObject_appt.Save()
            self._COMObject_appt.Send()

        def _create_event(self) -> Any:
            """
            Creates the AppointmentItem object (Outlook)
            https://docs.microsoft.com/en-us/office/vba/api/outlook.appointmentitem
            """
            # Check if event exists
            # self._cancel_if_exists(self._start_time_datetime)

            appointment = self._oOutlook.CreateItem(1)  # 1=outlook appointment item

            appointment.Start = self._start_time
            appointment.Subject = self._subject
            appointment.End = self._end_time
            appointment.Location = self._location
            appointment.Body = self._body
            appointment.ReminderSet = True
            appointment.ReminderMinutesBeforeStart = 30

            # If there are recipients, then convert to meeting and add them
            if len(self._recipients) > 0:
                appointment.MeetingStatus = 1
                for rcpnt in self._recipients:
                    appointment.Recipients.Add(rcpnt)

            # If there are attachments, add them
            if len(self._attachments) > 0:
                for attach in self._attachments:
                    appointment.Attachments.Add(attach)

            return appointment

        def _cancel_if_exists(self, start_time):
            """
            Work in progress since OutlookAPI doesn't let me filter down to the specific calendar meeting/appointment.
            Only allows me to filter to the day 😭
            """
            namespace = self._oOutlook.GetNamespace("MAPI")

            appointments = namespace.GetDefaultFolder(9).Items
            appointments.Sort("[Start]")

            # logger.debug(': Input date when running _cancel_if_exists | Literal: %s | Type: ', start_time, type(start_time))

            begin = datetime.date(start_time.year,start_time.month,start_time.day)
            end = begin + datetime.timedelta(days = 1)
            restriction = "[Start] > '" + begin.strftime("%m/%d/%Y %I:%M%p") + "' AND [End] < '" + end.strftime("%m/%d/%Y %I:%M%p") + "' AND [Subject] = 'Día de Trabajo'"
            restrictedItems = appointments.Restrict(restriction)

            if len(restrictedItems) > 0:
                for appointmentItem in restrictedItems:
                    appointmentItem.MeetingStatus = 5
                    appointmentItem.Save()
                    appointmentItem.Send()

if __name__ == '__main__':
    print(f"Ran {__file__}")
    print(str(datetime.datetime.today().date()), os.path.join(os.path.abspath(__file__), __file__))
else:
    print(f'Imported {__file__}')