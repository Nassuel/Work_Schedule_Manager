import logging
FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
logging.basicConfig(filename='logging.log', filemode='w+', format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__file__.split('\\')[-1].split('.')[0])

# Planning to add some more stuff here as I figure out more about the logging module