from pymongo import MongoClient
from collections import defaultdict
from time import time
import json

# MongoDB 접속
host = "localhost"
port = "27017"
client = MongoClient(host, int(port))
db = client['lol_matchdata']
collection = db['matchdata']

data = defaultdict(list)

start_time = time()

matches = collection.find({'participants': {'$not' :{'$elemMatch': {'timeline.lane' : 'NONE'}}}})
numberofgames_dict = defaultdict(int)
for match in matches:
    for player in match['participantidentities']:
        # 소환사의 uid는 matchhistoryuri에서 공통된 문자열 '/v1/stats/player_history/KR/' or '/v1/stats/player_history/kr/' 을 제외한 뒤 숫자부분이므로 [28:]로 슬라이싱
        numberofgames_dict[player['player']['matchhistoryuri'][28:]] += 1
# # 소환사별 게임 플레이 횟수 최소, 최댓값
# print('number of games played by single summoner')

# 게임 플레이 횟수에 따라 소환사를 선별하여 활용할 데이터 선택
game_limit = 10
summoner_set = set([key for key, value in numberofgames_dict.items() if value >= game_limit])

# timeline.lane 에 NONE이 없는 게임 쿼리
matches = collection.find({'participants': {'$not' :{'$elemMatch': {'timeline.lane' : 'NONE'}}}})
for match in matches:
    gameduration = match['gameduration']
    valid_players = set()
    participantid_to_puid = {}
    for player in match['participantidentities']:
        if player['player']['matchhistoryuri'][28:] in summoner_set:
            valid_players.add(player['participantid'])
            participantid_to_puid[player['participantid']] = player['player']['matchhistoryuri'][28:]
    for player in match['participants']:
        if player['participantid'] in valid_players:
            puid = participantid_to_puid[player['participantid']]
            data[puid].append({'stats' : player['stats'], 'gameduration' : gameduration})

list_data = [{'puid' : puid, 'data' : data[puid]} for puid in data.keys()]

with open('summoner_data.json', 'w') as make_file:
    json.dump(list_data, make_file, indent='\t')
