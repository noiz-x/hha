import re
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from unidecode import unidecode

def remove_punctuation(input_string):
    return re.sub(r'[^\w\s]', '', input_string)

def find_best_tag(result_tags, inp_lower):
    for tag in result_tags:
        tag_text = remove_punctuation(unidecode(tag.get_text().lower()))
        if inp_lower == tag_text:
            return tag
    return None

def get_hymn_text(title):
    title = remove_punctuation(title.lower())
    try:
        with requests.Session() as session:
            response = session.get(f'http://www.hymntime.com/tch/ttl/ttl-{title[0]}.htm')
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('a')
            link = find_best_tag(results, title)['href']
            response = session.get(f'http://www.hymntime.com/tch/ttl/{link}')
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find(class_='lyrics-text mc').find_all('p')
            for i in results:
                for j in i.find_all('br'):
                    j.replace_with('\r\n')
            hymn_text = [unidecode(i.get_text()) for i in results]
            return hymn_text, title
    except RequestException:
        return None

