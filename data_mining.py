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

# 분석 시작 시간 저장
start_time = time()

# timeline.lane 에 NONE이 없는 게임 쿼리
# matches = collection.find({'participants': {'$not' :{'$elemMatch': {'timeline.lane' : 'NONE'}}}})
# # 소환사 uid, 게임 플레이 횟수를 key, value로 가지는 dictionary
# numberofgames_dict = defaultdict(int)
# for match in matches:
#     for player in match['participantidentities']:
#         # 소환사의 uid는 matchhistoryuri에서 공통된 문자열 '/v1/stats/player_history/KR/' or '/v1/stats/player_history/kr/' 을 제외한 뒤 숫자부분이므로 [28:]로 슬라이싱
#         numberofgames_dict[player['player']['matchhistoryuri'][28:]] += 1
# # 소환사별 게임 플레이 횟수 최소값 : 1, 최댓값 : 161
# print('number of games played by single summoner')
# print('min :', min(numberofgames_dict.values()), 'max :', max(numberofgames_dict.values()))
# # 10판 이상 플레이한 소환사 (39,829명)
# print(len([i for i in numberofgames_dict.values() if i >= 10]))
# # 20판 이상 플레이한 소환사 (20,208명)
# print(len([i for i in numberofgames_dict.values() if i >= 20]))
# # 30판 이상 플레이한 소환사 (11,293명)
# print(len([i for i in numberofgames_dict.values() if i >= 30]))
# # 40판 이상 플레이한 소환사 (6,526명)
# print(len([i for i in numberofgames_dict.values() if i >= 40]))
# # 50판 이상 플레이한 소환사 (3,786명)
# print(len([i for i in numberofgames_dict.values() if i >= 50]))
# # numberofgames_dict 검증
# print(numberofgames_dict['2384460278402912'])

# 게임 플레이 횟수에 따라 소환사를 선별하여 활용할 데이터 선택
# game_limit = 50
# summoner_set = set([key for key, value in numberofgames_dict.items() if value >= game_limit])
# # summoner_set 검증
# print(len(summoner_set))

# matches = collection.find({'participants': {'$not' :{'$elemMatch': {'timeline.lane' : 'NONE'}}}})
# summoner_dict = defaultdict(list)
# for match in matches:
#     blue_team_damage, red_team_damage = 0, 0
#     blue_team_death, red_team_death = 0, 0
#     for player in match['participants']:
#         if player['teamid'] == 100:
#             blue_team_damage += player['stats']['totaldamagedealttochampions']
#             blue_team_death += player['stats']['deaths']
#         else:
#             red_team_damage += player['stats']['totaldamagedealttochampions']
#             red_team_death += player['stats']['deaths']
#     valid_players = set()
#     participantid_to_puid = {}
#     for player in match['participantidentities']:
#         if player['player']['matchhistoryuri'][28:] in summoner_set:
#             valid_players.add(player['participantid'])
#             participantid_to_puid[player['participantid']] = player['player']['matchhistoryuri'][28:]
#     for player in match['participants']:
#         if player['participantid'] in valid_players:
#             puid = participantid_to_puid[player['participantid']]
#             if player['teamid'] == 100:
#                 damage_factor = round(player['stats']['totaldamagedealttochampions'] / blue_team_damage, 5)
#                 if blue_team_death == 0:
#                     death_factor = 0
#                 else:
#                     death_factor = round(player['stats']['deaths'] / blue_team_death, 5)
#             else:
#                 damage_factor = round(player['stats']['totaldamagedealttochampions'] / red_team_damage, 5)
#                 if red_team_death == 0:
#                     death_factor = 0
#                 else:
#                     death_factor = round(player['stats']['deaths'] / red_team_death, 5)
#             if not summoner_dict[puid]:
#                 summoner_dict[puid].extend([damage_factor, death_factor])
#             else:
#                 summoner_dict[puid][0] += damage_factor
#                 summoner_dict[puid][1] += death_factor

# for puid in summoner_set:
#     summoner_dict[puid][0] = round(summoner_dict[puid][0] / numberofgames_dict[puid], 5)
#     summoner_dict[puid][1] = round(summoner_dict[puid][1] / numberofgames_dict[puid], 5)

# with open('summoner_dict_over_' + str(game_limit) + '.json', 'w') as make_file:
#     json.dump(summoner_dict, make_file, indent='\t')

matches = collection.find()
for match in matches:
    position = defaultdict(int)
    for s in match['participantextendedstats']:
        position[s['position']] += 1
    if len(position) != 5:
        print(position)
        break
    for i in position.values():
        if i != 2:
            print(position)
            break

# 분석 완료까지 걸린 시간 출력
print(time() - start_time)

