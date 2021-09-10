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

# 분석에 사용할 Feature
col_names = ['kills', 'deaths', 'assists', 'champlevel', 'totaldamagedealt', 
'totaldamagedealttochampions', 'damagedealttoobjectives', 'damagedealttoturrets', 'totaldamagetaken', 'neutralminionskilledteamjungle', 
'neutralminionskilledenemyjungle', 'neutralminionskilled', 'totalminionskilled', 'goldearned', 'goldspent', 
'wardsplaced', 'wardskilled', 'visionwardsboughtingame', 'visionscore']

# 분석 시작 시간 저장
start_time = time()

#################################################################################################################################################
#################################################################################################################################################

# # position value 적합성 검증
# # 하나의 매치에 팀별로 TOP, JUNGLE, MID, ADC, SUPPORT 가 하나씩 존재하는지 체크
# matches = collection.find()
# valid_position = set(['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT'])
# for match in matches:
#     participantid_to_teamid = [0 for _ in range(11)]
#     for participants in match['participants']:
#         participantid_to_teamid[participants['participantid']] = participants['teamid']
#     position_blueteam = defaultdict(int)
#     position_redteam = defaultdict(int)
#     for extended_stats in match['participantextendedstats']:
#         teamid = participantid_to_teamid[extended_stats['participantid']]
#         if teamid == 100:
#             position_blueteam[extended_stats['position']] += 1
#         else:
#             position_redteam[extended_stats['position']] += 1
#     for i, j in zip(position_blueteam.keys(), position_redteam.keys()):
#         if i not in valid_position or j not in valid_position:
#             print(position_blueteam, position_redteam)
#             break
#     for i, j in zip(position_blueteam.values(), position_redteam.values()):
#         if i != 1 or j != 1:
#             print(position_blueteam, position_redteam)
#             break
# print(time() - start_time)
# start_time = time()

#################################################################################################################################################
#################################################################################################################################################

# 유효 매치 데이터 load
matches = collection.find({'participants': {'$not' :{'$elemMatch': {'timeline.lane' : 'NONE'}}}})
# 소환사 uid, 게임 플레이 횟수를 key, value로 가지는 dictionary
summoners_dict = defaultdict(list)
for match in matches:
    pid_to_puid = {}
    for player in match['participantidentities']:
        # 소환사의 uid는 matchhistoryuri에서 공통된 문자열 '/v1/stats/player_history/KR/' or '/v1/stats/player_history/kr/' 을 제외한 뒤 숫자부분이므로 [28:]로 슬라이싱
        pid = player['participantid']
        puid = player['player']['matchhistoryuri'][28:]
        pid_to_puid[pid] = puid
    for player in match['participants']:
        pid = player['participantid']
        puid = pid_to_puid[pid]
        feature_list = []
        for feature in col_names:
            feature_list.append(player['stats'][feature] / match['gameduration'])
        summoners_dict[puid].append(feature_list)
# json 파일 저장
with open('summoners_dict.json', 'w') as make_file:
    json.dump(summoners_dict, make_file, indent='\t')
# 작업 시간 출력
print(time() - start_time)
start_time = time()

#################################################################################################################################################
#################################################################################################################################################

# # 소환사별 플레이 판 수 최소, 최댓값, 10판 / 50판 이상 플레이한 소환사 수 출력
# min, max = 1000, 0
# cnt_10, cnt_50 = 0, 0
# for val in summoners_dict.values():
#     if min > len(val):
#         min = len(val)
#     if max < len(val):
#         max = len(val)
#     if len(val) >= 10:
#         cnt_10 += 1
#         if len(val) >= 50:
#             cnt_50 += 1
# print(min, max, cnt_10, cnt_50)

#################################################################################################################################################
#################################################################################################################################################

# dictionary 형태의 데이터를 이중 리스트로 변환. 한 명의 소환사가 플레이한 여러 판의 데이터는 평균값을 계산해 저장
# 플레이 판 수에 따라 다른 데이터 셋 생성

with open('summoners_dict.json', 'r') as json_file:
    summoners_dict = json.load(json_file)

feature_over_10, feature_over_50 = [], []

for game_limit in [10, 50]:
    summoners_list = []
    for puid in summoners_dict.keys():
        games = summoners_dict[puid]
        if len(games) >= game_limit:
            feature = [puid]
            _feature = [0 for _ in range(len(games[0]))]
            for game in games:
                for i in range(len(game)):
                    _feature[i] += game[i]
            for i in range(len(_feature)):
                _feature[i] = round(_feature[i] / len(games), 5)
            feature.extend(_feature)
            summoners_list.append(feature)
    with open('feature_over_' + str(game_limit) + '.json', 'w') as make_file:
        json.dump(summoners_list, make_file, indent='\t')
        
print(time() - start_time)
start_time = time()

#################################################################################################################################################
#################################################################################################################################################

