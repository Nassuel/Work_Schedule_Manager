import pandas as pd
from pandas.core.base import DataError
import win32com.client
from datetime import datetime

from pandas.core.frame import DataFrame

from typing import Any, List


class EventTerminal():

    def __init__(self, df: DataFrame) -> None:
        if df.shape[0] > 0:
            self.df = df
        else:
            raise DataError('Dataframe has to have some data in it')
        self.appointment_list = []

    def build_events(self, subject, location, recipients, attachments):
        for row in self.df.iterrows():
            actual_row = row[1]

            start = datetime.strftime(actual_row.start_time_converted, '%Y-%m-%d %H:%M:%S')
            end = datetime.strftime(actual_row.end_time_converted, '%Y-%m-%d %H:%M:%S')
            event_instance = self.Event(start_time=start, subject=subject, end_time=end, location=location, duration=actual_row.duration, recipients=recipients, attachments=attachments)
            self.appointment_list.append(event_instance)

    def send_events(self):
        for event in self.appointment_list:
            event.send()

    class Event(object):
        """
        COMObject Appointment object wrapped used for easier access to event data since the Outlook API is somewhat funky
        """

        def __init__(self, start_time: str, subject: str, end_time: str, location: str, duration: float, recipients: List[str], attachments: List[str]) -> None:
            self.start_time = start_time
            self.end_time = end_time
            self.subject = subject
            self.location = location
            self.duration = duration
            self.recipients = recipients
            self.attachments = attachments
            self.body = 'Trabajas hoy por {duration} horas\nGenerado con ❤  por Nassuel 😊'.format(duration=duration)
            self.COMObject_appt = self._create_event()

        def __str__(self) -> str:
            return '''Subject: {subject}\n └ Start time: {start_time}\n  └ End time: {end_time}\n   └ Duration: {duration}\n    └ Location: {location}\n     └ Recipients: {recipients}\n      └ Body: {body}'''.format(
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
            # appointment.Duration = duration
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

def main():
    df = pd.read_csv('./Schedule_Dfs/1-11-2021_1-17-2021_schedule.csv')
    v_crtn = EventTerminal(df)
    v_crtn.build_events('Día de Trabajo', 'Costco (1175 N 205th St, Shoreline, WA  98133, United States)', ['valeracuevan@spu.edu'])
    for event in v_crtn.appointment_list:
        print(event)
        print()
    # v_crtn.send_events()


if __name__ == '__main__':
    main()
