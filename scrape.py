# sourcery skip: avoid-builtin-shadow, remove-zero-from-range, use-getitem-for-re-match-groups
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
        id[x] = re.search('([tt]{2}[0-9]{7,8})',id[x])[1]

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
        except Exception:
                season = soup.select('seasons_content > div > ul > li > a')[0].get_text()
                show_title = soup.select('#titleHeader > div > div.media-body > h5 > a')[0].get_text()

        if x == 'tt0472954':
                season = 18

        for i in range(1, int(season)+1):
                url = f"https://www.imdb.com/title/{x}/episodes?season={i}"
                req=requests.get(url)
                soup=BeautifulSoup(req.text,"html.parser")
                episode_containers = soup.find_all('div', class_ = 'info')

                for episodes in episode_containers:
                        try:
                                season = i
                                episode_number = episodes.meta['content']
                                title = episodes.a['title']
                                airdate = episodes.find('div', class_='airdate').text.strip()
                                rating = episodes.find('span', class_='ipl-rating-star__rating').text
                                total_votes = episodes.find('span', class_='ipl-rating-star__total-votes').text
                                desc = episodes.find('div', class_='item_description').text.strip()
                        except Exception as e:
                                print(e)
                                print(season, episode_number, show_title)
                                season = i
                                episode_number = episodes.meta['content']
                                title = episodes.a['title']
                                airdate = ''
                                rating = ''
                                total_votes = ''
                                desc = ''

                        episode_data = [season, episode_number, title, airdate, rating, total_votes, desc, x, show_title]
                        community_episodes.append(episode_data)

df = pd.DataFrame(community_episodes, columns = ['season', 'episode_number', 'title', 'airdate', 'rating', 'total_votes', 'desc', 'id', 'show_title'])

df['total_votes'] = df['total_votes'].str.replace('(', '').str.replace(')', '').str.replace(',', '')

df.to_csv('data.tsv', sep ='\t')
df = pd.read_csv('data.tsv', sep ='\t')
df

df = df.astype({'episode_number':'int', 'rating':'float'})
df['total_votes']

#checking for bad data
ep_column = df['episode_number']

for x in range(1, len(ep_column)-1):
        if ep_column[x + 1] in [1, 0]:
                continue
        elif ep_column[x+1] - ep_column[x] != 1:
            print(df['title'][x])


url_list = []
ids = []
test = pd.read_csv('data.tsv', sep ='\t')
urls = test['id'].unique()
import imdb
ia = imdb.IMDb()
for i in urls:
        code = i[2:]
        series = ia.get_movie(code)
        cover = series.data['cover url']
        url_list.append(cover)
        ids.append(i)

images = pd.DataFrame(
    {'id': ids,
     'img_url': url_list,
    })

images.to_csv('images.csv')
imgs = pd.read_csv('images.csv')

test = imgs.img_url.str[-15:].unique()
len(test)

for i in test:
        print(i)

imgs['img_url'] = imgs['img_url'].str.replace("SY150_CR2,0,101,150_.jpg", "SY1200_CR2,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("SY150_CR0,0,101,150_.jpg", "SY1200_CR0,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("SX101_CR0,0,101,150_.jpg", "SX808_CR0,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("SY150_CR4,0,101,150_.jpg", "SY1200_CR4,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("SY150_CR3,0,101,150_.jpg", "SY1200_CR3,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("SY150_CR1,0,101,150_.jpg", "SY1200_CR1,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("SY150_CR6,0,101,150_.jpg", "SY1200_CR6,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("SY150_CR9,0,101,150_.jpg", "SY1200_CR9,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("Y150_CR12,0,101,150_.jpg", "Y1200_CR12,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("Y150_CR10,0,101,150_.jpg", "Y1200_CR10,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("SY150_CR8,0,101,150_.jpg", "SY1200_CR8,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("SY150_CR7,0,101,150_.jpg", "SY1200_CR7,0,808,1200_.jpg")
imgs['img_url'] = imgs['img_url'].str.replace("SY150_CR5,0,101,150_.jpg", "SY1200_CR5,0,808,1200_.jpg")

imgs.to_csv('images.csv')

data = pd.read_csv('data.tsv', sep ='\t')
data.drop(['img_url'], axis=1)
show = pd.read_csv('top-shows.csv')
image = pd.read_csv('images.csv')
data.loc[data.id == "tt0290978", 'show_title'] = "The Office UK"
data = pd.merge(data,show[['id','show_rating']],on='id', how='left')
data = pd.merge(data,show[['id','star_cast']],on='id', how='left')
data = pd.merge(data,image[['id','img_url']],on='id', how='left')
data['ep_num'] = data.groupby(['show_title']).cumcount() + 1
data['total_votes'] = data['total_votes'].str.replace('(', '').str.replace(')', '').str.replace(',', '')
data['total_votes'] = data['total_votes'].fillna(0).astype(int)
data['avg_votes'] = data.groupby('show_title')["total_votes"].transform("mean").round()
data['rank'] = data['show_rating'].rank(method='dense', ascending=False)
data['vote_rank'] = data['avg_votes'].rank(method='dense', ascending=False)


data.to_csv('data/data.tsv', sep='\t')

