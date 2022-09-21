import requests, json, os, time
from bs4 import BeautifulSoup, SoupStrainer
import undetected_chromedriver as uc
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import pandas as pd
from pathlib import Path

def newSession(): return requests.Session()
session = newSession()
def initHeaders(): return {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51'}
headers = initHeaders()
BASE_DIR = Path(__file__).resolve().parent

# title, img, imgClass, link, left, center, right
class Container:
    def __init__(self, title, img='', imgClass='', link='', left='', center='', right='', type='Info'):
        self.title = title.strip()
        self.img = {'link':img, 'class':imgClass}
        self.link = link
        self.left = left.strip()
        self.center = center.strip()
        self.right = right.strip()
        self.type = type
# title, link, img, imgClass, type
class Elements:
    def __init__(self, title, link='', img='', imgClass='', type='Video'):
        self.title = title.strip()
        self.link = link
        self.img = {'link':img.strip(), 'class':imgClass} if img != '' else ''
        self.type = type
# title, img, imgClass, genres, desc, elements, sections, infos
class Info:
    def __init__(self, title, img='', imgClass='', genres=[], desc='', elements=[], sections=[], infos=[]):
        self.title = title.strip()
        self.img = {'link':img.strip(), 'class':imgClass} if img != '' else ''
        self.genres = genres
        self.desc = desc.strip().replace('.', '. ').replace('  ', ' ')
        self.elements = elements
        self.sections = sections
        self.infos = infos
# name, url
class Blank:
    def __init__(self, name='', link=''):
        if name == '' and link != '': name = link.split('/')[2].split('.')[-2]
        self.name = str(name).strip().title()
        self.link = link


class Soup(object):
    def Soup(url, headers=headers, cookies='', soupStrainer=SoupStrainer('body'), method='get', data={}, proxies={}):
        if method == 'get': response = session.get(url=url, headers=headers, cookies=cookies, proxies=proxies)
        elif method == 'post': response = session.post(url=url, headers=headers, data=data, proxies=proxies)
        print(response)
        if response.ok: return BeautifulSoup(response.content, 'lxml', parse_only=soupStrainer)
        else: return False

    def Soup_cloudflare(url, headers=headers, soupStrainer=SoupStrainer('body'), method='get', data={}, proxies={}, reCaptcha=False):
        try: soup = Soup.Soup(url, headers, soupStrainer, method, data, proxies)
        except: soup = False
        if not soup or reCaptcha != False:
            options = uc.ChromeOptions()
            options.add_argument('--user-data-dir=C:/Users/paula/AppData/Local/Google/Chrome/User Data/')
            if proxies != {}: options.add_argument('--proxy-server='+proxies['https'])

            driver = uc.Chrome(use_subprocess=True, options=options, executable_path='./chromedriver.exe')
            driver.get(url)
            time.sleep(1)
            if not reCaptcha:
                driver.minimize_window()
                x=0
                while 'cloudflare' in str(driver.page_source.encode('utf-8')):
                    time.sleep(0.5)
                    x+=1
                    if x > 20: return False
            else:
                while 'class="g-recaptcha"' in str(driver.page_source.encode('utf-8')) or  'cloudflare' in str(driver.page_source.encode('utf-8')): time.sleep(1)
            time.sleep(0.5)
            soup = BeautifulSoup(driver.page_source.encode('utf-8'), 'lxml', parse_only=soupStrainer)
            driver.quit()
        return soup

    def Soup_javascript(urls, soupStrainer=SoupStrainer('body'), proxies={}, headless=True, sleep=1, element='', elements=[], needClick=False):
        options = uc.ChromeOptions()
        if headless: options.add_argument('--headless')
        if proxies != {}: options.add_argument('--proxy-server='+proxies['https'])
        caps = DesiredCapabilities().CHROME
        caps['pageLoadStrategy'] = 'none'
        driver = uc.Chrome(use_subprocess=True, desired_capabilities=caps, options=options, executable_path='./chromedriver.exe')

        soups = []
        for url in urls:
            driver.get(url)
            if not needClick:
                if not headless: driver.minimize_window()
                x = 0
                while element not in str(driver.page_source.encode('utf-8')) and x <20:
                    time.sleep(0.5)
                    x+=1
            else:
                for element in elements:
                    time.sleep(sleep)
                    for el in driver.find_elements(By.CSS_SELECTOR, element):
                        try: el.click()
                        except: pass
            soups.append(BeautifulSoup(driver.page_source.encode('utf-8'), 'lxml', parse_only=soupStrainer))
        driver.quit()
        return soups


class Proxies(object):
    def __init__(self, url='https://httpbin.org/ip', nbIp=1):
        self.ipPath = os.path.join(BASE_DIR, 'static/json/ip.json')
        self.url = url
        self.nbIp = nbIp
    
    def proxies(self):
        try:
            proxies = json.load(open(self.ipPath, 'r', encoding='utf-8'))[-1]
            session.get(url=self.url, headers=headers, proxies=proxies, timeout=2)
        except: proxies = Proxies.freeProxy(self)[-1]
        return proxies

    def freeProxy(self):
        goodProx = []
        for site in ['http://proxydb.net/?protocol=https', 'https://www.sslproxies.org/']:
            try: response = session.get(url=site, headers=headers)
            except: continue
            if response.ok:
                proxyList = pd.read_html(response.text)[0]
                if 'proxydb.net' in site: proxyList['url'] = 'http://'+proxyList['Proxy']
                else: 
                    proxyList = proxyList[proxyList['Https'] == 'yes']
                    proxyList = proxyList[proxyList['Country'] != 'France']
                    proxyList['url'] = 'http://'+proxyList['IP Address']+':'+proxyList['Port'].astype('str')
                for url in proxyList['url']:
                    print(f'try {url}', end='\r')
                    proxies = {'http':url, 'https':url}
                    try:
                        response = session.get(url=self.url, headers=headers, proxies=proxies, timeout=2)
                        goodProx.append(proxies)
                        print(url)
                        if len(goodProx) >= self.nbIp:
                            print(goodProx)
                            open(self.ipPath, 'w+', encoding='utf-8').write(json.dumps(goodProx))
                            return goodProx
                    except: pass
        print(goodProx)
        open(self.ipPath, 'w+', encoding='utf-8').write(json.dumps(goodProx))
        return goodProx