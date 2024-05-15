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

def get_author_insignes( url, tag):
    page = get_the_soup(url)
    
    try:
        author_name = page.find("div", {"class":"livre_titre"}).text.strip()
    except AttributeError:
        author_name = url.split("=")[1]
    return [ {"user": author_name, "tag": tag, "badge": 
        n.get("href").split("/")[-1]
        }  
        for n in page.find_all("a") 
        if n.get("href").startswith("/insignes/") and (n.get("href").split("/")[-1]).isnumeric() and "#" not in n.get("href")
    ]

def store_book_infos(filename, book_list):
    print(book_list)
    if len(book_list) > 0:
        with open(filename, "w") as fd:
            detail_writer = csv.DictWriter(fd, fieldnames=list(book_list[0].keys()))
            detail_writer.writeheader()
            for book in book_list:
                detail_writer.writerow(book)
    return book_list

if __name__=="__main__":
    USER_CLIFI=["https://www.babelio.com/mesbadges.php?id_user=431968",
"https://www.babelio.com/monprofil.php?id_user=431968",
"https://www.babelio.com/monprofil.php?id_user=353118",
"https://www.babelio.com/monprofil.php?id_user=107394",
"https://www.babelio.com/monprofil.php?id_user=51204",
"https://www.babelio.com/monprofil.php?id_user=228299",
"https://www.babelio.com/monprofil.php?id_user=209479",
"https://www.babelio.com/monprofil.php?id_user=839460",
"https://www.babelio.com/monprofil.php?id_user=327791",
"https://www.babelio.com/monprofil.php?id_user=915459",
"https://www.babelio.com/monprofil.php?id_user=490565",
"https://www.babelio.com/monprofil.php?id_user=1414988",
"https://www.babelio.com/monprofil.php?id_user=857541",
"https://www.babelio.com/monprofil.php?id_user=173855",
"https://www.babelio.com/monprofil.php?id_user=844013",
"https://www.babelio.com/monprofil.php?id_user=346274",
"https://www.babelio.com/monprofil.php?id_user=1150138"]
    USER_SCIFI = ["https://www.babelio.com/monprofil.php?id_user=586582",
    "https://www.babelio.com/monprofil.php?id_user=107394",
    "https://www.babelio.com/monprofil.php?id_user=445897",
    "https://www.babelio.com/monprofil.php?id_user=1142164",
    "https://www.babelio.com/monprofil.php?id_user=1146137",
    "https://www.babelio.com/monprofil.php?id_user=1069260",
    "https://www.babelio.com/monprofil.php?id_user=1478160",
    "https://www.babelio.com/monprofil.php?id_user=11802",
    "https://www.babelio.com/monprofil.php?id_user=769639",
    "https://www.babelio.com/monprofil.php?id_user=1176333",
    "https://www.babelio.com/monprofil.php?id_user=814439",
    "https://www.babelio.com/monprofil.php?id_user=1485255",
    "https://www.babelio.com/monprofil.php?id_user=79553",
    "https://www.babelio.com/monprofil.php?id_user=155174",
    "https://www.babelio.com/monprofil.php?id_user=1275739",
    "https://www.babelio.com/monprofil.php?id_user=1220644",
    "https://www.babelio.com/monprofil.php?id_user=1866741",
    "https://www.babelio.com/monprofil.php?id_user=107804",
    "https://www.babelio.com/monprofil.php?id_user=1607303"]

    BADGES_CLIFI = []
    for url in USER_CLIFI:
        insignes = get_author_insignes(url, tag="clifi")
        BADGES_CLIFI.extend(get_author_insignes(url, tag="clifi"))

        
    store_book_infos("BADGES-CLIFI.csv", BADGES_CLIFI)

    BADGES_SCIFI = []
    for url in USER_SCIFI:
        BADGES_SCIFI.extend(get_author_insignes(url, tag="scifi"))

    store_book_infos("BADGES-SCIFI.csv", BADGES_CLIFI)
