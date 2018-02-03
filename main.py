#coding=utf8
import requests
import bs4
import telebot
import config
from googletrans import Translator
from time import sleep

data = []

def main():

    if len(data)>100:
        del data[:50]

    translator = Translator()

    TOKEN = config.TOKEN
    bot = telebot.TeleBot(TOKEN)
    BITLY_TOKEN = config.BITLY_TOKEN
    URL_FOR_SHORTEN = 'https://api-ssl.bitly.com/v3/shorten?access_token='+BITLY_TOKEN+'&longUrl='

    # data_path = r'data.txt'
    # with open(data_path, 'r') as f:
    #     data = f.read().split('\n')

    URL = 'http://neurosciencenews.com/neuroscience-topics/neuroscience'
    r = requests.get(URL)

    soup = bs4.BeautifulSoup(r.content, 'lxml')

    blocks = soup.find_all(attrs={'class':'cb-blog-style-a'})

    for i in blocks:
        titleBlock = i.find(attrs={'class':'cb-post-title'}).a
        title = translator.translate(titleBlock.text, src='en', dest='ru').text

        if title in data:
            continue
        else:
            data.append(title)
            link = titleBlock['href']
            # shortLink = requests.get(URL_FOR_SHORTEN+link+'&format=json').json()['data']['url']

            imgUrl = i.find(attrs={'class':'cb-img-fw'}).a.find('img')['data-lazy-src']
            imgUrl = requests.get(URL_FOR_SHORTEN+imgUrl+'&format=json').json()['data']['url']

            description = i.find(attrs={'class':'cb-excerpt'}).text[:-14]
            description = translator.translate(description, src='en', dest='ru').text

            text = '<b>'+title+'</b>' + '\n\n' + description + '\n\n'+'<b>Фото:</b>'+imgUrl
            bot.send_message(chat_id='@neuro_news', text=text, parse_mode='HTML')

    sleep(60000.0)

if __name__=='__main__':
    main()