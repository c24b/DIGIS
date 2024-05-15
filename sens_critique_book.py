import os
import requests
from bs4  import BeautifulSoup as bs
import json

BASE_URL = "https://www.senscritique.com"

def get_the_soup(url):
    '''Recupérer le HTML à parti d'une url et parser le HTML d'une page à partir d'une url '''
    r = requests.get(url) 
    #proxies=proxy)
    if r.status_code == 200:
        return bs(r.text, "lxml")
    print(r.status_code)
    return None




# def get_details(url):
#     details_url = os.path.join(BASE_URL, url, "/details")
#     #https://www.senscritique.com/livre/Soeurs_dans_la_guerre/44819701/details
#     page = get_the_soup(details_url)
#     return page.find("div", {"data-testid": "synopsis"}).text.strip()
def map_liste(liste_def):
    keys = ['url', 'hits','likePositiveCount', 'listSubtype', 'productCount','label', 'description']
    return {k:v for k,v in liste_def.items() if k in keys}

def get_listes(book_id, page):
    listes = []
    for link in page.find_all("a"):
        #/livre/Soeurs_dans_la_guerre/critique/253661311
        href = link.get("href")
        #['', 'livre', 'Soeurs_dans_la_guerre', 'critique', '253661311']
        composed_link = href.split("/")
        # NIVEAU LISTE
        if len(composed_link) == 5 and "livre" in composed_link and composed_link[-1] == "listes":
            # print(href)
            critique_url = BASE_URL+ href
            # print(critique_url)
            c_page = get_the_soup(critique_url)
            
            data = json.loads(c_page.find_all("script")[-1].text)
            # print(data.keys())
            filter_listes = [map_liste(v) for k,v in data["props"]["pageProps"]['__APOLLO_STATE__'].items() if k.startswith("UserList:")]
            for liste in filter_listes:
                liste_url = BASE_URL+liste["url"]
                liste["url"] = liste_url
                liste_pages = [get_the_soup(liste_url)]
                liste_pages.extend([get_the_soup(liste_url+f"?page={page_nb}") for page_nb in [n.text for n in liste_pages[0].nav.find_all("span")][1:]])
                liste["book_urls"] = []
                for page in liste_pages:
                    for item in json.loads(page.script.text).get('itemListElement'):
                        liste["book_urls"].append(item["url"])        
                
                listes.append(liste)
            
    return listes

def get_critiques(book_id, page):
    critiques = []
    for link in page.find_all("a"):
        #/livre/Soeurs_dans_la_guerre/critique/253661311
        href = link.get("href")
        #['', 'livre', 'Soeurs_dans_la_guerre', 'critique', '253661311']
        composed_link = href.split("/")
        if len(composed_link) == 5 and "livre" in composed_link and composed_link[-2] == "critique":
            critique_url = BASE_URL+ href
            c_page = get_the_soup(critique_url)
            data = json.loads(c_page.script.text)
            
            critique = {
                "book_id": book_id,
                "url": critique_url,
                "titre": data["name"], 
                "texte": data["reviewBody"], 
                "auteur": data["author"]["name"], 
                "date": data["datePublished"],
                "auteur_url": data["author"]["url"],  
                "ratingValue": data["reviewRating"]["ratingValue"],
                "bestRating": data["reviewRating"]["bestRating"]
            }
            critiques.append(critique)
            
    return critiques
    
def get_book_infos(url):
    page = get_the_soup(url)
    book_id = url.split("/")[-1]
    script = page.find("script")
    data = json.loads(script.text)
    titre = data["name"]
    date = data["datePublished"]
    resume = data["description"]
    stats = data["aggregateRating"]
    del stats["@type"]
    auteur = data["creator"][0]
    # del auteur["@type"]
    auteur_name = auteur["name"]
    auteur_url = auteur["url"]
    # critique_urls = []
    # for a in page.find_all("a")
    # critique_urls = [BASE_URL + a.get("href")  if "critique" in a.get("href") and "livre" in a.get("href") and a.get("href").split("/")[-1].isnumeric()]
    # print(critique_urls)
    # get_critiques(book_id, page)
    info = {
        "url": url, 
        "titre": titre, 
        "resume": resume, 
        "date": date, 
        "auteur": auteur_name, 
        "auteur_url": auteur_url, 
    }
    # info.update(stats)
    for list in get_listes(book_id, page):
        print(list)
    return info, get_critiques(book_id, page), get_listes(book_id, page)
if __name__ == "__main__":
    info, critiques, listes = get_book_infos("https://www.senscritique.com/livre/Soeurs_dans_la_guerre/44819701")
    # print(info)
    # for critique in critiques:
    #     print(critique)