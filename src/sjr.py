from __future__ import absolute_import, division, print_function, unicode_literals
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import hashlib
import random
import requests
import time
import datetime
import urllib3


_GOOGLEID = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()[:16]
_COOKIES = {'GSP': 'ID={0}:CF=4'.format(_GOOGLEID)}
_HEADERS = {
    'accept-language': 'en-US,en',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml'
    }
_HOST = 'https://www.scimagojr.com/'
_JOURNALSEARCH = '/journalsearch.php?q=={0}'
_SESSION = requests.Session()
_PAGESIZE = 100


def _get_page(pagerequest):
    time.sleep(5+random.uniform(0, 5))
    resp = _SESSION.get(pagerequest, headers=_HEADERS, cookies=_COOKIES)
    if resp.status_code == 200:
        return resp.text
    if resp.status_code == 503:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))

def _get_soup(pagerequest):
    html = _get_page(pagerequest)
    html = html.replace(u'\xa0', u' ')
    return BeautifulSoup(html, 'html.parser')

class Journal(object):
    def __init__(self,__data):
        self.ISSN = __data
        soupr = _get_soup(_HOST+_JOURNALSEARCH+self.ISSN)
        result = soupr.find_all('div', class_ = 'search_results')[0].find('a').get('href')
        soup = _get_soup(_HOST+result)
        column = soup.find('div',class_ = 'journaldescription colblock')
        self.title = column.find('h1').text[3:]
        self.hindex = soup.find('div', class_ = 'hindexnumber').text
        table = column.find_all('td')
        for i in table:
            if i.text == 'Publisher':
                self.publisher = i.parent.find('a').text
        dashboard = soup.find_all('div',class_ = 'cell2x1 dynamiccell')
        quartil_raw = dashboard[0].find('table').find_all('tr')
        quartil = list()
        for i in quartil_raw:
            quartil.append([x.text for x in i.find_all('td')])
        quartil.pop(0)
        keys = set()
        for i in quartil:
            keys.add(i[0])
        keys = list(keys)
        self.quartiles = dict()
        for i in keys:
            self.quartiles[i] = dict()
        for i in quartil:
            for j in keys:
                if i[0] == j:
                    self.quartiles[j][i[1]] = i[2]      
   

