#coding=utf8
import requests
import bs4
import telebot
from googletrans import Translator
from time import sleep
from urllib import parse
import psycopg2
import os

translator = Translator()

TOKEN = os.environ['TELEGRAM_TOKEN']
BITLY_TOKEN = os.environ['BITLY_TOKEN']
DATABASE_URL = os.environ['DATABASE_URL']

bot = telebot.TeleBot(TOKEN)
URL_FOR_SHORTEN = 'https://api-ssl.bitly.com/v3/shorten?access_token='+BITLY_TOKEN+'&longUrl='

def connect_database():
    parse.uses_netloc.append('postgres')
    url = parse.urlparse(DATABASE_URL)

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn

#
# def create_table():
#
#     conn = connect_database()
#     cur = conn.cursor()
#     command = (
#         '''
#         CREATE TABLE titles (
#             title_name text
#         )
#         ''')
#
#     cur.execute(command)
#     conn.commit()

def insert_inTable(text):
    conn = connect_database()
    cur = conn.cursor()

    sql = """INSERT INTO titles (title_name)
             VALUES (%s)"""
    cur.execute(sql, (text,))
    conn.commit()
    cur.close()
    conn.close()

def read_table():
    title_data = []
    conn = connect_database()
    cur = conn.cursor()

    sql = """SELECT * FROM titles"""
    cur.execute(sql)
    dataFetched = cur.fetchall()    ## data - list of tuples
    for tuple in dataFetched:
        title_data.append(tuple[0])

    print(title_data)
    return title_data




def main():
    title_data = read_table()

    URL = 'http://neurosciencenews.com/neuroscience-topics/neuroscience'
    r = requests.get(URL)

    soup = bs4.BeautifulSoup(r.content, 'html')

    blocks = soup.find_all(attrs={'class':'cb-blog-style-a'})

    for i in blocks:
        titleBlock = i.find(attrs={'class':'cb-post-title'}).a
        title = translator.translate(titleBlock.text, src='en', dest='ru').text

        if title in title_data:
            continue
        else:
            insert_inTable(title)
            link = titleBlock['href']
            shortLink = requests.get(URL_FOR_SHORTEN+link+'&format=json').json()['data']['url']

            imgUrl = i.find(attrs={'class':'cb-img-fw'}).a.find('img')['data-lazy-src']
            imgUrl = requests.get(URL_FOR_SHORTEN+imgUrl+'&format=json').json()['data']['url']

            description = i.find(attrs={'class':'cb-excerpt'}).text[:-14]
            description = translator.translate(description, src='en', dest='ru').text

            text = '<b>'+title+'</b>' + '\n\n' + description + '\n\n'+ '<b>Фото: </b>'+imgUrl + '\n'+ '<b>Оригинал: </b> ' +shortLink
            bot.send_message(chat_id='@neuro_news', text=text, parse_mode='HTML')

    sleep(1000)

if __name__=='__main__':
    main()