import random

import requests
from bs4 import BeautifulSoup as bs


HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 '
                  '(Macintosh; Intel Mac OS X 10_11_5) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.102 Safari/537.36'}


def get_random_title():
    """Получает HTML документ с указанного url-a и возвращает поля [h1, class=categories-list, url страницы]."""
    url = 'https://yummyanime.club/random'
    r = requests.get(url, allow_redirects=True, headers=HTTP_HEADERS)
    genre_list = []
    soup = bs(r.text, "html.parser")
    data = str(soup.find('h1').get_text()).replace('\t', ''). \
        replace('\n', '')[20:]
    for categories in soup.find_all(class_='categories-list'):
        for li in categories.find_all('li'):
            genre_list.append(li.find('a').get_text())
        break
    li_list = ', '.join(genre_list)
    return f'Title: {data} \nTypes: {li_list} \nSource: {r.url}'


def get_random_GIF(url):
    """Получает HTML документ с переданного url-a и возвращает адрес случайного img тега."""
    r = requests.get(url)
    soup = bs(r.text, "html.parser")
    gif_list = soup.findAll("img")[2:]
    src_gif_list = [gif["src"] for gif in gif_list]
    return random.choice(src_gif_list)
