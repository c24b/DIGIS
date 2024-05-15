#!/.venv/bin/python3

import os
import requests
from bs4  import BeautifulSoup as bs
import json
import csv

BASE_URL = "https://www.babelio.com"
STARTING_URL = "https://www.babelio.com/decouvriretiquettes.php"
TYPES_IDENT = [("tag", "livres-"), ("book", "livres"), ("auteur", "auteur"), ("author", "auteur"), ("publisher", "editeur"), ("work", "serie")]
TYPES_DICT = {"tag": "livres-", "book": "livres", "author": "auteur", "auteur": "auteur", "publisher": "editeur", "work": "serie"}
# proxy = {
#     'http': "4barbes%40gmail.com%3AV3n1%2CV1d1%2CV1c1@be154.nordvpn.com",
#     'https': "4barbes%40gmail.com%3AV3n1%2CV1d1%2CV1c1@be154.nordvpn.com",
# }



def get_the_soup(url):
    '''Recupérer le HTML à parti d'une url et parser le HTML d'une page à partir d'une url '''
    r = requests.get(url) 
    #proxies=proxy)
    if r.status_code == 200:
        return bs(r.text, "lxml")
    print(r.status_code)
    return None



def get_next_page(page):
    '''Récupère la page suivante'''
    next_url = page.find("a", {"class":"icon-next"})
    if next_url is not None:
        return get_the_soup(os.path.join(BASE_URL, next_url))
    return None  

def get_id(n):
    try:
        return int(n.get("href").split("/")[-1])
    except ValueError:
        try:
            return int(n.get("href").split("/")[-2])
        except ValueError:
            return n.get("href").split("/")[-2]

def extract_ressource(block, _type, item_nb=1):
    '''Recupérer une ressource generique (id, url, type, nom) en fonction de son type à partir d'un block HTML'''
    if _type not in TYPES_DICT.keys():
        raise KeyError(f"Type '{_type}' not supported in extract_ressource")
    try:
        identifier = TYPES_DICT[_type]
    except KeyError:
        raise KeyError(f"Type '{_type}' not supported in extract_ressource")
    results = [
        {   
            "type": _type,
            "id": get_id(n),
            "uid": f"{_type}-{get_id(n)}",
            "url":os.path.join(BASE_URL, n.get("href")), 
            "name": n.text.strip()
        } 
            for n in block.find_all("a") if n.get("href").startswith(f"/{identifier}/") 
    ]
    if item_nb == 1:
        try:
            return results[0]
        except IndexError:
            return {}
    return results 
def flat_ressource(block, _type, item_nb=1):
    dict_res = extract_ressource(block, _type, item_nb)
    if dict_res is not None:
        if item_nb == 1:
            ressource = {}
            for k, v in dict_res.items():
                if k != "type":
                    ressource[_type+"_"+k] = v
            return ressource
        else:
            new_ressource_list = []
            for item in dict_res:
                ressource = {}
                for k, v in item.items():
                    if k != "type":
                        ressource[_type+"_"+k] = v
                    
                new_ressource_list.append(ressource)
            return new_ressource_list
    else:
        return {}

def get_book_details(page):
    reco_books = page.find("div", {"class":"list_livre_con"})
    tags = extract_ressource(page, "tag", 2)
    linked_books = extract_ressource(reco_books, "book", 2)
    author = flat_ressource(page.find("div", {"class": "list_livre_con"}), "author", 1)
    publisher = flat_ressource(page.find("div", {"class": "list_livre_con"}), "publisher", 1)
    book = {
        "titre": page.find("h1").text.strip(),
        
        "resume": page.find("div", {"id": "d_bio"}).text.strip().split("... >Voir plus")[0],
        "tag_names": [t["name"] for t in tags],
        "rating": page.find("span", {"itemprop": "ratingValue"}).text,
        "votes": page.find("span", {"itemprop": "ratingCount"}).text,
        "linked_books_ids": [n["id"] for n in linked_books]
    }
    book.update(author)
    book.update(publisher)
    return book 
    # title = page.find("h1").text.lower()
    # resume = page.find("div", {"id": "d_bio"}).text
    # author = page.find("span", {"itemprop": "name"}).text
    # editeur = page.find_all("a") if a.get("href").start
    # note = page.find("span", {"itemprop": "ratingValue"}).text
    # refs = dict(zip(["ref", "pages_nb", "editeur_date"], [n.text for n in page.find("div",{"class": "livre_refs"}).split("<br>")]))
    # comments_nb = page.find("span", {"itemprop": "ratingCount"}).text



def extract_comment_details(page):
    note_block = page.find("div", {"class":"entete_login"}).find_all("span")
    if note_block is not None and len(note_block) > 0:
        note = float([n.get("content") for n in note_block[-1].find_all("meta") if n.get("itemprop") == 'ratingValue'][0])
        likes =  page.find("div", {"class":"post_items_like"})
        reactions =   page.find("div", {"class":"post_items_com"}).text
    else:
        note = 'NA'
        likes = 'NA'
        reactions = 'NA'
    return {
        "type": "comment",
        "author" : page.find("img").get("alt"),
        "note" : note,
        "likes": likes, 
        "reactions": reactions,
        "date" : page.find("div", {"class":"entete_date"}).find("span").text,
        "text" : page.find("div", {"class":"cri_corps_critique"}).text.strip()
    }

# def extract_book(book):
#     book_info = get_book_details(book)
#     book_tags = get_link(book.find("p", {"class":"tags"}), "tag", "livres-")
#     book_linked = get_link(book.find("div", {"class": "list_livre_con"}), "tag", "livres-")
#     #comments = [(extract_comment_details(n), n.get("id")) for n in book.find_all("div", {"class": "post_con"})]
#     print(book_info, book_tags, book_linked)

# def get_books(page, _books):
#     books = get_link(page, "book", "livres")
#     authors = get_link(page, "author", "auteur")
#     ratings = [p.findAll("h3")[1].text.strip().split("★") for p in page.findAll(attrs={"itemtype": "http://schema.org/Book"})]
    
#     for b, a, r in zip(books, authors, ratings):
#         b["author"] = a
#         b["ratings"] = [m.strip() for m in r]
#         # b["ratings"] = {"rating":r[0].strip(), "count": r[1].strip()}
#         _books.append(b)
#     next_page = page.find("a", {"class":"icon-next"})
#     if next_page is not None:
#         return get_books(next_page, _books)    
#     return _books
def get_tags():
    '''Extract all tags links from MAIN PAGE TAGS'''
    starting_page = get_the_soup("https://www.babelio.com/decouvriretiquettes.php")
    tag_urls = [(n.text.strip(), "https://www.babelio.com"+n.get("href")) for n in starting_page.find_all("a") if "livres-" in n.get("href")]
    with open("tags.csv", "w") as f:
        f.write("tag,url\n")
        for tag_url in tag_urls:
            f.write((",").join(tag_url)+"\n")

def get_book_url_list(csv_books= "babelio_books_u.csv"):
    clean_url_list = []
    with open("babelio_books_clean.csv", "w") as csvfileout:
        csvfileout.write("url"+"\n")
        with open(csv_books, "r") as csvfilein:
            reader = csv.DictReader(csvfilein)
            for row in reader:
                if "#" not in row["url"]:
                    if row["url"] not in clean_url_list:
                        clean_url_list.append(row["url"])
                       
                        csvfileout.write(row["url"]+"\n")
    return clean_url_list
# def get_books():
#     '''Extract all books links from TAGS'''
#     with open("books3.csv", "w") as csvfileout:
#         writer = csv.DictWriter(csvfileout, fieldnames=["tag", "titre", "url"])
#         with open("tags2.csv", "r") as csvfile:
#             reader = csv.DictReader(csvfile)
#             for row in reader:
#                 book_page1 = get_the_soup(row["url"])
#                 last_page = max([int(n.text.strip()) for n in book_page1.find_all("a") if n.get("href").startswith("/livres-/") and "page=" in n.get("href") and n.text.strip() != ""])
#                 #page_1
#                 book_urls = [{"tag": row["tag"], "titre": n.text.strip(), "url":"https://www.babelio.com"+n.get("href")} for n in book_page1.find_all("a") if n.get("href").startswith("/livres/")]
#                 for i in range(2, last_page+1):
#                     book_next_page = get_the_soup(row["url"]+f"?page={i}")
#                     book_urls.extend([{"tag": row["tag"], "titre": n.text.strip(), "url":"https://www.babelio.com"+n.get("href")} for n in book_next_page.find_all("a") if n.get("href").startswith("/livres/")])
#                 writer.writerows(book_urls)

def extract_critique(book_id, page_block):
    id = page_block.get("id")
    #"/monprofil.php?id_user=37732"
    date = page_block.find("div", {"class":"entete_date"}).text
    user_link = page_block.find("a", {"class":"lien_croco"})
    user_id = user_link.get("href").split("=")[1]
    name = user_link.text
    texte = " ".join([n.strip() for n in page_block.find("div", {"class":"cri_corps_critique"}).text.strip().split("\n")])
    note = page_block.find("meta", itemprop="ratingValue")
    if note is not None:
        note = note.get("content")
    #note = page_block.find("div", {"class":"rateit-range"}).get("aria-valuenow")
    return {"book_id":book_id, "id": id, "date":date, "user_id": user_id, "user_name": name, "user_link": "https://babelio.fr"+ user_link.get("href"), "texte": texte, "note": note}

def get_book_stats(page):
    note = page.find("div", {"class":'grosse_note'})
    note_total = page.find("div", {"class":"hc_gauche"}).find("span", {"class":"gris"})
    avis = {int(a.get("href").split("note=")[1]): int(a.get("title").split(" ")[0]) for a in page.find_all("a") if "/critiques?note=" in a.get("href")}
    avis.update({"note_moyenne":note.text.strip(), "note_nb":sum(list(avis.values())), "note_count": note_total.text})
    return avis
    
def get_critiques(url):
    #https://www.babelio.com/livres/Minier-Les-Effacees/1616011/critiques
    book_id = url.split("/")[-1]
    critique_url = url+"/critiques"
    critique_page1 = get_the_soup(critique_url)
    last_page = max([int(n.text.strip()) for n in critique_page1.find_all("a") if n.get("href").startswith("/livres/") and "critiques" in n.get("href") and "?a=a&pageN=" in n.get("href") and n.text.strip() != ""])
    
    critiques = [extract_critique(book_id, b) for b in critique_page1.find_all("div", {"class": "post_con"})]
    for i in range(2, last_page+1):
        book_next_page = get_the_soup(critique_url+f"?a=a&pageN={i}")
        critiques.extend([extract_critique(book_id, b) for b in book_next_page.find_all("div", {"class": "post_con"})])
    return critiques


def extract_babelio_book(url):
    page = get_the_soup(url)
    stats = get_book_stats(page)
    infos = get_book_details(page)
    book_id = int(url.split("/")[-1])
    book = {"id": book_id,"url": url}
    book.update(stats)
    book.update(infos)
    critiques = get_critiques(url)
    book.update({"critique_count": len(critiques), "critique_ids": [n["id"] for n in critiques]})
    
    with open(f'{book_id}.csv', "w") as fout:
        book_writer = csv.DictWriter(fout, fieldnames=list(book.keys()))
        book_writer.writeheader()
        book_writer.writerow(book)
    with open(f'{book_id}-critiques.csv', "w") as fout2:
        critique_writer = csv.DictWriter(fout2, fieldnames=list(critiques[0].keys()))
        critique_writer.writeheader()
        critique_writer.writerows(critiques)
    return book, critiques

if __name__ == "__main__":
    clean_url_list = get_book_url_list()
    print(len(clean_url_list))