import random
from bs4 import SoupStrainer
from urllib.parse import quote, unquote
from tools import *
from django.shortcuts import render

# note: download book
session = newSession()
headers = initHeaders()
scrapSites = {
    'Vostfree': {'baseUrl': 'https://vostfree.cx', 'img': 'https://vostfree.cx/templates/Animix/images/logo.png', 'style': 'margin-left: 15px'},
    'Vostanimes': {'baseUrl': 'https://vostanimey.com', 'img': 'https://vostanimey.com/wp-content/uploads/2022/09/cooltext418474422348093.png'},
    'Adkami': {'baseUrl': 'https://www.adkami.com', 'img': 'https://i.postimg.cc/4yX1tdVM/ADKami-Logo.png'},
    #'Voiranime': {'baseUrl': 'https://voiranime.com', 'img': 'https://1.bp.blogspot.com/-tnOKXWZFR2E/YCZWXHBmzjI/AAAAAAAAACQ/5u3_g7cC6D40AQxnX39AK9TkXo0VVejogCLcBGAsYHQ/s320/Untitled.png'},
    'IAnimes': {'baseUrl': 'https://www.ianimes.org', 'img': 'https://www.ianimes.org/img/i-anime.png', 'style':'width:248px'},

    'Wiflix': {'baseUrl': 'https://wiflix.zone', 'img': 'https://wiflix.zone/templates/wiflixnew/images/logo.png'},
    'FrenchStream': {'baseUrl': 'https://wwv.french-stream.re', 'img': 'https://i.postimg.cc/gkyWt2kQ/fstream-logo.png'},

    'Ninemanga': {'baseUrl': 'https://fr.ninemanga.com', 'img': 'https://www.ninemanga.com/files/img/ninemanga.png'},
    'ScanMangas': {'baseUrl': 'https://scansmangas.ws', 'img': 'https://scansmangas.ws/wp-content/uploads/2019/10/logo.png'},
    #'MangasOrigines': {'baseUrl': 'https://mangas-origines.fr', 'img': 'https://mangas-origines.fr/wp-content/uploads/2017/10/Mangas_logo.png', 'style': 'margin-left: -10px'},
}
# https://manga-scantrad.net/
# scrap download: zlib
   
# ScrapSites
class Vostfree:
    def __init__(self):
        self.baseUrl = scrapSites['Vostfree']['baseUrl']
        self.context = {}
        self.soupStrainer = SoupStrainer(id='dle-content')

    def Main(self):
        for version in ['', '-vf']:
            url = f'{self.baseUrl}/last-episode{version}.html'
            if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
                sectionName = soup.find(class_='active').text.strip()
                self.context[sectionName] = {'url':url, 'container':[]}

                for anime in soup.find_all(class_='last-episode'):
                    title = anime.find(class_='title').text
                    img = self.baseUrl + anime.find('img')['src']
                    link = anime.find('a')['href'].replace(self.baseUrl, '')

                    infos = anime.find(class_='alt').find_all('b')
                    episode = f'Episode {infos[1].text}'
                    date = anime.find(class_='additional').find_all('li')[1].text.replace('\xa0', ' ')
                    season = f'Saison {infos[0].text}'
                    
                    self.context[sectionName]['container'].append(Container( title, img, 'poster', link, episode, date, season ))
        return self.context

    def Search(self, search, page):
        url = f'{self.baseUrl}/index.php?story={search}&do=search&search_start={page}&subaction=search&submit=Submit'
        self.context = {'search': search, 'url': url, 'container': []}

        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            for anime in soup.find_all(class_='search-result'):
                title = anime.find(class_='title').text
                img = self.baseUrl + anime.find('img')['src']
                link = anime.find('a')['href'].replace(self.baseUrl, '')

                alt = anime.find(class_='alt')
                info1 = alt.find_all('span')
                info2 = alt.find_all('b')
                episode = f'{info1[1].text.strip()} {info2[1].text.strip()}'
                version = anime.find(class_='quality').text
                season = f'{info1[0].text.strip()} {info2[0].text.strip()}'
                    
                self.context['container'].append(Container( title, img, 'poster', link, episode, version, season ))
        return self.context

    def Info(self, url):
        if soup := Soup.Soup(url=self.baseUrl+url, soupStrainer=self.soupStrainer):
            title = soup.find(class_='slide-middle').find('h1').text
            img = self.baseUrl + soup.find(class_='slide-poster').find('img')['src']
            
            genres = [Blank(
                genre.text, genre['href'].replace(self.baseUrl, '')
            ) for genre in soup.find(class_='right').find_all('a')]
            desc = soup.find(class_='slide-desc').text

            episodes = [{'name':'Episodes', 'elements': [Elements(
                option.text, quote(f"{url}&nb={option['value'].split('_')[1]}")
            ) for option in soup.find(class_='new_player_selector').find_all('option')]}]

            try: date = soup.find(class_='slide-info').find('a').text
            except: date = ''
            time = soup.find(class_='slide-info').find_all('b')[-1].text.strip()
            infos = [date, time, f'Episode {len(episodes[0]["elements"])}']

            self.context = Info( title, img, 'poster', genres, desc, episodes, infos )
        return self.context

    def Video(self, url):
        container = []
        url = unquote(url).split('&nb=')
        if soup := Soup.Soup(url=self.baseUrl+url[0], soupStrainer=self.soupStrainer):
            newPlayers = {
                'new_player_myvi': 'https://myvi.ru/player/embed/html/{}',
                'new_player_gtv': 'https://iframedream.com/embed/{}.html',
                'new_player_mp4': 'https://www.mp4upload.com/embed-{}.html',
                'new_player_uqload': 'https://uqload.com/embed-{}.html',
                'new_player_vidfast': 'http://vosmanga.tk/watch/{}',
                'new_player_verystream': 'https://verystream.com/e/{}',
                'new_player_rapids': 'https://rapidstream.co/embed-{}.html',
                'new_player_cloudvideo': 'https://cloudvideo.tv/embed-{}.html',
                'new_player_mytv': 'https://www.myvi.xyz/embed/{}',
                'new_player_uptostream': 'https://uptostream.com/iframe/{}',
                'new_player_fembed': 'https://www.fembed.com/v/{}.html',
                'new_player_tune': 'https://tune.pk/player/embed_player.php?vid={}',
                'new_player_sibnet': 'https://video.sibnet.ru/shell.php?videoid={}',
                'new_player_netu': 'https://waaw.tv/watch_video.php?v={}',
                'new_player_rutube': 'https://rutube.ru/play/embed/{}',
                'new_player_ok': 'https://www.ok.ru/videoembed/{}',
                'new_player_google': 'https://drive.google.com/open?id={}',
                'new_player_mail': 'https://videoapi.my.mail.ru/videos/embed/mail/{}',
                'new_player_mail2': 'https://my.mail.ru/video/embed/{}'
            }

            for player in soup.find(id=f'buttons_{url[1]}').find_all('div'):
                id = soup.find(id=f'content_{player["id"]}').text

                try: link = newPlayers[player['class'][0]].format(id)
                except: link = id
                container.append(Blank(player.text, link))
        return container

    def Genre(self, genreUrl):
        url = f'{self.baseUrl}/{genreUrl}'
        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            genreName = url.split('/')[-2].replace('-', ' ').title()
            self.context[genreName] = {'url':url, 'container':[]}
            
            for anime in soup.find_all(class_='movie-poster'):
                title = anime.find(class_='title').text
                img = self.baseUrl + anime.find('img')['src']
                link = anime.find('a')['href'].replace(self.baseUrl, '')

                info = anime.find(class_='alt').find_all('b')
                episode = f'Episode {info[1].text}'
                version = anime.find(class_='quality').text
                season = f'Saison {info[0].text}'
                
                self.context[genreName]['container'].append(Container( title, img, 'poster', link, episode, version, season ))
        return self.context


class Vostanimes:
    def __init__(self):
        self.baseUrl = scrapSites['Vostanimes']['baseUrl']
        self.context = {}
        self.soupStrainer = SoupStrainer('main')

    def Main(self):
        if soup := Soup.Soup(url=self.baseUrl, soupStrainer=self.soupStrainer):
            for section in soup.find_all('section'):
                try: sectionName = section.find('h1').text.strip()
                except: sectionName = section.find(class_='Title').text.strip()
                if 'Saison' in sectionName.title(): continue
                self.context[sectionName] = {'url': f'{self.baseUrl}/{section.find("a")["href"]}', 'container':[]}
                
                for anime in section.find_all('article'):
                    title = anime.find(class_='Title').text
                    img = anime.find('img')['data-src']
                    imgClass = 'poster'
                    link = anime.find('a')['href'].replace(self.baseUrl, '')
                    type = 'Info'

                    try: left = anime.find(class_='Time').text
                    except: left = ''
                    try: center = anime.find('figcaption').text
                    except: center = ''
                    try: right = anime.find(class_='Year').text
                    except: right = ''

                    if 'pisodes' in sectionName:
                        imgClass = 'vertical'
                        info = center.split(' ep')
                        left = (f'ep{info[1]}').title()
                        right = info[0].title()
                        type = 'Video'

                    self.context[sectionName]['container'].append(Container( title, img, imgClass, link, left, center, right, type ))
        return self.context

    def Search(self, search, page):
        url = f'{self.baseUrl}/page/{page}/?s={search}'
        self.context = {'search': search, 'url': url, 'container': []}

        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            for anime in soup.find_all('article'):
                title = anime.find(class_='Title').text
                img = anime.find('img')['src']
                link = anime.find('a')['href'].replace(self.baseUrl, '')
                
                try: time = anime.find(class_='Time').text
                except: time = ''
                try: date = anime.find(class_='Year').text
                except: date = ''
                    
                self.context['container'].append(Container( title, img, 'poster', link, time, '', date ))
        return self.context

    def Info(self, url):
        if soup := Soup.Soup(url=self.baseUrl+url, soupStrainer=self.soupStrainer):
            title = soup.find('h1').text.split(' stream')[0].split(' en')[0]
            img = soup.find(class_='Image').find('img')['data-src']
            genres = [Blank( genre.text.title(), genre['href'].replace(self.baseUrl, '') )
                for genre in soup.find_all(rel='category')]
            desc = soup.find(class_='Description').text

            seasons = []
            episodes = []
            if 'anime' in url:
                for x, tbody in enumerate(soup.find_all('tbody')):
                    seasons.append({'name': soup.find_all(class_='AA-Season')[x].text, 'elements': []})
                    for tr in tbody.find_all('tr'):
                        try: seasons[x]['elements'].append(Elements(
                                tr.find(class_='MvTbTtl').find('a').text, tr.find('a')['href'].replace(self.baseUrl, ''),
                                tr.find('img')['data-src'], 'vertical'
                            ))
                        except: break
                    episodes += seasons[x]['elements']
            else: seasons = [{'name':'Film','elements' :[Elements(title, url, img, 'poster')]}]; episodes.append(1)

            try: date = soup.find(class_='Date').text
            except: date = ''
            infos = [
                date, soup.find(class_='Time').text.strip(),
                url.split('/')[1].replace('-', ' ').title(), f'Episode {len(episodes)}'
            ]

            self.context = Info(title, img, 'poster', genres, desc, seasons, infos)
        return self.context

    def Video(self, url):
        container = []
        if soup := Soup.Soup(url=self.baseUrl+url, soupStrainer=self.soupStrainer):
            for player in soup.find_all(class_='TPlayerTb'):
                url = str(player).split('src=')[1].split('"')[1].replace('#038;', '').replace('amp;', '')
                if soup := Soup.Soup(url=url, soupStrainer=SoupStrainer('iframe')):
                    link = soup.find('iframe')['src']
                    name = link.split('/')[2].split('.')[-2]
                    container.append(Blank(name, link))
        return container

    def Genre(self, genreUrl):
        url = self.baseUrl + genreUrl
        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            genreName = soup.find(class_='Top').find(class_='Title').text.title()
            self.context[genreName] = {'url':url, 'container':[]}
            
            for anime in soup.find_all('article'):
                title = anime.find(class_='Title').text
                img = anime.find('img')['data-src']
                link = anime.find('a')['href'].replace(self.baseUrl, '')
                
                try: time = anime.find(class_='Time').text
                except: time = ''
                try: date = anime.find(class_='Year').text
                except: date = ''
                
                self.context[genreName]['container'].append(Container( title, img, 'poster', link, time, '', date ))
        return self.context


class Adkami:
    def __init__(self):
        self.baseUrl = scrapSites['Adkami']['baseUrl']
        self.context = {}
        self.soupStrainer = SoupStrainer(class_='col-12')

    def Main(self):
        if soup := Soup.Soup(url=self.baseUrl, soupStrainer=self.soupStrainer):
            for div in soup.find(class_='col-12').find_all('div'):
                if 'list-days' in div['class'][0]:
                    sectionName = div.find('h5').text.strip()
                    self.context[sectionName] = {'url': self.baseUrl, 'container':[]}
                    continue
                
                title = div.find(class_='title').text
                img = div.find('img')['data-original']
                link = '/'.join(div.find_all('a')[1]['href'].replace(self.baseUrl, '').split('/')[:3])

                episode = ' '.join(div.find(class_='episode').text.split(' ')[:-1]).title().replace('Animation Digital', '')
                try: site = div.find(class_='team editeur').text.replace('Animation Digital Network', 'ADN')
                except: site = ''

                self.context[sectionName]['container'].append(Container( title, img, 'extra-vertical', link, episode, '', site ))
        return self.context

    def Search(self, search, page):
        url = f'{self.baseUrl}/video?search={search}&page={page}'
        self.context = {'search': search, 'url': url, 'container': []}

        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            for anime in soup.find_all(class_='video-item-list'):
                age = int(anime.find('span')['title'].split('+')[1])
                if age < 18:
                    title = anime.find(class_='title').text
                    img = anime.find('img')['data-original']
                    link = '/'.join(anime.find_all('a')[1]['href'].replace(self.baseUrl, '').split('/')[:3])
                    
                    nbEp = anime.find(class_='episode').text.split(' ')[-1]
                    status = anime.find_all('span')[2]['title']
                        
                    self.context['container'].append(Container( title, img, 'extra-vertical', link, f'Episodes {nbEp}', '', status ))
        return self.context

    def Info(self, url):
        if soup := Soup.Soup(url=self.baseUrl+url, soupStrainer=SoupStrainer('section')):
            title = soup.find_all(itemprop='name')[1].text
            img = soup.find('img')['src']
            genres = [Blank( genre.text.title(), quote(genre['href'].replace(self.baseUrl, '')) )
                for genre in soup.find(class_='info').find_all(class_='label')]
            desc = ' '.join(soup.find(class_='description').text.strip().split('\n')[0].split(' ')[:-1])

            seasons = []
            seasonsDict = {}
            for season in soup.find_all(class_='saison-container')[1:]:
                uls = season.find_all('ul')
                for ul in uls[1:]:
                    seasonName = uls[0].text.title()
                    for ep in ul.find_all('a'):
                        epText = ep.text.split(' ')
                        try: seasonsDict[f'{seasonName} {epText[-1].upper()}'].append([' '.join(epText[:-1]), ep['href']])
                        except: seasonsDict[f'{seasonName} {epText[-1].upper()}'] = [[' '.join(epText[:-1]), ep['href']]]
            seasons.extend({'name': season, 'elements': [Elements(ep[0], ep[1].replace(self.baseUrl, ''))
                for ep in eps]}
            for season, eps in seasonsDict.items())

            infos = [span['title'].capitalize() for span in soup.find(class_='anime-information-icon').find_all('span')]

            self.context = Info(title, img, 'extra-vertical', genres, desc, seasons, infos)
        return self.context

    def Video(self, url):
        container = []
        if soup := Soup.Soup_javascript(urls=[self.baseUrl+url], soupStrainer=SoupStrainer(id='look-video'), sleep=1.7, elements=['.protected-info'], needClick=True)[0]:
            container.extend(Blank('', iframe['src']) for iframe in soup.find_all('iframe'))
            container.extend(Blank('', external['href']) for external in soup.find_all(rel='external'))
        return container

    def Genre(self, genreUrl):
        url = self.baseUrl + unquote(genreUrl)
        if soup := Soup.Soup(url=url, soupStrainer=SoupStrainer(class_='video-item-list')):
            self.context[''] = {'url':url, 'container':[]}
            
            for anime in soup.find_all(class_='video-item-list'):
                age = int(anime.find('span')['title'].split('+')[1])
                if age < 18:
                    title = anime.find(class_='title').text
                    img = anime.find('img')['data-original']
                    link = '/'.join(anime.find_all('a')[1]['href'].replace(self.baseUrl, '').split('/')[:3])
                    
                    nbEp = anime.find(class_='episode').text.split(' ')[-1]
                    status = anime.find_all('span')[2]['title']
                        
                    self.context['']['container'].append(Container( title, img, 'extra-vertical', link, f'Episodes {nbEp}', '', status ))
        return self.context


# stand by clouflare and reCaptcha
class Voiranime:
    def __init__(self):
        self.baseUrl = scrapSites['Voiranime']['baseUrl']
        self.context = {}
        self.proxies = Proxies(self.baseUrl).proxies()
        self.soupStrainer = SoupStrainer(class_='container')

    def Main(self):
        for version in ['subbed', 'dubbed']:
            url = f'{self.baseUrl}/?filter={version}'
            if soup := Soup.Soup_cloudflare(url=url, soupStrainer=self.soupStrainer, proxies=self.proxies):
                sectionName = f"{soup.find(class_='h4').text.strip()} {soup.find(class_='active').text.strip()}"
                self.context[sectionName] = {'url':url, 'container':[]}

                for anime in soup.find_all(class_='page-item-detail'):
                    title = anime.find(class_='post-title').text
                    img = anime.find('img')['src'].replace('-110x150', '')
                    link = anime.find('a')['href'].replace(self.baseUrl, '')

                    episode = f'Episode {soup.find(class_="chapter").text}'
                    date = soup.find(class_='post-on').text
                    
                    self.context[sectionName]['container'].append(Container( title, img, 'poster', link, episode, '', date ))
        return self.context

    def Search(self, search, page):
        url = f'{self.baseUrl}/page/{page}/?s={search}&post_type=wp-manga&op=&author=&artist=&release=&adult=&type=&language='
        self.context = {'search': search, 'url': url, 'container': []}

        if soup := Soup.Soup_cloudflare(url=url, soupStrainer=self.soupStrainer, proxies=self.proxies):
            for anime in soup.find_all(class_='c-tabs-item__content'):
                title = anime.find(class_='post-title').text
                img = anime.find('img')['src'].replace('-193x278', '')
                link = anime.find('a')['href'].replace(self.baseUrl, '')
                
                status = anime.find(class_='mg_status').find(class_='summary-content').text
                try: type = anime.find_all(class_='summary-content')[2].text
                except: type = ''
                date = anime.find(class_='mg_release').find(class_='summary-content').text
                    
                self.context['container'].append(Container( title, img, 'poster', link, status, type, date ))
        return self.context

    def Info(self, url):
        if soup := Soup.Soup_cloudflare(url=self.baseUrl+url, soupStrainer=SoupStrainer(class_='site-content'), proxies=self.proxies):
            title = soup.find('h1').text
            img = soup.find('img')['src'].replace('-193x278', '')
            genres = [Blank( genre.text.title(), genre['href'].replace(self.baseUrl, '') )
                for genre in soup.find_all(rel='tag')]
            desc = soup.find(class_='description-summary').text

            episodes = [Elements(
                ep.find('a').text, ep.find('a')['href'].replace(self.baseUrl, '')
            ) for ep in soup.find_all(class_='wp-manga-chapter')][::-1]

            infos = [info.find(class_='summary-content').text
                for info in soup.find_all(class_='post-content_item')
                if 'Type' in info.find(class_='summary-heading').text or 'Status' in info.find(class_='summary-heading').text
            ]
            infos.append(f'Episode {len(episodes)}')

            self.context = Info( title, img, 'poster', genres, desc, episodes, [], infos )
        return self.context

    def Video(self, url):
        container = []
        if soup := Soup.Soup_cloudflare(url=self.baseUrl+url, reCaptcha=True):
            iframe = soup.find(class_='chapter-video-frame').find('iframe')['src']
            container.append(Blank('', iframe))
        return container

    def Genre(self, genreUrl):
        url = self.baseUrl + genreUrl
        if soup := Soup.Soup_cloudflare(url=url, soupStrainer=self.soupStrainer, proxies=self.proxies):
            genreName = soup.find(class_='entry-title').text.title()
            self.context[genreName] = {'url':url, 'container':[]}

            for anime in soup.find_all(class_='page-item-detail'):
                title = anime.find(class_='post-title').text
                img = anime.find('img')['src'].replace('-110x150', '')
                link = anime.find('a')['href'].replace(self.baseUrl, '')

                episode = f'Episode {soup.find(class_="chapter").text}'
                date = soup.find(class_='post-on').text
                
                self.context[genreName]['container'].append(Container( title, img, 'poster', link, episode, '', date ))
        return self.context


class IAnimes:
    def __init__(self):
        self.baseUrl = scrapSites['IAnimes']['baseUrl']
        self.context = {}
        self.soupStrainer = SoupStrainer(class_='content-inner')

    def Main(self):
        pages = ['nouveautees.html', 'top_30.php', 'films.php?liste=b1u3vv0lSorJk9Lex0tbKZEtbz8RlMC9', 'series.php', 'drama.php']
        for page in pages:
            if page is pages[0]: continue
            url = f'{self.baseUrl}/{page}'
            if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
                sectionName = soup.find(class_='header-title').text.strip()
                self.context[sectionName] = {'url':url, 'container':[]}

                for container in soup.find_all('td', align='center'):
                    title = container.find('center').text
                    img = container.find('div')['style'].split("'")[1]
                    link = quote(container.find('a')['href'])

                    infos = [info.text for info in container.find_all(bgcolor='#DCDCDC')]
                    
                    self.context[sectionName]['container'].append(Container( title, img, 'poster', link, infos[0], '', infos[-1] ))
        return self.context

    def Search(self, search, page):
        url = f'{self.baseUrl}/resultat+{search}.html'
        self.context = {'search': search, 'url': url, 'container': []}

        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            for container in soup.find_all('td', align='center'):
                try: type = container.find('headline11').text.split(' ')[-1].split("'")[-1]
                except: type = container.find('headline12').text.split(' ')[-1]
                if 'Hentai' in type: continue
                title = container.find('center').text
                img = container.find('div')['style'].split("'")[1]
                link = quote(container.find('a')['href'])

                lang = container.find_all(bgcolor='#DCDCDC')[-1].text
                
                self.context['container'].append(Container( title, img, 'poster', link, lang, '', type.title() ))
        return self.context

    def Info(self, url):
        soupStrainer = SoupStrainer(class_='primary_content_wrap_bot')
        originUrl = f'{self.baseUrl}/{unquote(url)}'

        if soup := Soup.Soup(url=originUrl, soupStrainer=soupStrainer):
            title = soup.find('h1').text
            img = soup.find_all('img')[2]['src']
            desc = soup.find_all('fieldset')[-1].find('font').text

            seasons = []
            if 'film' not in originUrl:
                genres = [Blank( genre.text.title(), quote(genre['href']) )
                    for genre in soup.find_all(class_='genre')]

                postList = soup.find(class_='post_list')
                seasonList = postList.find_all('center')
                y = 0
                for x in range(len(seasonList)):
                    season = seasonList[x]
                    seasons.append({'name': season.text, 'elements': []})
                    for i, ep in enumerate(postList.find_all('a')[y:]):
                        try:
                            if ep.text == seasonList[x+1].text:
                                y += i
                                break
                        except: pass
                        if ep.text != season.text:
                            seasons[x]['elements'].append(Elements(ep.text, ep['href'].replace(self.baseUrl, '')))
            else: seasons = [{'name': 'Film','elements':[Elements(title, f'/{soup.find("a")["href"]}', img, 'poster')]}]

            infos = []
            for x, info in enumerate(soup.find_all('font', color='#4682B4')):
                infoTitle = soup.find_all('font', color='#FFA07A')[x].text
                if 'Pays' in infoTitle or 'Origine' in infoTitle or 'Format' in infoTitle or 'Date' in infoTitle or 'Durée' in infoTitle:
                    infos.append(info.text)
                try: 'Genre' in infoTitle and not genres
                except: genres = [Blank(genre.strip()) for genre in info.text.split(',')]

            self.context = Info(title, img, 'poster', genres, desc, seasons, infos)
        return self.context

    def Video(self, url):
        container = []
        if soup := Soup.Soup(url=self.baseUrl+url, soupStrainer=SoupStrainer(class_='box')):
            for script in soup.find_all('script'):
                if 'unescape' in script.text:
                    iframe = unquote(script.text.split('"')[1]).split('src')[1].split("'")[1]
                    if soup := Soup.Soup(url=iframe, method='post', headers=headers|{'referer': iframe, 'content-type': 'application/x-www-form-urlencoded'}, data={'submit.x':'0','submit.y':'0'}):
                        try: container.append(Blank('', soup.find('iframe')['src']))
                        except: pass
        return container

    def Genre(self, genreUrl):
        url = f'{self.baseUrl}/{unquote(genreUrl)}'
        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            genreName = soup.find(class_='header-title').text.strip()
            self.context[genreName] = {'url':url, 'container':[]}

            for container in soup.find_all('td', align='center'):
                title = container.find('center').text
                img = container.find('div')['style'].split("'")[1]
                link = quote(container.find('a')['href'])

                infos = [info.text for info in container.find_all(bgcolor='#DCDCDC')]
                
                self.context[genreName]['container'].append(Container( title, img, 'poster', link, infos[0], '', infos[-1] ))
        return self.context


class Wiflix:
    def __init__(self):
        self.baseUrl = scrapSites['Wiflix']['baseUrl']
        self.context = {}
        self.soupStrainer = SoupStrainer(id='dle-content')

    def Main(self):
        if soup := Soup.Soup(url=self.baseUrl, soupStrainer=SoupStrainer(class_='block-main')):
            for section in soup.find_all(class_='block-main'):
                sectionTitle = section.find(class_='block-title').find_all('a')
                sectionName = sectionTitle[0].text.strip()
                self.context[sectionName] = {'url': sectionTitle[1]['href'], 'container':[]}
                
                for mov in section.find_all(class_='mov'):
                    title = mov.find(class_='mov-t').text
                    img = self.baseUrl + mov.find('img')['src']
                    link = mov.find('a')['href'].replace(self.baseUrl, '')

                    try: ep = mov.find(class_='block-ep').text
                    except: ep = ''
                    center = mov.find(class_='nbloc1-2').text
                    date = mov.find(class_='ml-desc').text

                    self.context[sectionName]['container'].append(Container( title, img, 'poster', link, ep, center, date ))
        return self.context

    def Search(self, search, page):
        url = f'{self.baseUrl}/index.php/search/?story={search}&do=search&search_start={page}&subaction=search&submit=Submit/'
        self.context = {'search': search, 'url': url, 'container': []}

        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            for mov in soup.find_all(class_='mov'):
                title = mov.find(class_='mov-t').text
                img = self.baseUrl + mov.find('img')['src']
                link = mov.find('a')['href'].replace(self.baseUrl, '')

                try: ep = mov.find(class_='block-ep').text
                except: ep = ''
                center = mov.find(class_='nbloc1-2').text
                date = mov.find(class_='ml-desc').text
                    
                self.context['container'].append(Container( title, img, 'poster', link, ep, center, date ))
        return self.context

    def Info(self, url):
        if soup := Soup.Soup(url=self.baseUrl+url, soupStrainer=self.soupStrainer):
            title = soup.find('h1').text
            img = self.baseUrl + soup.find('img')['src']
            desc = soup.find(itemprop='description').text.split('\t')[0]

            movList = soup.find(class_='mov-list')
            genres = [Blank( genre.text, genre['href'].replace(self.baseUrl, '') )
                for genre in movList.find_all('a')]
            infos = [
                info.find(class_='mov-desc').text
                for info in movList.find_all('li')
                if 'date' in info.text.lower() or 'version' in info.text.lower() or 'durée' in info.text.lower()
            ]

            versions = []
            episodes = []
            if 'film' not in url:
                for x, version in enumerate(['vostfr', 'fr']):
                    bloc = soup.find(class_=f'bloc{version}')
                    versions.append({'name': bloc.find('span').text, 'elements': []})
                    for ep in bloc.find_all('li'):
                        versions[x]['elements'].append(Elements(
                            ep.text, quote(f'{url}&rel={ep["rel"]}')
                        ))
                    episodes = versions[x]['elements'] if len(versions[x]['elements']) > len(episodes) else episodes
                infos.append(f'Episode {len(episodes)}')
            else: versions = [{'name': 'Film', 'elements':[Elements(title, url, img, 'poster')]}]

            self.context = Info(title, img, 'poster', genres, desc, versions, infos)
        return self.context

    def Video(self, url):
        container = []
        unquoteUrl = unquote(url).split('&rel=')
        url = self.baseUrl+unquoteUrl[0]
        if 'film' not in url:
            if soup := Soup.Soup(url=url, soupStrainer=SoupStrainer(class_='hostsblock')):
                container.extend(Blank('', player['href'].replace('/vd.php?u=', ''))
                    for player in soup.find(class_=unquoteUrl[1]).find_all('a'))

        elif soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            container.extend(Blank('', player['href'].replace('/vd.php?u=', ''))
                for player in soup.find(class_='tabs-sel').find_all('a'))
        return container

    def Genre(self, genreUrl):
        url = self.baseUrl + genreUrl
        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            self.context[''] = {'url':url, 'container':[]}
                
            for mov in soup.find_all(class_='mov'):
                title = mov.find(class_='mov-t').text
                img = self.baseUrl + mov.find('img')['src']
                link = mov.find('a')['href'].replace(self.baseUrl, '')

                try: ep = mov.find(class_='block-ep').text
                except: ep = ''
                center = mov.find(class_='nbloc1-2').text
                date = mov.find(class_='ml-desc').text
                
                self.context['']['container'].append(Container( title, img, 'poster', link, ep, center, date ))
        return self.context


class FrenchStream:
    def __init__(self):
        self.baseUrl = scrapSites['FrenchStream']['baseUrl']
        self.context = {}
        self.soupStrainer = SoupStrainer(id='dle-content')
        self.proxies = Proxies(self.baseUrl).proxies()

    def Main(self):
        if soup := Soup.Soup(url=self.baseUrl, soupStrainer=SoupStrainer(class_='sect'), proxies=self.proxies):
            for section in soup.find_all(class_='sect'):
                sectionName = section.find(class_='st-capt').text.strip()
                try: url = self.baseUrl + section.find('a')['href']
                except: url = ''
                self.context[sectionName] = {'url': url, 'container':[]}
                
                for short in section.find_all(class_='short-in'):
                    title = short.find(class_='short-title').text
                    img = short.find('img')['src']
                    link = short.find('a', class_='short-poster')['href'].replace(self.baseUrl, '')

                    try: left = short.find(class_='film-ripz').text
                    except: left = short.find(class_='mli-eps').text
                    try: right = short.find(class_='film-verz').text
                    except: right = ''

                    self.context[sectionName]['container'].append(Container( title, img, 'poster', link, left, '', right ))
        return self.context

    def Search(self, search, page):
        url = f'{self.baseUrl}/index.php/search/?story={search}&do=search&search_start={page}&subaction=search&submit=Submit/'
        self.context = {'search': search, 'url': url, 'container': []}

        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer, proxies=self.proxies):
            for short in soup.find_all(class_='short-in'):
                title = short.find(class_='short-title').text
                img = short.find('img')['src']
                link = short.find('a', class_='short-poster')['href'].replace(self.baseUrl, '')

                try: left = short.find(class_='film-ripz').text
                except: left = short.find(class_='mli-eps').text
                try: right = short.find(class_='film-verz').text
                except: right = ''
                    
                self.context['container'].append(Container( title, img, 'poster', link, left, '', right ))
        return self.context

    def Info(self, url):
        if soup := Soup.Soup(url=self.baseUrl+url, soupStrainer=self.soupStrainer, proxies=self.proxies):
            title = soup.find('h1').text
            img = soup.find('img')['src']
            desc = soup.find(class_='fdesc').text

            genres = [Blank( genre.text, genre['href'].replace(self.baseUrl, '') )
                for genre in soup.find(class_='flist clearfix').find_all('a')]
            infos = [
                info.text
                for info in soup.find(class_='flist clearfix').find_all('li')
                if 'Version' in info.text or 'Date' in info.text or 'Genre' in info.text
            ]

            versions = []
            episodes = []
            if 'serie' in url:
                for x, version in enumerate(['VOSTFR', 'VF']):
                    versions.append({'name': soup.find(class_=f'{version}-tab').text.strip(), 'elements': []})
                    for ep in soup.find_all(class_='elink')[x].find_all('a'):
                        versions[x]['elements'].append(Elements(
                            ep.text, quote(f'{url}&rel={ep["data-rel"]}')
                        ))
                    episodes = versions[x]['elements'] if len(versions[x]['elements']) > len(episodes) else episodes
                infos.append(f'Episode {len(episodes)}')
            else: versions = [{'name': 'Film', 'elements':[Elements(title, url, img, 'poster')]}]

            self.context = Info(title, img, 'poster', genres, desc, versions, infos)
        return self.context

    def Video(self, url):
        container = []
        unquoteUrl = unquote(url).split('&rel=')
        url = self.baseUrl+unquoteUrl[0]
        if 'serie' in url:
            if soup := Soup.Soup(url=url, soupStrainer=SoupStrainer(class_='series-center'), proxies=self.proxies):
                for player in soup.find(id=unquoteUrl[1]).find_all(class_='fsctab'):
                    try:
                        url = session.get(url=player['href'], headers=headers).url
                        container.append(Blank(player.text, url))
                    except: pass

        elif soup := Soup.Soup(url=url, soupStrainer=SoupStrainer(id='primary_nav_wrap'), proxies=self.proxies):
            for player in soup.find_all('li'):
                name = player.find('a').text
                for playerVersion in player.find_all('li'):
                    try:
                        url = session.get(url=playerVersion.find('a')['href'], headers=headers).url
                        container.append(Blank(f'{name}:{playerVersion.text}', url))
                    except: pass
        return container

    def Genre(self, genreUrl):
        url = self.baseUrl + genreUrl
        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer, proxies=self.proxies):
            self.context[''] = {'url':url, 'container':[]}

            for short in soup.find_all(class_='short-in'):
                title = short.find(class_='short-title').text
                img = short.find('img')['src']
                link = short.find('a', class_='short-poster')['href'].replace(self.baseUrl, '')

                try: left = short.find(class_='film-ripz').text
                except: left = short.find(class_='mli-eps').text
                try: right = short.find(class_='film-verz').text
                except: right = ''
                
                self.context['']['container'].append(Container( title, img, 'poster', link, left, '', right ))
        return self.context


class Ninemanga:
    def __init__(self):
        self.baseUrl = scrapSites['Ninemanga']['baseUrl']
        self.headers = headers | {
            'upgrade-insecure-requests': '1', 'sec-fetch-site': 'none', 'sec-fetch-mode': 'navigate', 'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'fr',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }
        self.context = {}
        self.soupStrainer = SoupStrainer(class_='mainbox')

    def Main(self):
        sections = ['New-Update/', 'New-Book/', 'Hot-Book/']
        for section in sections:
            url = f'{self.baseUrl}/list/{section}'
            if soup := Soup.Soup(url=url, headers=self.headers, soupStrainer=self.soupStrainer):
                sectionName = soup.find('h1').text.strip().title().replace('Manga Manga', 'Manga').replace('À', 'à')
                self.context[sectionName] = {'url':url, 'container':[]}
                
                mangas = soup.find(class_='direlist').find_all('dl')
                if section is sections[2]: random.shuffle(mangas)
                for manga in mangas[:31]:
                    title = manga.find(class_='bookname').text
                    img = manga.find('img')['src']
                    link = manga.find('a')['href'].replace(self.baseUrl, '')

                    views = manga.find('span').text
                    try: chapter = f"Chapitre {int(manga.find(class_='chaptername').text.split(' ')[-1])}"
                    except: chapter = ''
                    if chapter != '' and len(views.split(',')) > 2:
                        views = f"{','.join(views.split(',')[:2])}M {views.split(' ')[1]}"
                    
                    self.context[sectionName]['container'].append(Container( title, img, 'poster', link, views, '', chapter ))
        return self.context

    def Search(self, search, page):
        url = f'{self.baseUrl}/search/?name_sel=&wd={search}&author_sel=&author=&artist_sel=&artist=&category_id=&out_category_id=&completed_series=&page={page}.html'
        self.context = {'search': search, 'url': url, 'container': []}

        if soup := Soup.Soup(url=url, headers=self.headers,  soupStrainer=self.soupStrainer):
            for manga in soup.find(class_='direlist').find_all('dl'):
                title = manga.find(class_='bookname').text
                img = manga.find('img')['src']
                link = manga.find('a')['href'].replace(self.baseUrl, '')

                views = manga.find('span').text
                try: chapter = f"Chapitre {int(manga.find(class_='chaptername').text.split(' ')[-1])}"
                except: chapter = ''
                if chapter != '' and len(views.split(',')) > 2:
                    views = f"{','.join(views.split(',')[:2])}M {views.split(' ')[1]}"
                    
                self.context['container'].append(Container( title, img, 'poster', link, views, '', chapter ))
        return self.context

    def Info(self, url):
        if soup := Soup.Soup(url=f'{self.baseUrl}{url}?waring=1', headers=self.headers, soupStrainer=self.soupStrainer):
            title = soup.find('h1').text
            img = soup.find(class_='bookface').find('img')['src']
            try: genres = [Blank( genre.text, genre['href'] )
                for genre in soup.find(itemprop='genre').find_all('a')]
            except: genres = [Blank('Manga')]
            try: desc = soup.find(itemprop='description').text
            except: desc = ''

            chapters = [{'name': soup.find(class_='chapterbox').find('h1').text, 'elements': [Elements(
                chapter.text, chapter['href'].replace(self.baseUrl, '').replace('.html', '-10-1.html'), '', '', 'Image'
            ) for chapter in soup.find_all(class_='chapter_list_a')][::-1]}]

            try: status = soup.find(class_='red').text
            except: status = ''
            try: author = soup.find(itemprop='author').text.title()
            except: author = ''
            infos = [status, author, f'Chapitre {len(chapters[0]["elements"])}']

            self.context = Info( title, img, 'poster', genres, desc, chapters, infos )
        return self.context

    def Image(self, url):
        container = []
        numPage = 0
        equal10 = True

        while equal10:
            if soup := Soup.Soup(url=self.baseUrl+url, headers=self.headers, soupStrainer=SoupStrainer('img')):
                page = int(url.split('-')[-1].split('.')[0])

                imgs = soup.find_all('img')[1:]
                for img in imgs:
                    link = img['src']
                    numPage += 1
                    container.append(Blank(numPage, link))
                if len(imgs) < 10: equal10 = False
                url = f"{'-'.join(url.split('-')[:-1])}-{page+1}.html"
            else: equal10 = False
        return container

    def Genre(self, genreUrl):
        url = self.baseUrl + genreUrl
        if soup := Soup.Soup(url=url, headers=self.headers,  soupStrainer=self.soupStrainer):
            genreName = soup.find('h1').text.replace('Annuaire', '').strip().title()
            self.context[genreName] = {'url':url, 'container':[]}
            
            for manga in soup.find(class_='direlist').find_all('dl'):
                title = manga.find(class_='bookname').text
                img = manga.find('img')['src']
                link = manga.find('a')['href'].replace(self.baseUrl, '')

                views = manga.find('span').text
                try: chapter = f"Chapitre {int(manga.find(class_='chaptername').text.split(' ')[-1])}"
                except: chapter = ''
                if chapter != '' and len(views.split(',')) > 2:
                    views = f"{','.join(views.split(',')[:2])}M {views.split(' ')[1]}"
                    
                self.context[genreName]['container'].append(Container( title, img, 'poster', link, views, '', chapter ))
        return self.context

class ScanMangas:
    def __init__(self):
        self.baseUrl = scrapSites['ScanMangas']['baseUrl']
        self.soupStrainer = SoupStrainer(class_='white')
        self.context = {}

    def Main(self):
        for order in ['update', 'popular']:
            url = f'{self.baseUrl}/tous-nos-mangas/?order={order}'
            if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
                sectionName = soup.find(class_='active').text
                self.context[sectionName] = {'url':url, 'container':[]}
                
                for manga in soup.find_all(class_='bsx')[:31]:
                    title = manga.find('a')['title']
                    img = manga.find('img')['src']
                    link = manga.find('a')['href'].replace(self.baseUrl, '')

                    score = f"{'⭐'*int(float(manga.find('i').text)/2)} {manga.find('i').text}/10"
                    
                    self.context[sectionName]['container'].append(Container( title, img, 'poster', link, '', score ))
        return self.context

    def Search(self, search, page):
        url = f'{self.baseUrl}/?s={search}&post_type=manga'
        self.context = {'search': search, 'url': url, 'container': []}

        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            for manga in soup.find_all(class_='bsx'):
                title = manga.find('a')['title']
                img = manga.find('img')['src']
                link = manga.find('a')['href'].replace(self.baseUrl, '')

                try: score = f"{'⭐'*int(float(manga.find('i').text)/2)} {manga.find('i').text}/10"
                except: score = '⭐'*5
                
                self.context['container'].append(Container( title, img, 'poster', link, '', score ))
        return self.context

    def Info(self, url):
        url = self.baseUrl+url
        if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
            title = soup.find('h1').text
            img = soup.find('img', class_='wp-post-image')['src']

            genres = [Blank( genre.text, genre['href'].replace(self.baseUrl, '') ) for genre in soup.find_all(rel='tag')]
            desc = soup.find(class_='desc').text

            chapters = [{'name': soup.find(class_='widget-title_top').text, 'elements': [Elements(
                chapter.find('a').text, chapter.find('a')['href'].replace(self.baseUrl, ''), '', '', 'Image'
            ) for chapter in soup.find_all(class_='lchx desktop')][::-1]}]
            
            infos = [info.text for info in soup.find(class_='spe').find_all('span')[1:-1]]
            self.context = Info( title, img, 'poster', genres, desc, chapters, infos )
        return self.context

    def Image(self, url):
        container = []
        if soup := Soup.Soup(url=self.baseUrl+url, soupStrainer=SoupStrainer('article')):
            print(soup)
            container.extend(
                Blank(numPage+1, soup.find(class_='scan-page')['src'].replace('1.jpg', f'{numPage+1}.jpg'))
            for numPage in range(len(soup.find(id='page-list').find_all('option'))))
        return container

    def Genre(self, genreUrl):
        url = self.baseUrl + genreUrl
        if soup := Soup.Soup(url=url, soupStrainer=SoupStrainer(class_='c-page')):
            if soup := Soup.Soup(url=url, soupStrainer=self.soupStrainer):
                genreName = soup.find(class_='widget-title_top').text
                self.context[genreName] = {'url':url, 'container':[]}
                
                for manga in soup.find_all(class_='bsx')[:31]:
                    title = manga.find('a')['title']
                    img = manga.find('img')['src']
                    link = manga.find('a')['href'].replace(self.baseUrl, '')

                    score = f"{'⭐'*int(float(manga.find('i').text)/2)} {manga.find('i').text}/10"
                    
                    self.context[genreName]['container'].append(Container( title, img, 'poster', link, '', score ))
        return self.context


# stand by clouflare
class MangasOrigines:
    def __init__(self):
        self.baseUrl = scrapSites['MangasOrigines']['baseUrl']
        self.context = {}

    def Main(self):
        for order in ['latest', 'new-manga', 'rating', 'trending', 'views']:
            url = f'{self.baseUrl}/catalogues/?m_orderby={order}'
            if soup := Soup.Soup(url=url, soupStrainer=SoupStrainer(class_='c-page__content')):
                sectionName = soup.find(class_='active').text
                self.context[sectionName] = {'url':url, 'container':[]}
                
                for manga in soup.find_all(class_='page-item-detail'):
                    title = manga.find(class_='post-title').find('a').text
                    img = manga.find('img')['data-src'].replace('-110x150', '')
                    link = manga.find('a')['href'].replace(self.baseUrl, '')

                    try: genre = manga.find(class_='manga-title-badges').text
                    except: genre = ''
                    try: score = f"{'⭐'*len(manga.find_all(class_='rating_current'))} {manga.find(class_='score').text}/5"
                    except: score = ''
                    try: chapter = manga.find(class_='chapter').text.split('-')[0]
                    except: chapter = ''
                    
                    self.context[sectionName]['container'].append(Container( title, img, 'poster', link, genre, score, chapter ))
        return self.context

    def Search(self, search, page):
        url = f'{self.baseUrl}/page/{page}/?s={search}&post_type=wp-manga'
        self.context = {'search': search, 'url': url, 'container': []}

        if soup := Soup.Soup(url=url, soupStrainer=SoupStrainer(class_='c-tabs-item')):
            for manga in soup.find_all(class_='c-tabs-item__content'):
                title = manga.find(class_='post-title').find('a').text
                img = manga.find('img')['data-src'].replace('-110x150', '')
                link = manga.find('a')['href'].replace(self.baseUrl, '')

                try: date = manga.find(class_='release-year').text
                except: date = ''
                try: statut = manga.find(class_='mg_status').find(class_='summary-content').text
                except: statut = ''
                try: chapter = manga.find(class_='chapter').text.split('-')[0]
                except: chapter = ''
                    
                self.context['container'].append(Container( title, img, 'poster', link, date, statut, chapter ))
        return self.context

    def Info(self, url):
        url = self.baseUrl+url
        if soup := Soup.Soup(url=url, soupStrainer=SoupStrainer(class_='site-content')):
            title = soup.find('h1').text
            img = soup.find('img')['data-src']
            author = soup.find(class_='author-content').find('a')
            genres = [Blank( author.text, author['href'].replace(self.baseUrl, '') )]
            genres.extend(Blank( genre.text, genre['href'].replace(self.baseUrl, '') )
                for genre in soup.find(class_='genres-content').find_all('a'))
            try: desc = soup.find(class_='manga-excerpt').text
            except: desc = title

            if chapSoup := Soup.Soup(url=f'{url}ajax/chapters/', headers=headers|{'referer': url}, method='post'):
                chapters = [Elements(
                    chapter.find('a').text, chapter.find('a')['href'].replace(self.baseUrl, ''), '', '', 'Image'
                ) for chapter in chapSoup.find_all(class_='wp-manga-chapter')][::-1]

            
            infos = [info.text for info in soup.find(class_='post-status').find_all(class_='post-content_item')]
            infos.extend([
                f"{'⭐'*len(soup.find_all(class_='rating_current'))} {soup.find(class_='score').text}/5",
                f'Chapitre {len(chapters)}'
            ])
            self.context = Info( title, img, 'poster', genres, desc, chapters, '', infos )
        return self.context

    def Image(self, url):
        container = []
        if soup := Soup.Soup(url=f'{self.baseUrl}{url}?style=list', soupStrainer=SoupStrainer(class_='reading-content')):
            container.extend(
                Blank(numPage+1, img['data-src'])
            for numPage, img in enumerate(soup.find_all('img')))
        return container

    def Genre(self, genreUrl):
        url = self.baseUrl + genreUrl
        if soup := Soup.Soup(url=url, soupStrainer=SoupStrainer(class_='c-page')):
            genreName = soup.find(class_='item-title').text.title()
            self.context[genreName] = {'url':url, 'container':[]}
            
            for manga in soup.find_all(class_='page-item-detail'):
                title = manga.find(class_='post-title').find('a').text
                img = manga.find('img')['data-src'].replace('-110x150', '')
                link = manga.find('a')['href'].replace(self.baseUrl, '')

                try: genre = manga.find(class_='manga-title-badges').text
                except: genre = ''
                try: score = f"{'⭐'*len(manga.find_all(class_='rating_current'))} {manga.find(class_='score').text}/5"
                except: score = ''
                try: chapter = manga.find(class_='chapter').text
                except: chapter = ''
                
                self.context[genreName]['container'].append(Container( title, img, 'poster', link, genre, score, chapter ))
        return self.context



def Index(request): return render(request, 'index.html', context={'scrapSites': dict(sorted(scrapSites.items(), key=lambda t: t[0]))})

def ScrapMain(request):
    site = request.GET['Site']
    context = {'site': site, 'sections': globals()[site]().Main()}
    return render(request, 'scrapMain.html', context=context)

def ScrapSearch(request):
    site = request.GET['Site']
    search = request.GET['search']
    page = int(request.GET['page'])
    context = {'site': site, 'search': search} | globals()[site]().Search(search, page)
    return render(request, 'scrapSearch.html', context=context)

def ScrapGenre(request):
    site = request.GET['Site']
    genreUrl = request.GET['url']
    context = {'site': site, 'sections': globals()[site]().Genre(genreUrl)}
    return render(request, 'scrapMain.html', context=context)
     
def ScrapInfo(request):
    site = request.GET['Site']
    url = request.GET.get('url')
    context = {'site': site, 'info': globals()[site]().Info(url)}
    return render(request, 'scrapInfo.html', context=context)

def ScrapVideo(request):
    site = request.GET['Site']
    url = request.GET.get('url')
    context = {'site': site, 'container': globals()[site]().Video(url)}
    return render(request, 'scrapVideo.html', context=context)

def ScrapImage(request):
    site = request.GET['Site']
    url = request.GET.get('url')
    context = {'site': site, 'container': globals()[site]().Image(url)}
    return render(request, 'scrapImage.html', context=context)