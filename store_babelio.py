# import os
# import requests
# from bs4  import BeautifulSoup as bs
# import json
# import csv


# from pymongo import MongoClient

# client = MongoClient()
# db = client.babelio
# books = db.books
import sqlite3
con = sqlite3.connect("babelio.db")
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS tag") 
create_table_tag = '''
CREATE TABLE tag(
    tag_id TEXT PRIMARY KEY NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE
);
'''
cur.execute(create_table_tag)
cur.execute("DROP TABLE IF EXISTS book")

create_table_book = '''
CREATE TABLE book(
    _id INTEGER PRIMARY KEY ,
    title TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL UNIQUE,
    tags INT[]
);
'''
cur.execute(create_table_book);
import psycopg2
import pandas as pd

conn = psycopg2.connect(database = "babelio", 
                        user = "postgres", 
                        host= 'localhost',
                        password = "AbyssusAbyssumInvocat!")
# Toutes les pages de tous les livres référencé sur Babelio
# with open("book_list.csv", "r") as csvfile:
    # load the data into a Pandas DataFrame
tags = pd.read_csv("tags.csv")
books = pd.read_csv("book_list.csv")
u_tags = books.drop_duplicates('tag')

u_books = books.drop_duplicates('url')
# u_books.to_sql("book")
u_books.to_csv('babelio_books_u.csv', index=False)  

# from sqlalchemy import create_engine
# u_books.to_sql('book', engine)
# tags.to_sql("tag", engine)

# write the data to a sqlite table
# users.to_sql('users', conn, if_exists='append', index = False)
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         book_id = row["url"].split("/")[-1]
#         insert_q = f"INSERT INTO tag VALUES({row['tag']},{row['tag']})"
#         cur.execute(insert_q)
#         con.commit()
        
        # cur.execute(f"""
        # INSERT IGNORE INTO book VALUES
        #     ({book_id}, {row["title"]}, {row["url"]}, [{row["tag"]}]),    
        # """)
        # con.commit()
        
