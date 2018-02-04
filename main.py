#coding=utf8
import requests
import bs4
import telebot
from googletrans import Translator
from time import sleep
import os

data = []
translator = Translator()

TOKEN = os.environ['TELEGRAM_TOKEN']
BITLY_TOKEN = os.environ['BITLY_TOKEN']
# TOKEN = config.TOKEN

bot = telebot.TeleBot(TOKEN)
# BITLY_TOKEN = config.BITLY_TOKEN
URL_FOR_SHORTEN = 'https://api-ssl.bitly.com/v3/shorten?access_token='+BITLY_TOKEN+'&longUrl='

def main():

    if len(data)>100:
        del data[:50]

    URL = 'http://neurosciencenews.com/neuroscience-topics/neuroscience'
    r = requests.get(URL)

    soup = bs4.BeautifulSoup(r.content, 'html')

    blocks = soup.find_all(attrs={'class':'cb-blog-style-a'})

    for i in blocks:
        titleBlock = i.find(attrs={'class':'cb-post-title'}).a
        title = translator.translate(titleBlock.text, src='en', dest='ru').text

        if title in data:
            continue
        else:
            data.append(title)
            link = titleBlock['href']
            shortLink = requests.get(URL_FOR_SHORTEN+link+'&format=json').json()['data']['url']

            imgUrl = i.find(attrs={'class':'cb-img-fw'}).a.find('img')['data-lazy-src']
            imgUrl = requests.get(URL_FOR_SHORTEN+imgUrl+'&format=json').json()['data']['url']

            description = i.find(attrs={'class':'cb-excerpt'}).text[:-14]
            description = translator.translate(description, src='en', dest='ru').text

            text = '<b>'+title+'</b>' + '\n\n' + description + '\n\n'+ '<b>Фото: </b>'+imgUrl + '\n'+ '<b>Оригинал: </b> ' +shortLink
            bot.send_message(chat_id='@neuro_news', text=text, parse_mode='HTML')

    bot.send_message(chat_id='@neuro_news', text='Number of list items {}'.format(len(data)))
    sleep(1000)

if __name__=='__main__':
    main()