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

def store_book_infos(filename, book_list):
    with open(filename, "w") as fd:
        detail_writer = csv.DictWriter(fd, fieldnames=list(book_list[0].keys()))
        detail_writer.writeheader()
        for book in book_list:
            detail_writer.writerow(book)
    return book_list

def get_tag_urls(book_page):
    '''A partir de la page d'un livre extraire les urls des étiquettes qui lui correspondent'''
    return [os.path.join(BASE_URL, n.get("href")) for n in book_page.find_all("a") if "livres-" in n.get("href") and n.get("href").split("/")[-1].isnumeric()]

def extract_book_list_from_tag(row):
    '''A partir d'une page de tag, récupérer la liste de tous les livres qui portent ce tag
    créer un fichier excel science-fiction.csv avec la liste des livres
    '''
    books = []
    pages = [get_the_soup(row["url"])] 
    last_page_nb = max([int(n.text.strip()) for n in pages[0].find_all("a") if n.get("href").startswith("/livres-/") and "page=" in n.get("href") and n.text.strip() != ""])
    for i in range(2, last_page_nb+1):
        pages.append(get_the_soup(row["url"]+f"?page={i}"))
    for page in pages:
        for n in page.find_all("a"):
            href = n.get("href")
            id = href.split("/")[-1]
            if href is not None and href.startswith("/livres/") and  "#" not in href and id.isnumeric():
                url = BASE_URL+ href
                print(url)
                books.append(url)
    return books   

if __name__=="__main__":
    HUMOUR_TAGS_URL = []
    ADD_HUMOUR_TAGS = []
    CLIFI_TAGS_URL = []
    ADD_HUMOUR_TAGS = []