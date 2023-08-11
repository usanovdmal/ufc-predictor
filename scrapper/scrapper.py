import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "http://www.ufcstats.com/statistics/events/completed"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def get_event_links():
    response = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    event_links = [a['href'] for a in soup.select('.b-link.b-link_style_black')]
    return event_links


def scrape_event(event_link):
    response = requests.get(event_link, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Parse event data here...


def main():
    event_links = get_event_links()
    for link in event_links:
        scrape_event(link)


if __name__ == '__main__':
    main()
