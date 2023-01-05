from bs4 import BeautifulSoup
import requests
import pandas as pd
import openpyxl
import re #regex
from tqdm import tqdm

url ="https://www.imdb.com/chart/toptv/"
req= requests.get(url)
soup= BeautifulSoup(req.text,"html.parser")

shows = soup.select('td.titleColumn')
crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]
ratings = [b.attrs.get('data-value')
        for b in soup.select('td.posterColumn span[name=ir]')]
id = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]

for x in range(len(id)):
        id[x] = re.search('([tt]{2}[0-9]{7,8})',id[x]).group(1)


linked=soup.find("tbody",class_="lister-list")
rows=linked.find_all("tr")

values = []

for index in range(0, len(shows)):
    show_string = shows[index].get_text()
    movie = (' '.join(show_string.split()).replace('.', ''))
    show_title = movie[len(str(index))+1:-7]
    year = re.search('\((.*?)\)', show_string).group(1)
    place = movie[:len(str(index))-(len(movie))]
    data = {"place": place,
            "show_title": show_title,
            "rating": ratings[index],
            "year": year,
            "star_cast": crew[index],
            "id": id[index]
            }
    values.append(data)

df = pd.DataFrame(values)
df.to_csv('top-shows.csv',index=False)
counter = 0

community_episodes = []      

for x in tqdm(id):
        url = f"https://www.imdb.com/title/{x}/episodes"
        req=requests.get(url)
        soup=BeautifulSoup(req.text,"html.parser")
        try:
                season = soup.select('#episode_top')[0].get_text()

                if season.startswith(u"Season\xa0"):
                        season = season.replace(u'Season\xa0', u'')
                elif season.startswith(u'Season&nbsp;'):
                        season = season.replace(u'Season&nbsp;', u'')
                elif season.startswith('Unknown'):
                        season = soup.select('#bySeason > option:nth-last-child(2)')[0].get_text().replace('\n', '').strip()
                        
                show_title = soup.select('div.subpage_title_block > div > div > h3 > a')[0].get_text()
        except:
                season = soup.select('seasons_content > div > ul > li > a')[0].get_text()
                show_title = soup.select('#titleHeader > div > div.media-body > h5 > a')[0].get_text()
                pass
        try:
                for i in range(1, int(season)+1):
                        url = f"https://www.imdb.com/title/{x}/episodes?season={i}"
                        req=requests.get(url)
                        soup=BeautifulSoup(req.text,"html.parser")
                        episode_containers = soup.find_all('div', class_ = 'info')

                        for episodes in episode_containers:
                            season = i
                            episode_number = episodes.meta['content']
                            title = episodes.a['title']
                            airdate = episodes.find('div', class_='airdate').text.strip()
                            rating = episodes.find('span', class_='ipl-rating-star__rating').text
                            total_votes = episodes.find('span', class_='ipl-rating-star__total-votes').text
                            desc = episodes.find('div', class_='item_description').text.strip()
                            episode_data = [season, episode_number, title, airdate, rating, total_votes, desc, x, show_title]
                            community_episodes.append(episode_data)
        except Exception as e:
                print(e)
                continue

community_episodes
show_title
df = pd.DataFrame(community_episodes, columns = ['season', 'episode_number', 'title', 'airdate', 'rating', 'total_votes', 'desc', 'id', 'show_title'])

df['total_votes'] = df['total_votes'].str.replace('(', '').str.replace(')', '').str.replace(',', '')

df.to_csv('data.tsv', sep ='\t')


df = df.astype({'episode_number':'int', 'rating':'float'})
df['total_votes']

#checking for bad data
ep_column = df['episode_number']

for x in range(1, len(ep_column)-1):
    if ep_column[x+1] == 1 or ep_column[x+1] == 0:
        continue
    elif ep_column[x+1] - ep_column[x] != 1:
        print(df['title'][x])