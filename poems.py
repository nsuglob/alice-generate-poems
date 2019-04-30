import cfscrape
import requests
from bs4 import BeautifulSoup as soup
import json


VERSION = 0
ALLOW_TODAY = False


def by_last_poems(last_poems):
    url = "https://yandex.ru/autopoet"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20180101 Firefox/47.0",
        "Referer": url
    }
    session = requests.session()
    scraper = cfscrape.create_scraper(sess=session)
    r = scraper.get(url, headers=headers)
    page = soup(r.text, "html.parser")

    data = page.select('.verse.verse_offline_no.verse_state_disappear')[0].get('data-bem')
    data = json.loads(data)['verse']['verses']

    try:
        last_poems = list(map(int, last_poems))
    except:
        pass

    for verse in data:
        if int(verse['id']) not in last_poems:
            return verse
    return data[0]


def get(last_poems=[]):
    if ALLOW_TODAY:
        from generator import generate_poem
        return generate_poem.main()
    else:
        return by_last_poems(last_poems)


print(get(last_poems=[]))