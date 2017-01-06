# coding=utf-8
"""
Schema:
    Title
    Speaker
    Date
    Content
    SentenceIndex
    House/Senate/Extension (hse)
    Congress


:author: Andrew B Godbehere
:date: 12/27/16
"""

import urllib.request
from bs4 import BeautifulSoup
import pickle


def top_level_pages():
    rescrape = False
    try:
        urlinfo = pickle.load(open('urlinfo.pkl', 'rb'))
    except FileNotFoundError:
        rescrape = True

    if rescrape:
        session_url_template = "https://www.congress.gov/congressional-record/{}th-congress/browse-by-date"
        sessions = range(104, 115)

        data = {}

        for session in sessions:
            data[session] = {}
            session_url = session_url_template.format(session)
            data[session]['url'] = session_url
            req = urllib.request.Request(session_url, data=None, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
            with urllib.request.urlopen(req) as response:
                html = response.read()
                index_soup = BeautifulSoup(html, 'html5lib')
                for index_row in index_soup.find_all('tr'):
                    print("INDEX ROW")
                    # TODO: Get and format list of entries...
                    td_entries = index_row.find_all('td')
                    if len(td_entries) == 0:
                        continue

                    date = td_entries[0].text
                    data[session][date] = {}
                    print(td_entries)
                    senate = td_entries[2].a
                    try:
                        senate_url = senate['href']
                        senate_text = senate.text
                    except (TypeError, KeyError):
                        senate_url = None
                        senate_text = '--'
                    data[session][date]['senate'] = {'url': senate_url, 'text': senate_text}

                    house = td_entries[3].a
                    try:
                        house_url = house['href']
                        house_text = house.text
                    except (TypeError, KeyError):
                        house_url = None
                        house_text = '--'
                    data[session][date]['house'] = {'url': house_url, 'text': house_text}

                    extensions = td_entries[4].a
                    try:
                        extensions_url = extensions['href']
                        extensions_text = extensions.text
                    except (TypeError, KeyError):
                        extensions_url = None
                        extensions_text = '--'
                    data[session][date]['extensions'] = {'url': extensions_url, 'text': extensions_text}

                    # TODO: For each of these urls, get all pages

        with open('urlinfo.pkl', 'wb') as outfile:
            pickle.dump(data, outfile)

    print("DONE")


def get_text(url):
    pass

def get_all_pages():
    urlinfo = pickle.load(open('urlinfo.pkl', 'rb'))
    # add all pages into data structure...
    for session in iter(urlinfo.keys()):
        for date in iter(urlinfo[session].keys()):
            for sessiontype in ('senate', 'house', 'extensions'):
                if urlinfo[session][date][sessiontype]['url'] is not None:
                    url = urlinfo[session][date][sessiontype]['url']
                    req = urllib.request.Request(url, data=None, headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
                    with urllib.request.urlopen(req) as response:
                        html = response.read()
                        soup = BeautifulSoup(html, 'html5lib')
                        for index_row in soup.find_all('tr'):
                            td_entries = index_row.find_all('td')
                            if len(td_entries) == 0:
                                continue

                            title = td_entries[0].a.text
                            content = get_text(td_entries[0].a['href'])
                            if 'content' not in urlinfo[session][date][sessiontype]:
                                urlinfo[session][date][sessiontype]['content'] = []
                            urlinfo[session][date][sessiontype]['content'].append({'title': title, 'text': content})   # TODO: LEFT OFF HERE

if __name__ == "__main__":
    top_level_pages()


