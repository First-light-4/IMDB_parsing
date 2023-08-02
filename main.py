import multiprocessing
import json
import os
import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from  selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import user_agent


def cookies():
    login = 'savchenkovalsav@gmail.com'
    password = '17Hokkeey03'
    return login, password

class BS4:

    def __init__(self, url):
        self.url = url

    def get_products(self, name):
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Mobile Safari/537.36"
        }

        req = requests.get(self.url, headers=headers)
        src = req.text
        with open(f"{name}.html", "w", encoding="utf-8") as file:
            file.write(src)

        with open(f"{name}.html", "r", encoding="utf-8") as file:
            src = file.read()

        return src

class Selenium:

    def __init__(self, url):
        self.url = url
        self.casting_directors_href = {}

    # подключение к драйверу
    def get_data_with_selenium(self, headless=False):
        # создаем обьект опций
        options = webdriver.ChromeOptions()

        # useragent для анонимности
        # options.add_argument(f"user-agent={user_agent().ie}")
        options.add_argument(
            f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

        # disable webdriver
        options.add_argument("disable-blink-features=AutomationControlled")

        # without window
        # options.headless = headless
        self.driver = webdriver.Chrome(executable_path=r"chromedriver.exe"
                                  , options=options
                                  )

        # url = driver.command_executor._url
        # session_id = driver.session_id
        #
        # driver = webdriver.Remote(command_executor=url, desired_capabilities={})
        # driver.close()
        # driver.session_id = session_id

        self.driver.get(url=self.url)
        # time.sleep(30)
        return self.driver

    # открытие IMDB
    def open_IMDB(self):

        # попытка входа
        log_in = self.driver.find_element(By.ID, 'ap_email')
        password = self.driver.find_element(By.ID, 'ap_password')
        log_in.click()
        time.sleep(3)
        log_in.send_keys(cookies()[0])
        time.sleep(3)
        password.click()
        time.sleep(3)
        password.send_keys(cookies()[1])
        time.sleep(3)
        password.send_keys(Keys.ENTER)
        time.sleep(3)

        # при отриуательном варианте переход ещё раз
        self.driver.get('https://pro.imdb.com/login/ap?u=/login/lwa&imdbPageAction=signUp&rf=cons_nb_hm&ref_=cons_nb_hm')

        # вход через amazon
        el = self.driver.find_element(By.ID, 'signup_with_amazon')
        el.click()
        contin = self.driver.find_element(By.ID, "ap-oaconsent-agree-button")
        contin.click()
        time.sleep(3)
        #
        #
        # driver.get('https://pro.imdb.com/discover/people?profession=director&ref_=dsc_pe_nv_ppl_dir')
        # print(driver.find_element(By.ID, 'maincontent').text)
        return self.driver

    # получение всех ссылок и имен директоров
    def save_all_hrefs(self, url = 'https://pro.imdb.com/discover/people?profession=casting_director&ref_=hm_nv_ppl_dir&minNumOfReleasedCredits=1&creditBeginYear=2018&sortOrder=RELEVANCE&pageNumber='):
        for i in range(1, 4834):
            try:
                self.driver.get(
                    f'{url}{i}')
                time.sleep(3)
                all_casting_directors = self.driver.find_element(By.ID, 'search_result_selections_form')
                # print(all_casting_directors.text)
                for direct in all_casting_directors.find_elements(By.TAG_NAME, 'table'):
                    try:
                        name = direct.text.split('\n')[0]
                        href = str(direct.find_element(By.TAG_NAME, 'a').get_attribute('href'))
                        self.casting_directors_href[name] = href
                    except Exception:
                        print('not found href')
            except Exception:
                print(f'href not working:\nhttps://pro.imdb.com/discover/people?profession=casting_director&ref_=hm_nv_ppl_dir&minNumOfReleasedCredits=1&creditBeginYear=2018&sortOrder=RELEVANCE&pageNumber={i}')
        return self.casting_directors_href

    def open_info(self, filename):
        with open(f"{filename}.json") as file:
            self.lines = json.load(file)
        return self.lines

    def open_everyone(self, href):
        dict_info = {}


        # for name, href in self.lines.items():
        try:
            self.driver.get(href)
            contact = self.driver.find_element(By.ID, 'contacts')
            if 'Direct Contact' in contact.text and '@' in contact.find_element(By.TAG_NAME, 'ul').text:
                print(' Director')
                name = contact.find_element(By.TAG_NAME, 'ul').text
                print(name)
                info = (contact.find_element(By.TAG_NAME, 'ul').find_element(By.TAG_NAME, 'a').get_attribute('href'))
                print(info)
                print('films')
                all_films = self.driver.find_element(By.ID, 'const_tabs').find_elements(By.CLASS_NAME,'a-fixed-left-grid-inner')[0:4]
                films = []
                for film in all_films:
                    films.append(film.text)
                dict_info[name] = {"info": info, "films": films}
                time.sleep(3)
        except Exception as e:
            print(e)
            print("can't to connect to director")
            # save_all_href(dict_info, "casting_director")
            # break
        return dict_info
        # save_all_href(dict_info, "casting_director")


def save_all_href(data, name):
    with open(f'testing.json', 'w') as f:
        json.dump(data, f, indent=2)
def login_in_IMDB(filename):
    casting_directors = {}

    # создание основного driver
    main_sait = Selenium(
        'https://na.account.amazon.com/ap/signin?_encoding=UTF8&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.pape.max_auth_age=0&ie=UTF8&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=amzn_lwa_na&marketPlaceId=ATVPDKIKX0DER&arb=22117d24-564b-4980-90ca-2615fa92bf55&language=en_US&openid.return_to=https%3A%2F%2Fna.account.amazon.com%2Fap%2Foa%3FmarketPlaceId%3DATVPDKIKX0DER%26arb%3D22117d24-564b-4980-90ca-2615fa92bf55%26language%3Den_US&enableGlobalAccountCreation=1&metricIdentifier=amzn1.application.eb539eb1b9fb4de2953354ec9ed2e379&signedMetricIdentifier=fLsotU64%2FnKAtrbZ2LjdFmdwR3SEUemHOZ5T2deI500%3D')
    main_sait.get_data_with_selenium(headless=False)
    driver = main_sait.open_IMDB()
    print(driver)

    i = main_sait.open_info(filename)
    print(list(i.values())[:5])
    for href in list(i.values())[15:25]:
        print(main_sait.open_everyone(href))

    # casting_directors_href = main_sait.save_all_hrefs()
    # print(casting_directors_href)
    # save_all_href(casting_directors_href, 'href_director')

    time.sleep(6000)
    # save_info(casting_directors)

class work_with_information:

    def __init__(self, name_file):
        self.name_file = name_file

    def open_file(self):
        with open(self.name_file) as file:
            self.lines = json.load(file)
        return self.lines

def test(x):
    print(x)
    return x*2

def save_test(response):
    print("задание завершенно")
    print(response)

if __name__ == '__main__':
    # main_sait = Selenium(
    #     'https://na.account.amazon.com/ap/signin?_encoding=UTF8&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.pape.max_auth_age=0&ie=UTF8&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=amzn_lwa_na&marketPlaceId=ATVPDKIKX0DER&arb=22117d24-564b-4980-90ca-2615fa92bf55&language=en_US&openid.return_to=https%3A%2F%2Fna.account.amazon.com%2Fap%2Foa%3FmarketPlaceId%3DATVPDKIKX0DER%26arb%3D22117d24-564b-4980-90ca-2615fa92bf55%26language%3Den_US&enableGlobalAccountCreation=1&metricIdentifier=amzn1.application.eb539eb1b9fb4de2953354ec9ed2e379&signedMetricIdentifier=fLsotU64%2FnKAtrbZ2LjdFmdwR3SEUemHOZ5T2deI500%3D')
    # main_sait.get_data_with_selenium(headless=False)
    # driver = main_sait.open_IMDB()
    #
    # casting_directors_href = main_sait.save_all_hrefs(url='https://pro.imdb.com/discover/people?profession=director&ref_=hm_nv_ppl_dir&minNumOfReleasedCredits=1&creditBeginYear=2018&sortOrder=RELEVANCE&pageNumber=')
    # print(casting_directors_href)
    # save_all_href(casting_directors_href, 'href_director')

    # мультипроцессинг
    # info = work_with_information('href_director.json')
    # with multiprocessing.Pool(multiprocessing.cpu_count() * 3) as p:
    #     # p.map_async(test, list(range(len(info.open_file().keys()))[:50]), callback=save_test)
    #     l = list('a'*i for i in range(10))
    #     p.map_async(login_in_IMDB('href_director'), list(range(len(info.open_file().keys()))[:6]), callback=save_all_href)
    #     p.close()
    #     p.join()

    login_in_IMDB('href_director')

    # driver.open_IMDB()
    # for name, info in data.open_file().items():
    #     print(name, info)

