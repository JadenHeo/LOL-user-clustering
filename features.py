from pymongo import MongoClient
from collections import defaultdict
from time import time
import json

# MongoDB 접속
host = "localhost"
port = "27017"
client = MongoClient(host, int(port))
db = client['lol_matchdata']
collection = db['summonerdata']
summoners = collection.find()

game_limit = 50
summoner_avg_data = []
data = []

for summoner in summoners:
    temp = []
    puid = summoner['puid']
    temp.append(puid)
    num_of_games = len(summoner['data'])
    selected_stats = defaultdict(int)
    selectors = ['kills', 'deaths', 'assists', 'totalminionskilled', 'neutralminionskilled', 'neutralminionskilledteamjungle', 'neutralminionskilledenemyjungle',
    'totaldamagedealt', 'totaldamagedealttochampions', 'totaldamagetaken', 'damagedealttoobjectives', 'totalheal', 'wardsplaced', 'wardskilled', 'visionscore', 'champlevel',
    'damagedealttoturrets', 'longesttimespentliving']
    if num_of_games >= game_limit:
        for game in summoner['data']:
            gameduration = (game['gameduration'] // 100) + (game['gameduration'] % 100) / 60
            stats = game['stats']
            for selector in selectors:
                selected_stats[selector] += stats[selector] / gameduration
        for key in selected_stats.keys():
            selected_stats[key] = round(selected_stats[key] / num_of_games, 5)
            temp.append(round(selected_stats[key] / num_of_games, 5))
        summoner_avg_data.append({'puid' : puid, 'stats' : selected_stats})
        data.append(temp)

with open('summoner_avg_data_' + str(game_limit) + '.json', 'w') as make_file:
    json.dump(summoner_avg_data, make_file, indent='\t')

with open('dataframe_' + str(game_limit) + '.json', 'w') as make_file:
    json.dump(data, make_file, indent='\t')


