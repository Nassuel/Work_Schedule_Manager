import pandas as pd
import win32com.client
from datetime import datetime

from pandas.core.frame import DataFrame

from typing import Any, List

class EventCreation(object):

    def __init__(self, df: DataFrame) -> None:
        self.df = df
        self.appointment_list = []
        self.appointment_list_readable = []

    def build_events(self, subject, location, recipient):
        for row in self.df.iterrows():
            actual_row = row[1]
            
            if not(pd.isna(actual_row.end_time_converted)) or not(pd.isna(actual_row.start_time_converted)):
                start = datetime.strftime(actual_row.start_time_converted, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(actual_row.end_time_converted, '%Y-%m-%d %H:%M:%S')
                duration = actual_row.duration
                self.appointment_list_readable.append({'start': start, 'subject': subject, 'end': end, 'location': location, 'recipient': recipient})
                self.appointment_list.append(self._create_event(start=start, subject=subject, end = end, location=location, recipient=recipient))

    def send_events(self) -> None:
        """
        docstring
        """
        for appt in self.appointment_list:
            appt.Save()
            appt.Send()

    @staticmethod
    def _create_event(start, subject, location, recipient, end=None, duration=None) -> Any:
        """
        docstring
        """
        pass
        oOutlook = win32com.client.Dispatch("Outlook.Application")
        
        appointment = oOutlook.CreateItem(1) # 1=outlook appointment item
        
        appointment.Start = start
        appointment.Subject = subject
        # appointment.Duration = duration
        appointment.End = end
        appointment.Location = location
        appointment.ReminderSet = True
        appointment.ReminderMinutesBeforeStart = 30

        appointment.MeetingStatus = 1
        appointment.Recipients.Add(recipient)

        return appointment

def main():
    file_location = './Pictures/1-11-2021_1-17-2021_schedule.jpg'
    df = pd.read_csv('./Schedule_Dfs/1-11-2021_1-17-2021_schedule.csv')
    v_crtn = EventCreation(df)
    v_crtn.build_events('Día de Trabajo', 'Costco (1175 N 205th St, Shoreline, WA  98133, United States)', 'valeracuevan@spu.edu')
    print(v_crtn.appointment_list_readable)
    # v_crtn.send_events()
        
if __name__ == '__main__':
    main()
