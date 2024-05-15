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


def get_authors(url):
    book_page = get_the_soup(url)
    return [ 
        BASE_URL+n.get("href") 
        for n in book_page.find_all("a") 
        if n.get("href").startswith("/auteur/") and (n.get("href").split("/")[-1]).isnumeric() and "#" not in n.get("href")
    ]

def store_book_infos(filename, book_list):
    if len(book_list) > 0:
        with open(filename, "w") as fd:
            detail_writer = csv.DictWriter(fd, fieldnames=list(book_list[0].keys()))
            detail_writer.writeheader()
            for book in book_list:
                detail_writer.writerow(book)
    return book_list


def get_author_books(author_name, url):
    ''''''
    
    id_user = url.split("id_user=")[1]
    reading_url = f"https://www.babelio.com/historique_lecture_annee.php?id_user={id_user}"
    print(reading_url)
    page_book = get_the_soup(reading_url)
    if len(page_book.find_all("a")) != 0:
        return [ 
            {"user": author_name, "book": os.path.join(BASE_URL, n.get("href"))} 
            for n in page_book.find_all("a") 
            if n.get("href").startswith("/livres/") and (n.get("href").split("/")[-1]).isnumeric()
        ]
    

if __name__=="__main__":
    
    AUTHOR_BOOKS_UNLIKED = [("mimipinson","https://www.babelio.com/monprofil.php?id_user=12548"),
("carnetdelecture","https://www.babelio.com/monprofil.php?id_user=34870"),
("magaliverdonck","https://www.babelio.com/monprofil.php?id_user=214711"),
("val-m-les-livres","https://www.babelio.com/monprofil.php?id_user=7748")
]
    BOOK_LISTS =[]

    for name, url in AUTHOR_BOOKS_UNLIKED:
        print(name,url)
        BOOK_LISTS.extend(get_author_books(name, url))
    store_book_infos("BOOKS-UNLIKES.csv", BOOK_LISTS)
    AUTHORS_LIKED = [("biblioroz","https://www.babelio.com/monprofil.php?id_user=431968"),
    ("ssstella","https://www.babelio.com/monprofil.php?id_user=64833"),
    ("kittiwake","https://www.babelio.com/monprofil.php?id_user=28178"),
    ("Ancolie","https://www.babelio.com/monprofil.php?id_user=44581"),
    ("Myriam3",	"https://www.babelio.com/monprofil.php?id_user=134390"),
    ("Wanda50","https://www.babelio.com/monprofil.php?id_user=212087"),
    ("BibliothequeViroflay","https://www.babelio.com/monprofil.php?id_user=60498"),
    ("EManzoni","https://www.babelio.com/monprofil.php?id_user=1033166"),
    ("Clair-De-Lune","https://www.babelio.com/monprofil.php?id_user=10890"),
    ("MicheleLaframboise","https://www.babelio.com/monprofil.php?id_user=544232"),
    ("enisab","https://www.babelio.com/monprofil.php?id_user=647393")
    ]
    BOOKS_LIKED = []
    for name, url in AUTHORS_LIKED:
        BOOKS_LIKED.extend(get_author_books(name, url))
    store_book_infos("BOOKS-LIKES.csv", BOOKS_LIKED)
