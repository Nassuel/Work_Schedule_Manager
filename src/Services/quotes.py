import re
import random
import requests
from bs4 import BeautifulSoup

import variables_in
from main_logger import logger

class QuoteService():
    def __init__(self) -> None:
        logger.debug(': in: Quote Service started')
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
        
        logger.debug(': Quote service | Setting data')
        self.data = data

    def __get_random_quote(self):
        try:
            random_quote_data = self.data[random.randint(0,len(self.data))]
        except IndexError:
            random_quote_data = self.data[0]
        return f"{random_quote_data['quote']} \n {random_quote_data['author']}"