import re
import random
import requests
import pandas as pd
import win32com.client
from typing import Any, List
from bs4 import BeautifulSoup
from datetime import datetime
from pandas.core.base import DataError
from pandas.core.frame import DataFrame

class EventTerminal():

    def __init__(self, df: DataFrame) -> None:
        if df.shape[0] > 0:
            self.df = df
        else:
            raise DataError('Dataframe has to have some data in it')
        self.appointment_list = []

    def build_events(self, subject, location, recipients, attachments, body):
        for row in self.df.iterrows():
            actual_row = row[1]

            start = datetime.strftime(actual_row.start_time_converted, '%Y-%m-%d %H:%M:%S')
            end = datetime.strftime(actual_row.end_time_converted, '%Y-%m-%d %H:%M:%S')
            event_instance = self.Event(start_time=start, subject=subject, end_time=end, location=location, duration=actual_row.duration, recipients=recipients, attachments=attachments, body=body)
            self.appointment_list.append(event_instance)

    def send_events(self):
        for event in self.appointment_list:
            event.send()

    class Event(object):
        """
        COMObject Appointment object wrapper used for easier access to event data since the Outlook API is somewhat funky
        """
        _fields = [('Subject','subject'),('Start time', 'start_time'), ('End time', 'end_time'), 
                   ('Duration', 'duration'), ('Location', 'location'), ('Recipients', 'recipients'), ('Body','body')]
        def __init__(self, start_time: str, subject: str, end_time: str, location: str, duration: float, recipients: List[str], attachments: List[str], body: str) -> None:
            self.start_time = start_time
            self.end_time = end_time
            self.subject = subject
            self.location = location
            self.duration = duration
            self.recipients = recipients
            self.attachments = attachments
            self.body = body.format(duration=duration,quote=self.quote_service())
            self.COMObject_appt = self._create_event()

        def __str__(self) -> str:
            output = ''
            for i, field in enumerate(self._fields):
                if i != 0:
                    output += ' ' * i + '└ ' + field[0] + ': {' + field[1] + '}\n'
                else:
                    output += field[0] + ': {' + field[1] + '}\n'
            return output.format(
                start_time=self.start_time, end_time=self.end_time, duration=self.duration, location=self.location, subject=self.subject, recipients=self.recipients, body=self.body
            )

        def send(self) -> None:
            """
            Each event has the attribute of sending itself, called by event terminal
            """
            self.COMObject_appt.Save()
            self.COMObject_appt.Send()

        def _create_event(self) -> Any:
            """
            Creates the AppointmentItem object (Outlook)
            https://docs.microsoft.com/en-us/office/vba/api/outlook.appointmentitem
            """
            pass
            oOutlook = win32com.client.Dispatch("Outlook.Application")

            appointment = oOutlook.CreateItem(1)  # 1=outlook appointment item

            appointment.Start = self.start_time
            appointment.Subject = self.subject
            appointment.End = self.end_time
            appointment.Location = self.location
            appointment.Body = self.body
            appointment.ReminderSet = True
            appointment.ReminderMinutesBeforeStart = 30

            # If there are recipients, then convert to meeting and add them
            if len(self.recipients) > 0:
                appointment.MeetingStatus = 1
                for rcpnt in self.recipients:
                    appointment.Recipients.Add(rcpnt)

            # If there are attachments, add them
            if len(self.attachments) > 0:
                for attach in self.attachments:
                    appointment.Attachments.Add(attach)

            return appointment

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

            df = pd.DataFrame(data=data)
            random_quote = df.iloc[random.randint(0,df.shape[0])]
            
            return random_quote[0] + '\n' + random_quote[1]

# def main():
#     df = pd.read_csv('./Schedule_Dfs/3-8-2021_3-14-2021_schedule.csv')
#     df = df.dropna(axis=0).reset_index()
#     v_crtn = EventTerminal(df)
#     v_crtn.build_events('Día de Trabajo', 'Costco (1175 N 205th St, Shoreline, WA  98133, United States)', ['valeracuevan@spu.edu'], attachments=[])
#     for event in v_crtn.appointment_list:
#         print(event)
#         print()
#     # v_crtn.send_events()


# if __name__ == '__main__':
#     main()
