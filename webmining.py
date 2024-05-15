import os
import requests
from bs4  import BeautifulSoup as bs

BASE_URL = "http://babelio.fr"
def get_the_soup(url):
    '''Recupérer la page HTML à partir d'une url et transformer le HTML en un arbre à parcourir'''
    r = requests.get(url) 
    #proxies=proxy)
    if r.status_code == 200:
        return bs(r.text, "lxml")
    
def extract_title(page):
    '''A partir d'une page parsée, découper la valeur qui nous intéresse ici en nous aidant des balises HTML et du CSS
    et le renvoyer pour le stocker'''
    title = page.find("h1", {"class": "titre"})
    return title

def get_links(url, page):
    links = []
    for a in page.find_all("a"):
        if not a.get("href").startswith("http"):
            link = os.path.join(BASE_URL, a.get("href"))
            if link != BASE_URL+"/" and link != url:
                links.append(link)
    return list(set(links))

def get_next_page(page):
    '''A partir d'une page: récupérer l'url de la page suivante'''
    next_url = page.find("a", {"class":"icon-next"})
    if next_url is not None:
        return get_the_soup(os.path.join(BASE_URL, next_url))
    return None  

def crawling(starting_url):
    '''Parcourir, extraire et stocker toutes les pages d'un site à partir d'une url de départ'''
    starting_page = get_the_soup(starting_url)
    links = get_links(starting_page)
     
    while len(links) > 0:
        for link in links:
            page = get_the_soup(link)
            title = extract_title(page)
            links.remove(link)
            links.extend(get_links(starting_page))
            yield(title, link)
            if len(links)== 0:
                break
        