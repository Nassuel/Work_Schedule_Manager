import logging
FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
logging.basicConfig(filename='logging.log', filemode='w+', format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__file__.split('\\')[-1].split('.')[0])
# Planning to add some more stuff here as I figure out more about the logging module

from enum import Enum
class EventType(Enum):
    GOOGLECALENDAR = 'google_calendar'
    OUTLOOKCALENDAR = 'outlook_calendar'

if __name__ == '__main__':
    print(f"Ran {__file__}")
else:
    print(f'Imported {__file__}')