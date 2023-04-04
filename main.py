import datetime

from aiogram.utils.markdown import hbold
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from sql import DataBase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

db = DataBase('data\statistica.db')

options = webdriver.ChromeOptions()
options.headless = False

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(options=options, service=service)

driver.set_page_load_timeout(60000)


def get_html(articul):
    try:
        request = requests.get(
            f'https://card.wb.ru/cards/detail?curr=rub&dest=-1257786&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,22,31,71,114,111&spp=0&nm={articul}')
        request = request.json()
        products = request['data']['products']
        a = None
        b = None
        for item in products:
            if item['id'] == articul:
                imtId = item['root']
                size = item['sizes'][0]['optionId']
                a = imtId
                b = size
        driver.maximize_window()
        driver.get(f'https://www.wildberries.ru/catalog/{articul}/feedbacks?imtId={a}&size={b}')
        time.sleep(5)
        while True:
            # Проматываем страницу вниз
            now_1 = datetime.datetime.now()
            now_1 -= datetime.timedelta(days=5)

            try:
                target = driver.find_element(By.XPATH, f"//span[contains(text(),'{now_1.day} ')]")
                break
            except Exception as e:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(0.5)
        html = driver.page_source
        return html


    except Exception as ex:
        print(ex)


def five_days(html):
    now = datetime.datetime.now()
    list = []
    now_1 = datetime.datetime.now()
    now_1 -= datetime.timedelta(days=5)
    soup = BeautifulSoup(html, 'lxml')
    li = soup.find_all(class_='feedback__info')
    for item in li:

        time = item.find(class_='feedback__date hide-mobile').get('content')
        time = datetime.datetime.fromisoformat(time)
        time += datetime.timedelta(hours=3)
        if time.date() >now_1.date() :
            for i in range(1,6):
                star_5 = item.find(class_=f'feedback__rating stars-line star{i}')
                if star_5 != None:
                    data =star_5.get('class')[-1].replace('star','')
                    list.append(data)
    five = list.count('5')
    four = list.count('4')
    three = list.count('3')
    two = list.count('2')
    one = list.count('1')
    five_d = round((5*five+4*four+3*three+2*two+1*one)/(five+four+three+two+one),2)
    otz = five+four+three+two+one
    result = [five_d,otz]
    return result

def count(soup):
    count = int(soup.find(class_='rating-product__review hide-mobile').text.replace('На основе ', '').split(' ')[0].replace('\xa0', ''))
    return count


def stars5(soup):
    st = soup.find_all(class_='feedback-percent__count')
    stars_r = []
    for item in st:
        stars_r.append(int(item.text.replace('%', '')))
    return stars_r


async def main(articul, name):
    try:
        REIT = float(db.get_reit()[0][0])
        html = get_html(articul)
        result = five_days(html)
        reit_za_5 = result[0]
        otz_za_5 = result[-1]
        now = datetime.datetime.now().day
        soup = BeautifulSoup(html, 'lxml')
        counts = count(soup)
        stars_5 = stars5(soup)
        raiting = round((5 * stars_5[0] + 4 * stars_5[1] + 3 * stars_5[2] + 2 * stars_5[3] + 1 * stars_5[4]) / 100, 2)
        stat = db.get_stat(articul)
        if stat == []:
            iz_reit = 'нет данных'
            iz_kolvo = 'нет данных'
            iz_reit_5 = 0
            iz_kolvo_5 = 0
            if raiting < REIT and reit_za_5 < REIT:
                card = f'{hbold(name)}  {hbold(raiting)}({iz_reit}) {counts}({iz_kolvo})\n' \
                       f' Рейтинг за 5 дней: {hbold(reit_za_5)}({iz_reit_5}) - {otz_za_5}({iz_kolvo_5})отзывов'
                db.add_stat(articul, raiting, counts,reit_za_5,otz_za_5)
                return card
            elif raiting < REIT:
                card = f'{hbold(name)}  {hbold(raiting)}({iz_reit}) {counts}({iz_kolvo})\n' \
                       f' Рейтинг за 5 дней: {reit_za_5}({iz_reit_5}) - {otz_za_5}({iz_kolvo_5})отзывов'
                db.add_stat(articul, raiting, counts, reit_za_5, otz_za_5)
                return card
            elif reit_za_5 < REIT:
                card = f'{hbold(name)}  {raiting}({iz_reit}) {counts}({iz_kolvo})\n' \
                       f' Рейтинг за 5 дней: {hbold(reit_za_5)}({iz_reit_5}) - {otz_za_5}({iz_kolvo_5})отзывов'
                db.add_stat(articul, raiting, counts, reit_za_5, otz_za_5)
                return card
            else:
                card = f' {name}  {raiting}({iz_reit}) {counts}({iz_kolvo})\n' \
                       f' Рейтинг за 5 дней: {reit_za_5}({iz_reit_5}) - {otz_za_5}({iz_kolvo_5})отзывов'
                db.add_stat(articul, raiting, counts,reit_za_5,otz_za_5)

                return card
        else:
            iz_reit = round(raiting - float(stat[0][0]), 2)
            iz_kolvo = counts - stat[0][1]
            iz_reit_5 = round(reit_za_5 - float(stat[0][2]),2)
            iz_kolvo_5 =otz_za_5 - stat[0][3]
            if raiting < REIT and reit_za_5 < REIT :
                card = f'{hbold(name)}  {hbold(raiting)}({iz_reit}) {counts}({iz_kolvo})\n' \
                       f' Рейтинг за 5 дней: {hbold(reit_za_5)}({iz_reit_5}) - {otz_za_5}({iz_kolvo_5})отзывов'
                db.add_stat(articul, raiting, counts, reit_za_5, otz_za_5)
                return card
            elif raiting < REIT:
                card = f'{hbold(name)}  {hbold(raiting)}({iz_reit}) {counts}({iz_kolvo})\n' \
                       f' Рейтинг за 5 дней: {reit_za_5}({iz_reit_5}) - {otz_za_5}({iz_kolvo_5})отзывов'
                db.add_stat(articul, raiting, counts, reit_za_5, otz_za_5)
                return card
            elif reit_za_5 < REIT :
                card = f'{hbold(name)}  {raiting}({iz_reit}) {counts}({iz_kolvo})\n' \
                       f' Рейтинг за 5 дней: {hbold(reit_za_5)}({iz_reit_5}) - {otz_za_5}({iz_kolvo_5})отзывов'
                db.add_stat(articul, raiting, counts, reit_za_5, otz_za_5)
                return card
            else:
                card = f' {name}  {raiting}({iz_reit}) {counts}({iz_kolvo})\n' \
                       f' Рейтинг за 5 дней: {reit_za_5}({iz_reit_5}) - {otz_za_5}({iz_kolvo_5})отзывов'
                db.add_stat(articul, raiting, counts,reit_za_5,otz_za_5)

                return card

    except Exception as e:
        print(e)




if __name__ == '__main__':
   main('17345830 ',',kffd')