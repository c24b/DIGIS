# LIVRES CLIFI vs SCIFI
import os
import requests
import json
from bs4 import BeautifulSoup as bs
import csv

BASE_URL = "https://babelio.org"

def get_the_soup(url):
    '''Recupérer la page HTML à partir d'une url et transformer le HTML en un arbre à parcourir'''
    r = requests.get(url) 
    if r.status_code == 200:
        return bs(r.text, "lxml")


def get_sens_critique_books(url):
    page = get_the_soup(url)
    data = json.loads(page.find_all("script")[-1].text)
    return list(set(["https://www.senscritique.com"+v["url"] for k,v in data["props"]["pageProps"]['__APOLLO_STATE__'].items() if "Product:" in k]))

def get_babelio_books(url):
    page_book = get_the_soup(url)
    return ["https://babelio.org"+n.get("href") for n in page_book.find_all("a") if (n.get("href")).startswith("/livres/") and (n.get("href").split("/")[-1]).isnumeric()]


def store_book_infos(filename, book_list):
    with open(filename, "w") as fd:
        detail_writer = csv.DictWriter(fd, fieldnames=list(book_list[0].keys()))
        detail_writer.writeheader()
        for book in book_list:
            detail_writer.writerow(book)
    return book_list


if __name__ == "__main__":
    URLS_CLIFI = ["https://www.babelio.com/liste/11951/Climate-fiction--romans-adultes","https://www.babelio.com/liste/9955/La-climate-fiction-ou-cli-fi", "https://www.senscritique.com/liste/climate_fiction/3657739"]
    BOOKS_CLIFI = []
    for url in URLS_CLIFI:
        if "senscritique" in url:
            BOOKS_CLIFI.extend([{"tag": "clifi", "book": book, "source":"senscritique"} for book in get_sens_critique_books(url)])
        else:
            print(url)
            BOOKS_CLIFI.extend([{"tag": "clifi", "book": book, "source":"babelio"} for book in get_babelio_books(url)])
    store_book_infos("CLIFI.csv", BOOKS_CLIFI)

    URLS_SCIFI = ["https://www.babelio.com/liste/9979/La-science-fiction-pour-ceux-qui-croient-ne-pas-ai","https://www.babelio.com/liste/2170/Quand-la-SF-se-camoufle-dans-la-litterature","https://www.senscritique.com/liste/science_fiction_livres/2107715"]
    BOOKS_CLIFI = []
    for url in URLS_SCIFI:
        if "senscritique" in url:
            BOOKS_CLIFI.extend([{"tag": "scifi", "book": book,"source":"senscritique"} for book in get_sens_critique_books(url)])
        else:
            BOOKS_CLIFI.extend([{"tag": "scifi", "book": book, "source":"babelio"} for book in get_babelio_books(url)])
    store_book_infos("SCIFI.csv", BOOKS_CLIFI)
