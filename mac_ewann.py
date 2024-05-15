import os
import requests
import json
from bs4 import BeautifulSoup as bs
import csv

BASE_URL = "https://babelio.com"

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

def get_tags(url):
    '''A partir de la page d'un livre extraire les urls des étiquettes qui lui correspondent'''
    book_page = get_the_soup(url)
    return [{"text":n.text, "url": BASE_URL+ n.get("href")} for n in book_page.find_all("a") if "livres-" in n.get("href") and n.get("href").split("/")[-1].isnumeric()]

def get_tags_name(url, tag):
    # print(">>", url, tag)
    if url.strip() is not None :
        soup = get_the_soup(url)
        if soup is not None:
            links =  soup.find_all("a")
            if len(links) > 0:
                return [ n.text.strip() for n in links if "livres-" in n.get("href") and n.get("href").split("/")[-1].isnumeric() and n.text.strip() != tag]
    return []

def get_tag_urls(book_page):
    '''A partir de la page d'un livre extraire les urls des étiquettes qui lui correspondent'''
    return [os.path.join(BASE_URL, n.get("href")) for n in book_page.find_all("a") if "livres-" in n.get("href") and n.get("href").split("/")[-1].isnumeric()]

def extract_book_list_from_tag(url):
    '''A partilsr d'une page de tag, récupérer la liste de tous les livres qui portent ce tag
    créer un fichier excel science-fiction.csv avec la liste des livres
    '''
    
    books = []
    pages = [get_the_soup(url)]
    next_pages = [int(n.text.strip()) for n in pages[0].find_all("a") if n.get("href").startswith("/livres-/") and "page=" in n.get("href") and n.text.strip() != ""] 
    if len(next_pages) > 0:
        last_page_nb = max(next_pages)
        for i in range(2, last_page_nb+1):
            pages.append(get_the_soup(url+f"?page={i}"))
    for page in pages:
        for n in page.find_all("a"):
            href = n.get("href")
            id = href.split("/")[-1]
            if href is not None and href.startswith("/livres/") and  "#" not in href and id.isnumeric():
                url = BASE_URL+ href
                books.append(url)
    return list(set(books))   

def store_book_infos(filename, book_list):
    with open(filename, "w") as fd:
        detail_writer = csv.DictWriter(fd, fieldnames=list(book_list[0].keys()))
        detail_writer.writeheader()
        for book in book_list:
            detail_writer.writerow(book)
    return book_list
def collect_and_store():
    humour_books = extract_book_list_from_tag('https://www.babelio.com/livres-/humour/15')
    clifi_books = extract_book_list_from_tag('https://www.babelio.com/livres-/cli-fi/369070')
    with open("TAGS-humour.csv", "a") as fo:
        fo.write("tag\ttarget_tag\n")
        for book in humour_books:
            for book_tag in get_tags_name(book.strip(), "humour"):
                if "Voir" not in book_tag:
                    fo.write(book_tag.strip()+"\t"+ "humour\n")
                    print(book_tag.strip()+"\t"+ "humour\n")
    with open("TAGS-clifi.csv", "w") as fo:
        fo.write("tag\ttarget_tag\n")
        for book in set(clifi_books):
            for book_tag in get_tags_name(book, "cli-fi"):
                if "Voir" not in book_tag:
                    fo.write(book_tag+"\t"+ "cli-fi\n")
            
    
def count_tags_frequency(filename="TAGS-clifi.csv"):
    from collections import Counter
    with open(filename, "r", encoding='latin-1') as f:
        # with open("STATS-"+filename, "w") as fout:
        reader = csv.DictReader(f,  delimiter="\t")
        tags = [r['Tag'].strip() for r in reader]
        freq = Counter(tags)
            # for k, v in freq.items():
            #     fout.write("\t".join([k, str(v)])+"\n")
        # print(" ".join(tags))
        return freq

def count_coocurrence():
    freq_CLIFI = count_tags_frequency(filename="TAGS-clifi.csv")
    freq_HUMOUR = count_tags_frequency(filename="TAGS-humour.csv")
    CLIFI = list(freq_CLIFI.keys())
    HUMOUR = list(freq_HUMOUR.keys()) 
    import matplotlib.pyplot as plt
    from matplotlib_venn import venn2
        
    print(len(CLIFI), "mots clés associés à CLIFI")
    print(len(HUMOUR), "mots clés associés à HUMOUR")
    common = set(CLIFI).intersection(HUMOUR)
    print(common, "en commun")

    # Use the venn2 function
    venn2(subsets = (len(CLIFI), len(HUMOUR), len(common)), set_labels = ('CLIFI', 'HUMOUR'))
    plt.show()

def build_cloud_coocurence():
    freq_CLIFI = count_tags_frequency(filename="TAGS-clifi.csv")
    freq_HUMOUR = count_tags_frequency(filename="TAGS-humour.csv")
    CLIFI = list(freq_CLIFI.keys())
    HUMOUR = list(freq_HUMOUR.keys()) 
    common = set(CLIFI).intersection(HUMOUR)
    common_counter = {}
    for word in common:
        common_counter[word] = freq_CLIFI[word]+ freq_HUMOUR[word]
    build_tag_cloud(common_counter)

def build_tag_cloud(frequency_list):
    import numpy as np
    from PIL import Image
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    
    text = []
    for tag, nb in frequency_list.items():
        text.append(tag*nb)
    final_text = (" ").join(text)
    
    wordcloud = WordCloud().generate(final_text)
    
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()

if __name__=="__main__":
    import json
    #count_tags_frequency(filename="TAGS-humour.csv")
    #count_tags_frequency(filename="TAGS-clifi.csv")
    count_coocurrence()
    # build_tag_cloud()
    build_cloud_coocurence()