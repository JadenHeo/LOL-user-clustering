# LOL 매치 데이터를 통한 유저 분석

# 주제

17만여 건의 매치 데이터를 이용하여 매치에 존재하는 소환사들을 나눌 수 있는 '티어를 제외한' 기준을 제시한다.

# 데이터 분석 방법론 선정

소환사들을 특정 기준에 따라 여러 개의 집단으로 나눌 것이므로 지도학습 / 비지도학습 등의 방법 중, **비지도학습의 클러스터링**을 사용한다.

소환사들이 어떤 집단에 속하는지 정답이 정해지지 않은 상황이기 때문에 지도학습이 힘들고, 적절한 feature들을 선정하여 **K-means 클러스터링을 통해 소환사들을 분류**해보려 한다.

# 가설

League Of Legends (이하 '롤') 플레이는 자유도가 굉장히 높고, 플레이하는 소환사는 매 순간마다 다양한 선택의 기로에 놓인다.

같은 상황에서도 소환사 **개인의 성향에 따라 다양한 선택이 존재**하게 되고, 이 매 순간의 **선택은 결국 소환사의 플레이 스타일을 결정**짓게 된다. 플레이 스타일은 공격적 ~ 수비적까지 다양한 종류로 나뉠 것으로 예상되고, 소환사의 플레이 스타일에 영향을 줄 수 있다고 판단되는 feature들을 이용해 K-means 분석을 실시하면 몇 개의 집단으로 소환사들이 나눠지게 될지 알 수 있을 것이다.

K-means를 통해 나온 **각 클러스터는 소환사의 플레이 스타일을 대표**하고, 각 클러스터가 어떤 플레이 스타일의 소환사들을 포함하는지 해석하여 가설을 검증할 수 있다.

# 데이터 분석

## 0. 분석 Tool

매치 데이터는 dictionary와 list로 구성된 **비정형 데이터**이기 때문에 No-SQL **MongoDB**에 저장해 분석했다. MongoDB를 통해 많은 양의 데이터도 간단한 쿼리를 이용해서 간단한 데이터의 추세를 관찰할 수 있었다.

연산 및 분석에는 **Python**을 사용했다. pymongo 라이브러리를 이용해 MongoDB와 쉽게 연동하여 사용할 수 있었으며, **numpy, pandas, sklearn, seaborn** 라이브러리를 이용해 데이터 정리, 분석, 가시화 등의 과정을 진행했다.

## 1. 유효 매치 데이터 선택

17만 개의 매치 데이터 중에서는 분명 분석에 적합하지 않은 데이터들도 존재할 것이라고 생각해, 특정 기준에 따라 유효한 데이터만을 분석에 사용하기로 했다. '유효한 데이터'를 선정하는 과정에서 다음 두 개의 관점이 존재했다.

- 해당 매치 데이터가 유효한가?
- 분석할 대상 소환사의 데이터가 유효한가?

매치 데이터의 유효성 검증을 위해 가장 쉽게 생각할 수 있는 기준은 '플레잉 타임'이었다. 게임 시간이 지나치게 짧은 데이터들은 분석에 있어 outlier로 작용할 가능성이 크다고 생각해서 제외하려 한다. 그렇다면 어떤 기준으로 '지나치게 짧은 게임'을 구별해 낼 것인가가 관건이었고, MongoDB 쿼리를 통해 다양한 조건에 따라 데이터들을 조회한 결과, *lane* 데이터에서 그 힌트를 얻을 수 있었다.

**Riot API Document**에 따르면, Riot이 자체적으로 여러 데이터들을 종합해 **participant(이하 '플레이어')**의 다양한 정보들을 종합해 해당 플레이어의 포지션을 결정짓는 것을 알 수 있다. **약 87.5%의 정확도**를 보인다고 주장하고 있으며, *lane*과 *role* 데이터를 통해 롤의 5개 포지션인 탑, 정글, 미드, 원거리 딜러, 서포터로 포지션을 분류하고 있다. lane, role, position 데이터는 아래 주어진 값들 중 하나를 가지며, 플레이어의 포지션은 우선 아래와 같은 간단한 매핑으로 결정할 수 있다고 소개하고 있다.

```python
# Role: DUO, DUO_CARRY, DUO_SUPPORT, NONE, and SOLO

# Lane: TOP_LANE, MID_LANE, BOT_LANE, and JUNGLE

# Position: TOP, MIDDLE, JUNGLE, BOTTOM, UTILITY, APEX, and NONE

{
(MID_LANE, SOLO): MIDDLE,
(TOP_LANE, SOLO): TOP,
(JUNGLE, NONE): JUNGLE,
(BOT_LANE, DUO_CARRY): BOTTOM,
(BOT_LANE, DUO_SUPPORT): UTILITY
}
```

우선, 위 소개된 값들 외에 *role*, *lane*, *position* 값이 정확히 어떤 의미를 가지는 데이터들인지 공식 문서에는 명시되어 있지 않았다. 따라서 각 데이터들이 17만 개의 매치에서 가지는 값들을 검토하면서 어떤 의미인지 찾을 필요가 있었다.

- Riot Doc에 소개된 Role : 매치 데이터에서의 *role* 값이 정확히 일치. 그러나 명시된 값들의 해석 만으로는 각 값들이 어떤 의미를 가지는지 정확히 판단이 어려움
- Riot Doc에 소개된 Lane : 매치 데이터에 존재하는 *lane* 값과 그 범위가 다르고, 문서에도 정확히 어떤 의미를 가지는지 소개되지 않아 판단이 어려움
- Riot Doc에 소개된 Position : 문서에 따르면, 위 매핑을 포함해 플레이어가 플레이한 챔피언의 종류, 타임라인에 따른 플레이어의 위치 **데이터 등을 이용하여 87.5%의 신뢰도를 가지도록 산출된 값. 매치 데이터 속 *lane* 값이 이 값들을 가지고 있음**
    - **매치 데이터 속 lane은 플레잉 타임이 1200, 즉 20분 미만의 게임에 한해 모든 플레이어가 NONE의 값을 가짐**. 플레잉 타임이 20분이 넘어가야 신뢰도 있는 Position을 계산해 매치 데이터 속 *lane* 값에 넣어주는 것으로 예상됨
    - (추가) 매치 데이터 속에 포함된 *position* 데이터 : *MID, TOP, JUNGLE, ADC, SUPPORT*의 값으로 한 팀에 포지션 별로 1명씩 정확히 할당. 17만 건의 매치 데이터에 단 하나의 예외도 없다는 점, 그리고 *position* 값은 티어 점수와 함께 하나의 dict에 포함되어 있다는 점을 근거로 게임 시작 전 플레이어에게 할당된 포지션이라고 판단됨

위와 같은 과정으로 매치 데이터 속 *lane*, *role*, *position* 데이터들을 살펴봄으로써 분석에 **유효한 게임의 최저 플레잉 타임을 1200(20분)으로 결정**할 수 있었다. Riot에서 자체적으로 플레잉 타임이 짧아 정확한 Position 분석이 이루어지지 않은 게임들은 *lane* 값에 *NONE*을 할당했기 때문에, *lane* 값이 *NONE*인 플레이어가 포함된 게임을 제외함으로써 유효 매치 데이터를 선택할 수 있었다 (플레잉 타임 1200이라는 경곗값에 Position 분석이 이루어진 / 이루어지지 않은 경기들이 동시에 존재했기 때문에, 플레잉 타임으로 필터링하는 것은 부적절하다고 판단).

MongoDB에서 lane 값이 'NONE'인 플레이어가 있는 매치를 제외하면, 17만 개 중 약 13만 개의 매치 데이터가 선택된다. 해당 매치들은 MongoDB 쿼리를 통해 쉽게 찾을 수 있다. 아래의 쿼리로 선택된 약 13만 개의 매치 데이터를 이용하여 데이터 분석을 실시한다.

```python
{'participants': {'$not' :{'$elemMatch': {'timeline.lane' : 'NONE'}}}}
```

또한 매치 데이터에서 얻을 수 있는 소환사 별 게임 데이터를 살펴보니 **최소 1판 ~ 최대 161판까지 플레이한 소환사들이 다양하게 존재**했다. 소환사의 플레이 스타일은 **일정 판 수 이상을 분석해야 신뢰도가 있을 것**으로 생각되어 기본적으로 **10판 이상 플레이한 소환사들의 데이터에 대해서 분석을 진행하고, 50판 이상의 높은 신뢰도를 보이는 소환사에 대해서도 분석**해보려 한다. 플레이 판 수 별 소환사의 수는 다음과 같다.

```python
# 소환사별 게임 플레이 횟수 최소값 : 1, 최댓값 : 161

# 10판 이상 플레이한 소환사 : 39,829명
# 20판 이상 플레이한 소환사 : 20,208명
# 30판 이상 플레이한 소환사 : 11,293명
# 40판 이상 플레이한 소환사 : 6,526명
# 50판 이상 플레이한 소환사 : 3,786명
```

## 2. 데이터 변환

주어진 매치 데이터는 하나의 매치에서 일어난 일들을 플레이어 별로 저장한 데이터다. 소환사를 분류하려는 데이터 분석에 이와 같은 종류의 데이터는 적절하지 않으므로, 각 소환사 별로 플레이 데이터 list를 갖고 있도록 변환해 준다. 변환된 데이터는 다음과 같은 형태를 띤다.

```python
"206929328": [
{
	"stats": {}, "gameduration": 1514
},
{
	"stats": {}, "gameduration": 1908
}
],
```

dictionary의 **key는 소환사의 고유 id인 *puid***이며, **value는 소환사가 플레이 한 게임들의 *stats*, *gameduration*** 데이터를 리스트로 저장한다. *puid*는 *participantidentities → player → matchhistoryuri*에 저장된 데이터의 마지막 숫자 부분을 통해 알 수 있다.

## 3. Feature 선정

매치 데이터를 살펴보면 *seansonid*, *queid*, *gameversion* 등등 기본적인 해당 매치에 관한 정보들이 존재한다. 그중 *gameduration*은 차 후에 플레이어 세부 스탯을 보정하는 데 사용될 수 있으므로 두고, **나머지 데이터들은 플레이어가 본인의 스타일에 따라 선택할 수 있는 값들이 아니기 때문에** 배제했다.

*participants* 배열은 각 플레이어의 게임 내 행동이 기록된 데이터이므로, 소환사의 플레이 스타일을 분석하는 데에 가장 중요한 요소라고 볼 수 있다. *participant* 배열의 element는 단일 플레이어의 데이터를 보여주며, 다음과 같은 값들을 가진다.

```python
"participants": {
        "stats": {...},
        "participantid": 1,
        "timeline": {
            "lane": "MIDDLE",
            "participantid": 1,
            "csdiffpermindeltas", 
            "goldpermindeltas", 
            "xpdiffpermindeltas", 
            "creepspermindeltas", 
            "xppermindeltas", 
            "role": "SOLO", 
            "damagetakendiffpermindeltas", 
            "damagetakenpermindeltas"},
        "teamid": 100,
        "spell2id": 12,
        "spell1id": 4,
        "championid": 38}
```

- *stats* : 플레이어의 행동이 반영된 데이터 셋으로, 가장 눈여겨봐야 할 데이터
- *timeline* : 기본적으로 deltas, 즉 상대와의 시간 별 지표 차이를 저장하는데, 상대 플레이어 선정이 어떤 기준으로 이루어지는지 정확히 알 수 없었기 때문에 배제함
- *participantid*, *teamid* : 플레이어가 선택할 수 없는 값이기 때문에 배제함
- *spell1id*, *spell2id*, *championid* : 플레이어가 선택할 수 있지만, 스펠과 챔피언은 너무나 다양한 조합이 존재하고, 각 조합에 플레이 스타일이 어떻게 반영될지 예측이 어렵다고 판단해 배제함

위 근거들을 통해 stats에 포함된 데이터들을 분석에 주로 이용하기로 결정했다. stats에는 굉장히 많은 종류의 값들이 존재하는데, 종류별로 데이터들을 묶으면 다음과 같다.

```python
# 1. 킬, 데스, 어시스트, 챔피언 레벨, 최대 생존 시간
"kills", "deaths", "assists", "champlevel", "longesttimespentliving"

# 2. 가한 피해
"physicaldamagedealt", "magicdamagedealt", "truedamagedealt", "totaldamagedealt", 
"physicaldamagedealttochampions", "magicdamagedealttochampions", "truedamagedealttochampions",
"totaldamagedealttochampions", "damagedealttoobjectives", "damagedealttoturrets"

# 3. 받은 피해
"physicaldamagetaken", "magicaldamagetaken", "truedamagetaken", "totaldamagetaken"

# 4. 몬스터 처치
"neutralminionskilledteamjungle", "neutralminionskilledenemyjungle", "neutralminionskilled", "totalminionskilled"

# 5. 벌어들인 골드, 사용된 골드
"goldearned", "goldspent"

# 6. 시야 데이터
 "wardsplaced", "wardskilled", "sightwardsboughtingame", "visionwardsboughtingame", "visionscore"

# 7. 룬, 아이템 데이터
"perk0-5", "perk0-5var1-3", "statperk0-2", "perkprimarystyle", "perksubstyle", "item0-6"

# 8. 군중 제어기, 피해 감소, 힐, 크리티컬 등 플레이한 챔피언이나 아이템의 종류에 따라 급변하는 값을 가지는 데이터
"totaltimecrowdcontroldealt", "timeccingothers", "totalunitshealed", "totalheal", "largestcriticalstrike", "damageselfmitigated"

# 9. 대부분의 값이 0, 1, 2 ... 정도로 지나치게 정형화 된 데이터
"largestkillingspree", "quadrakills", "firsttowerassist", "firsttowerkill", "firstbloodassist", "turretkills", "triplekills", 
"doublekills", "unrealkills", "largestmultikill", "killingsprees", "pentakills", "firstbloodkill", "inhibitorkills", "win"

# 10. 정확히 어떤 정보를 포함하는지 알 수 없는 데이터
"totalplayerscore", "totalscorerank", "objectiveplayerscore", "combatplayerscore"

# 11. 플레이어의 선택에 영향을 받지 않는 플레이어 id
"participantid"
```

- 9, 10, 11번 데이터는 위 언급된 이유들로 분석할 Feature에서 제외
- 7, 8번 데이터는 룬, 아이템, 챔피언의 종류에 따라 너무 다른 값을 가지기 때문에, 룬, 아이템, 챔피언 데이터를 직접 고려해서 분석하지 않으면 정확한 분석이 어렵다고 판단해 제외
- 2, 3번의 가한 피해 및 받은 피해는 물리/마법/고정 피해로 카테고리가 나눠져있는데, 이 역시 챔피언의 종류에 의존해 달라질 것이므로 제외. 이들을 대표하는 total 값을 대표로 포함

상기 과정에 따라 분석에 이용할 Feature로 다음과 같은 20개의 데이터를 선정했다. 선정된 Feature를 바탕으로 pandas dataframe에 사용될 column을 아래와 같이 만들 수 있었다.

```python
col_names = ['kills', 'deaths', 'assists', 'champlevel', ~~'longesttimespentliving'~~, 'totaldamagedealt', 'totaldamagedealttochampions', 
'damagedealttoobjectives', 'damagedealttoturrets', 'totaldamagetaken', 'neutralminionskilledteamjungle', 'neutralminionskilledenemyjungle', 
'neutralminionskilled', 'totalminionskilled', 'goldearned', 'goldspent', 'wardsplaced', 'wardskilled', ~~'sightwardsboughtingame',~~ 
'visionwardsboughtingame', 'visionscore']
```

선택된 20개의 데이터는 게임이 진행됨에 따라 쌓여가는 정수 형태의 누적 데이터이며 **게임 진행 시간에 따라 그 크기가 달라지므로 플레잉 타임으로 나누어 그 값을 저장**한다. 이후 소환 사별로 플레이한 게임의 모든 Feature들을 평균 내어 데이터에 넣어주어 그 값을 해당 소환사의 Feature로 사용한다. 다만, 최대 생존 시간인 *longesttimespentliving*은 다른 데이터와 다르게 플레잉 타임에 따라 누적되는 데이터가 아니며, 생존에 관한 정보는 *deaths*로 충분히 반영될 수 있다고 판단하여 자체적으로 제외했다.

**(추가)** 20개의 feature를 분석하는 과정에서 *sightwardsboughtingame* 데이터가 scaling 과정에 문제를 발생시켜 조회해보니 모든 데이터에서 값이 0이었기 때문에, 이 역시도 제외했다. **결과적으로 19개의 feature에 대해 분석을 진행**했다.

## 4. 데이터 분석 및 해석

### 4.1 Feature Scaling

각 feature들은 게임 진행 시간에 따라 분당 데이터로 환산되어 있다. Feature의 종류에 따라 scale이 다 다르고, scale의 차이가 너무 크다면 클러스터링이 잘 안될 수 있기 때문에 Feature Scaling 과정을 거쳤다.

$X_{original}$ : 원본 데이터

$X_{scaled} = \frac{X_{orginal} - X_{min}}{X_{max} - X_{min}}$

해당 과정을 거친 scaled 데이터는 0~1 사이의 일정한 범위를 가진 값으로 변화하므로, 더욱 정확한 분석이 가능하다.

### 4.2 Cluster 개수 판단

적절한 cluster의 수는 inertia 값을 통해 결정할 수 있다. inertia 값은 K-means 모델을 통한 cluster 형성 이후, Centroid까지의 거리를 합산한 값이다. 그러므로 inertia 값이 작을수록 clustering이 잘 되었다고 볼 수 있으며, cluster의 개수 별로 inerita 값을 구해 적절한 cluster 수를 결정한다.

<center>
<img src="https://github.com/JadenHeo/LOL-user-clustering/blob/main/graph/inertia_10.png" width="600" height="400"/>
</center>

cluster의 개수가 많으면 많을수록 inertia의 값은 당연히 줄어들겠지만, 과도하게 많아지면 cluster를 나누는 의미 자체가 퇴색되므로 좋지 않다. **inertia 값이 k=2 → 3으로 바뀔 때 급격히 감소**하고, 이후에는 감소 폭이 크지 않은 것을 고려해 **클러스터의 수를 3개로 결정**했다.

### 4.3 K-means 클러스터링

<table>
  <tr>
    <td><img alt="" src="https://github.com/JadenHeo/LOL-user-clustering/blob/main/graph/3klusters_10.png" /></td><td><img alt="" src="https://github.com/JadenHeo/LOL-user-clustering/blob/main/graph/3klusters_50.png" /></td>
  <tr>
</table>

다차원의 그래프를 그려서 보기는 힘들기 때문에, 간략히 2차원 그래프를 통해 군집된 소환사들을 관찰할 수 있었다. 개인적으로 플레이어의 플레이 스타일에 따라 *데스, 챔피언에게 가한 피해량*이 달라질 것이라 생각해 두 데이터를 기준으로 그래프를 그려 군집을 관찰했는데, 육안으로 겹치는 부분이 많아 확연한 구분이 힘들었다. 물론 해당 분석에는 19개의 Feature를 고려했기 때문에, 클러스터링 자체가 실패했다고 보기는 어렵다. 그래프 상에서 클러스터들의 특징을 관찰하긴 어려웠기 때문에, 각 클러스터의 무게중심값을 출력해서 어떤 집단을 대표하는지 분석했다. 해당 분석을 통해 도출된 Centroid의 값은 다음과 같다.

```python
# Cluster 1 Centroid
"kills": 0.38429,	"deaths": 0.39248, "assists": 0.32272, "champlevel": 0.53626,	"totaldamagedealt": 0.34694,
"totaldamagedealttochampions": 0.37245,	"damagedealttoobjectives": 0.45504,	"damagedealttoturrets": 0.06215,
"totaldamagetaken": 0.50963, "neutralminionskilledteamjungle": 0.56534,	"neutralminionskilledenemyjungle": 0.28493,
"neutralminionskilled": 0.58143, "totalminionskilled": 0.19145,	"goldearned": 0.47968, "goldspent": 0.49595,
"wardsplaced": 0.14561,	"wardskilled": 0.21979,	"visionwardsboughtingame": 0.23694,	"visionscore": 0.20989

# Cluster 2 Centroid
"kills": 0.33927,	"deaths": 0.39008, "assists": 0.26495, "champlevel": 0.55362, "totaldamagedealt": 0.27906,
"totaldamagedealttochampions": 0.41643, "damagedealttoobjectives": 0.18521, "damagedealttoturrets": 0.1362,
"totaldamagetaken": 0.36501, "neutralminionskilledteamjungle": 0.071, "neutralminionskilledenemyjungle": 0.06476,
"neutralminionskilled": 0.08197, "totalminionskilled": 0.66969, "goldearned": 0.48081, "goldspent": 0.49993,
"wardsplaced": 0.17915, "wardskilled": 0.15405, "visionwardsboughtingame": 0.14748, "visionscore": 0.16159

# Cluster 3 Centroid
"kills": 0.14816, "deaths": 0.37651, "assists": 0.47645, "champlevel": 0.25364, "totaldamagedealt": 0.07052,
"totaldamagedealttochampions": 0.18533, "damagedealttoobjectives": 0.06981, "damagedealttoturrets": 0.04654,
"totaldamagetaken": 0.24677, "neutralminionskilledteamjungle": 0.02261, "neutralminionskilledenemyjungle": 0.01341,
"neutralminionskilled": 0.02684, "totalminionskilled": 0.16218, "goldearned": 0.17631, "goldspent": 0.18525,
"wardsplaced": 0.48672, "wardskilled": 0.32318, "visionwardsboughtingame": 0.38538, "visionscore": 0.46504
```

- 1번 클러스터
    - *중립 몬스터 처치, 적 정글 몬스터 처치*가 다른 클러스터에 비해 훨씬 높다. *시야 점수*는 3번 클러스터에 비해 낮지만 2번 클러스터에 비해 높고, *레벨, 챔피언 피해량, 골드*는 3번 클러스터에 비해 높고, 2번 클러스터보다는 소폭 높은 것으로 보아 정글러 포지션의 소환사들로 보인다.
- 2번 클러스터
    - *미니언 처치(cs)*가 다른 클러스터에 비해 확연히 높으며 *레벨, 챔피언 피해량, 골드, 타워 피해량* 등도 3번 클러스터와는 큰 차이를 보이고, 1번 클러스터(정글)보다도 소폭 높다. 이는 탑, 미드, 원거리 딜러 라인을 플레이한 소환사들의 특징으로 보인다.
- 3번 클러스터
    - *킬, 챔피언 레벨, 피해량* 등이 다른 클러스터에 비해 압도적으로 낮고, 반면 *와드 설치, 시야 점수* 등은 높다. 이는 서포터 포지션을 주로 플레이한 소환사들이 모인 클러스터라 생각된다.

가시적으로 좀 더 명확히 나뉜 클러스터를 관찰하기 위해, 클러스터 별로 크게 차이가 나는 Feature인 *중립 몬스터 처치, 미니언 처치*를 기준으로 다시 2차원 그래프를 그렸다.

![3klusters_10_2.png](LOL%20%E1%84%86%E1%85%A2%E1%84%8E%E1%85%B5%20%E1%84%83%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%90%E1%85%A5%E1%84%85%E1%85%B3%E1%86%AF%20%E1%84%90%E1%85%A9%E1%86%BC%E1%84%92%E1%85%A1%E1%86%AB%20%E1%84%8B%E1%85%B2%E1%84%8C%E1%85%A5%20%E1%84%87%E1%85%AE%E1%86%AB%E1%84%89%E1%85%A5%E1%86%A8%205d6671b6ef174a6d8881369ac90e7abc/3klusters_10_2.png)

![3klusters_50_2.png](LOL%20%E1%84%86%E1%85%A2%E1%84%8E%E1%85%B5%20%E1%84%83%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%90%E1%85%A5%E1%84%85%E1%85%B3%E1%86%AF%20%E1%84%90%E1%85%A9%E1%86%BC%E1%84%92%E1%85%A1%E1%86%AB%20%E1%84%8B%E1%85%B2%E1%84%8C%E1%85%A5%20%E1%84%87%E1%85%AE%E1%86%AB%E1%84%89%E1%85%A5%E1%86%A8%205d6671b6ef174a6d8881369ac90e7abc/3klusters_50_2.png)

가설에 따라 클러스터가 소환사의 플레이 스타일에 따라 나눠질 것이라 예상했지만, 오히려 소환사가 주로 플레이한 포지션에 따라 클러스터가 나뉘는 것을 확인했다. 생각해 본 가설 검증 실패의 요인은 다음 두 가지다.

1. 소환사의 플레이 스타일 차이가 플레이어 스탯(선택된 19개의 Feature)에 영향을 주지 않음
2. 선정된 19개의 Feature가 **소환사의 플레이 스타일보다 소환사가 플레이한 포지션에 훨씬 더 큰 영향을 받아** 플레이 스타일 차이가 가려짐

1번 원인을 살펴보면, 실제 게임을 진행하다 보면 소환사가 게임에 임하는 플레이 스타일이 Feature에 아무런 영향을 주지 않는다는 것은 앞서 진행한 한 번의 분석으로 단정 짓기 어려웠다. 따라서 2번 원인을 주 실패 요인으로 생각하고, 방금 전 클러스터링에 소환사가 플레이한 포지션이 지대한 영향을 주는 것으로 판단했다. 따라서 문제 해결을 위해서는 같은 포지션에 있는 플레이어들끼리 동일한 분석을 진행하기로 했다. 예를 들어 MID 포지션에서 플레이한 결과만을 가지고 소환사들을 분석한다면, 좀 더 개선된 결과를 얻을 수 있을 것이라 생각했다. 가장 빠른 방법으로, 지금 결과로 나온 3개의 클러스터가 이미 어느 정도 포지션들을 나눠주고 있기 때문에, 해당 분석에서 같은 클러스터로 분류된 소환사를 다시 한번 분석해보기로 했다.

![inertia_10_cluster.png](LOL%20%E1%84%86%E1%85%A2%E1%84%8E%E1%85%B5%20%E1%84%83%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%90%E1%85%A5%E1%84%85%E1%85%B3%E1%86%AF%20%E1%84%90%E1%85%A9%E1%86%BC%E1%84%92%E1%85%A1%E1%86%AB%20%E1%84%8B%E1%85%B2%E1%84%8C%E1%85%A5%20%E1%84%87%E1%85%AE%E1%86%AB%E1%84%89%E1%85%A5%E1%86%A8%205d6671b6ef174a6d8881369ac90e7abc/inertia_10_cluster.png)

![2klusters_10_cluster.png](LOL%20%E1%84%86%E1%85%A2%E1%84%8E%E1%85%B5%20%E1%84%83%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%90%E1%85%A5%E1%84%85%E1%85%B3%E1%86%AF%20%E1%84%90%E1%85%A9%E1%86%BC%E1%84%92%E1%85%A1%E1%86%AB%20%E1%84%8B%E1%85%B2%E1%84%8C%E1%85%A5%20%E1%84%87%E1%85%AE%E1%86%AB%E1%84%89%E1%85%A5%E1%86%A8%205d6671b6ef174a6d8881369ac90e7abc/2klusters_10_cluster.png)

inertia 그래프를 살펴보면, 클러스터의 수가 2일 때, 그리고 5일 때 기울기의 변화가 관찰되었다. elbow의 각이 2일 때 두드러졌기 때문에, 2개의 클러스터로 분석을 진행했고, *데스-챔피언 피해량* 그래프에서 위와 같은 결과를 보여줬다. 2개의 Centroid는 다음과 같다.

```python
# Cluster 1 Centroid
"kills": 0.28808, "deaths": 0.38098, "assists": 0.28084, "champlevel": 0.50806, "totaldamagedealt": 0.24844,
"totaldamagedealttochampions": 0.36709, "damagedealttoobjectives": 0.1585, "damagedealttoturrets": 0.10961, 
"totaldamagetaken": 0.35072, "neutralminionskilledteamjungle": 0.06688, "neutralminionskilledenemyjungle": 0.04818,
"neutralminionskilled": 0.07439, "totalminionskilled": 0.61523, "goldearned": 0.41632, "goldspent": 0.43528,
"wardsplaced": 0.19341, "wardskilled": 0.1579, "visionwardsboughtingame": 0.16592, "visionscore": 0.17572

# Cluster 2 Centroid
"kills": 0.39464, "deaths": 0.39994, "assists": 0.24778, "champlevel": 0.60286, "totaldamagedealt": 0.31216,
"totaldamagedealttochampions": 0.46979, "damagedealttoobjectives": 0.21409, "damagedealttoturrets": 0.16496,
"totaldamagetaken": 0.38045, "neutralminionskilledteamjungle": 0.07545, "neutralminionskilledenemyjungle": 0.08268,
"neutralminionskilled": 0.09018, "totalminionskilled": 0.72855, "goldearned": 0.55054, "goldspent": 0.56984,
"wardsplaced": 0.16376, "wardskilled": 0.14989, "visionwardsboughtingame": 0.12757, "visionscore": 0.14634
```

게임을 10판 이상 플레이한 소환사에 대해 분석했기 때문에 승패 여부나 개인의 성장이 특별히 제한된 경우 등의 특별한 게임에 대한 데이터가 아니라고 가정하고 각 클러스터의 Centroid 값을 해석했다.

- 1번 클러스터
    - 2번 클러스터에 비해 *킬, 레벨, 챔피언 피해량, 받은 피해량, 타워 피해량, 골드*가 낮다. 반면 ***골드*가 낮은 것에 비해 *와드 설치, 제거, 제어와드 구매, 시야 점수*가 높다**. 이는 **상대적으로 전투를 통한 개인의 성장보다, 꼼꼼한 시야 플레이를 통해 게임을 승리하고자 하는 성향의 소환사**로 보인다.
- 2번 클러스터
    - 1번 클러스터와 **반대로, 팀적인 부분에서 필요한 시야 플레이보다 개인의 성장과 획득 골드를 바탕으로 게임을 승리하는 성향의 소환사**로 보인다.

# 결론

## 분석 피드백

개인적인 기준에 따라 선정한 19개의 Feature를 이용해 진행한 클러스터링 분석을 요약하자면 다음과 같다.

- 1차 K-means 클러스터링 시도에서는 선정된 Feature가 소환사의 플레이 포지션에 영향을 많이 받아서 포지션과 별개로 어떤 스타일로 게임을 플레이하는지에 대한 분류를 제대로 이뤄내지 못했다.
- 따라서 2차 클러스터링에서는, 1차 클러스터링에서 구분된 각 클러스터가 특정 포지션에서 주로 플레이한 소환사들을 나눴다고 가정하고, 특정 클러스터에 속한, 즉 같은 포지션에서 플레이한 소환사들끼리 다시 한번 클러스터링 해서 소환사의 플레이 스타일을 찾을 수 있었다.
- 2차 클러스터링의 결과로 **성장보다 시야 플레이에 집중하는 소환사**, 반대로 **개인의 성장과 전투에 집중하는 소환사** 그룹으로 나눠짐을 확인할 수 있었다. 이를 일상적인 표현으로 말하자면 **'전투 vs 운영'**이나, **'이기적 vs 이타적'** 등의 용어로 표현할 수 있다.

## 향후 과제

제한된 시간에 수많은 데이터를 파악하고, 분석 및 해석을 했기 때문에 개선의 여지가 있는 점들이 있었다. 더욱 정확한 분석을 위해 이뤄져야 할 개선점은 대표적으로 4가지 정도가 있다고 생각했다.

1. 클러스터 개수의 선정을 단순히 inertia 값의 elbow를 찾는 과정으로 진행했는데, 사실 **클러스터의 적정 개수를 판단하는 다른 방법도 존재**한다. 클러스터의 개수에 따른 silhouette score를 측정해서 다른 클러스터끼리는 떨어져 있고, 같은 클러스터 내의 데이터는 뭉쳐있는 정도를 계산하고 이를 참고해 적정 클러스터의 수를 결정할 수도 있다. 이번 분석에는 적용해보지 못했지만, 향후 정확한 분석을 위해 사용해볼 필요가 있는 평가 방법이라 생각된다.
2. 1차 분석에서 포지션별로 소환사가 나눠진 것을 관찰한 후에, 단순히 같은 클러스터에 속한 소환사를 대상으로 다시 분석을 진행했다. 하지만 1차 분석에서 나눠진 클러스터가 소환사의 플레이 포지션을 제대로 나누고 있는지에 대한 신뢰도가 검증되지 않았기 때문에, 2차 분석에서 얻은 결과에 대한 신뢰도에 대해서도 의문점을 가질 수 있다고 생각했다. 이는 Riot에서 자체적으로 계산한 *lane* 데이터가 87.5%라는 상당히 높은 신뢰도를 보장했기 때문에, 이를 바탕으로 **각 *lane* 별 평균 Feature 값과 해당 lane을 플레이한 소환사의 Feature 값을 비교하고, 비교된 값을 바탕으로 클러스터링**을 진행한다면 더욱 신뢰도 있는 결과를 도출할 수 있을 것으로 보인다.
3. 이번 분석에서는 K-means 클러스터링 기법을 활용했는데, K-means도 당연히 만능이 아니기 때문에 초기 클러스터 개수를 설정해야 한다던가, Centroid가 local optimum에 빠져서 최적의 결과가 나오지 않을 수 있는 등의 단점이 존재한다고 알고 있다. **비지도 학습 기반의 다른 클러스터링 기법들 역시 활용해서 분석해보고, 이번 클러스터링의 결과와 비교 분석하면서 어떤 기법이 더 적절할지 알아보는 과정**도 필요할 것이라 생각한다.
4. 선정된 19개의 Feature가 게임에서 어떤 의미를 가지는지 생각해 본다면, 필연적으로 플레이한 포지션, 챔피언, 아이템, 룬 등에 따라 그 값이 영향을 받을 수밖에 없다. 2번에서 언급한 포지션 외에도, **플레이한 챔피언과 구매한 아이템, 선택한 룬들의 index를 바탕으로 해당 챔피언, 아이템, 룬에 대해 분석된 정보를 Feature에 넣어 분석**해보면 또 다른 결과가 나올 수 있지 않을까 하고 기대한다.

## 플레이 스타일 분류에 대한 기대

롤을 플레이하는 소환사 본인은 본인이 어떤 스타일로 게임하고 있는지 객관적으로 판단할 능력이 없는 경우가 많다. 이번 분석을 시작으로 더욱 신뢰성 있는 다양한 데이터와 분석 기법 등을 활용해 소환사가 어떤 스타일의 플레이어인지 분석이 가능하다면, **해당 소환사의 승률을 높여줄 챔피언, 아이템, 룬 등의 데이터를 제공해 줄 수 있을 것**으로 보인다. 한 가지 챔피언을 진득하게 플레이하는 장인 유저들도 존재하지만, 상황에 맞게 그때그때 플레이할 챔피언을 선택해 게임하는 유저들 역시 굉장히 많다. 유저 개인별 맞춤 추천이 가능하다면, 너무 한 가지 챔피언만 플레이하는 유저에겐 또 다른 챔피언을, 다양한 챔피언을 플레이하는 유저에겐 더 어울리는 챔피언을 추천해 주는 식의 서비스가 가능할 것으로 기대된다.

또한 추가적으로 개인의 플레이 스타일을 데이터 분석을 통해 규정할 수 있다면, **어떤 스타일의 사람들이 모여 플레이할 때 좋은 결과가 있는지에 대한 분석 역시 가능할 것**이다. 그렇다면 이는 작게는 어떤 친구들과 함께 랭크 게임을 플레이하면 높은 승률이 나오는지를, 크게는 **프로팀을 운영하는 입장에서 어떤 선수가 우리 팀에 맞는 최적의 선수인지를 판단하는 데에 큰 도움을 줄 수 있을 것**이라고 생각한다.