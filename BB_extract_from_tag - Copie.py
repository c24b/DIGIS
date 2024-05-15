#!/usr/bin/env python3
__doc__="Extraire les livres associés à un tag"

import os
import requests
from bs4 import BeautifulSoup as bs
import csv

BASE_URL = "http://www.babelio.com"

def get_the_soup(url):
    '''Recupérer le HTML à parti d'une url et parser le HTML d'une page à partir d'une url '''
    # if not url.startswith(BASE_URL):
    #     url = os.path.join(BASE_URL, url)
    r = requests.get(url) 
    #proxies=proxy)
    if r.status_code == 200:
        return bs(r.text, "lxml")
    raise ConnectionError(url+" unavailable")

def get_tag_names(book_page):
    '''A partir de la page d'un livre extraire les noms des étiquettes qui lui correspondent'''
    return [n.text for n in book_page.find_all("a") if "livres-" in n.get("href") and n.get("href").split("/")[-1].isnumeric()]

def get_tag_urls(book_page):
    '''A partir de la page d'un livre extraire les urls des étiquettes qui lui correspondent'''
    return [os.path.join(BASE_URL, n.get("href")) for n in book_page.find_all("a") if "livres-" in n.get("href") and n.get("href").split("/")[-1].isnumeric()]

def get_linked_book_urls(book_page):
    '''A partir de la page d'un livre extraire les urls des livres conseillés'''
    return [ 
        os.path.join(BASE_URL, n.get("href")) 
        for n in book_page.find("div", {"class":"list_livre_con"}).find_all("a") 
        if n.get("href").startswith("/livres/") and (n.get("href").split("/")[-1]).isnumeric()
    ]
def get_linked_book_ids(book_page):
    '''A partir de la page d'un livre extraire les ids des livres conseillés'''
    return [ 
        int(n.get("href").split("/")[-1]) 
        for n in book_page.find("div", {"class":"list_livre_con"}).find_all("a") 
        if n.get("href").startswith("/livres/") and (n.get("href").split("/")[-1]).isnumeric() and "#" not in n.get("href") 
    ]
def get_authors(book_page):
    return [ 
        os.path.join(BASE_URL, n.get("href")) 
        for n in book_page.find_all("a") 
        if n.get("href").startswith("/auteur/") and (n.get("href").split("/")[-1]).isnumeric() and "#" not in n.get("href")
    ]
def get_book_detail(book_page, id):
    return {
        "id": id,
        "auteur": get_authors(book_page)[0],
        "titre": book_page.find("h1").text.strip(),
        "resume": book_page.find("div", {"id": "d_bio"}).text.strip().split("... >Voir plus")[0],
        "rating": book_page.find("span", {"itemprop": "ratingValue"}).text,
        "votes": book_page.find("span", {"itemprop": "ratingCount"}).text,
        "linked_books": get_linked_book_ids(book_page),
        "tags":  get_tag_names(book_page)
    }

def extract_book_list_from_tag(row):
    '''A partir d'une page de tag, récupérer la liste de tous les livres qui portent ce tag
    créer un fichier excel science-fiction.csv avec la liste des livres
    créer un fichier excel science-fiction-critiques avec la liste des critiques de tous les livres 
    '''
    pages = [get_the_soup(row["url"])] 
    last_page_nb = max([int(n.text.strip()) for n in pages[0].find_all("a") if n.get("href").startswith("/livres-/") and "page=" in n.get("href") and n.text.strip() != ""])
    for i in range(2, last_page_nb+1):
        pages.append(get_the_soup(row["url"]+f"?page={i}"))
    print(len(pages))
    with open(f"TAG-{row['name']}-details.csv", "w") as fd:
        detail_writer = csv.DictWriter(fd, fieldnames=["id","auteur","titre","resume","rating","votes","linked_books","tags"])
        detail_writer.writeheader()
        #["id", "Auteur", "Titre", "Resumé", "Note générale", "Total des Notes", "ID des livres conseillés", "Etiquettes associées"]
        with open(f"TAG-{row['name']}-booklist.csv", "w") as f:
            list_writer = csv.writer(f, delimiter=",")
            list_writer.writerow("id,url\n")
            for page in pages:
                for n in page.find_all("a"):
                    href = n.get("href")
                    id = href.split("/")[-1]
                    if href is not None and href.startswith("/livres/") and  "#" not in href and id.isnumeric():
                        url = BASE_URL+ href
                        print(url)
                        id = int(id)
                        list_writer.writerow(f"{id},'{url}'\n")
                        book_page = get_the_soup(url)
                        book_details = get_book_detail(book_page, id)
                        detail_writer.writerow(book_details)

if __name__== "__main__":
    starting_page = {"url": "https://www.babelio.com/livres-/science-fiction/6", "name": "science-fiction", "id": 6}
    extract_book_list_from_tag(starting_page)

