# League of Legends Riot API 정리

확인일: 2026-06-12

공식 문서:

- API Reference: https://developer.riotgames.com/apis
- League of Legends Docs: https://developer.riotgames.com/docs/lol
- Developer Portal Docs: https://developer.riotgames.com/docs/portal

## 공통 호출 방식

Riot API는 라우팅 값이 들어간 호스트로 호출한다.

```text
https://{routing}.api.riotgames.com/{api-path}
```

일반 Riot API Key 호출은 `X-Riot-Token` 헤더를 사용한다.

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://kr.api.riotgames.com/lol/status/v4/platform-data"
```

RSO(Riot Sign On) 기반 호출은 OAuth access token을 `Authorization: Bearer` 헤더로 보낸다.

```bash
curl \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  "https://asia.api.riotgames.com/riot/account/v1/accounts/me"
```

## 라우팅

LoL API는 API 성격에 따라 플랫폼 라우팅과 지역 라우팅을 나누어 쓴다.

| 구분 | 예시 | 주 사용처 |
| --- | --- | --- |
| 플랫폼 라우팅 | `kr.api.riotgames.com` | 소환사, 리그, 관전, 서버 상태 |
| 지역 라우팅 | `asia.api.riotgames.com` | 계정, 매치 히스토리 |

KR 서버 데이터를 다룰 때는 보통 아래 조합을 쓴다.

| 설정 | 값 |
| --- | --- |
| 플랫폼 | `kr` |
| 지역 | `asia` |

주요 플랫폼 호스트:

| 플랫폼 | 호스트 |
| --- | --- |
| KR | `kr.api.riotgames.com` |
| JP1 | `jp1.api.riotgames.com` |
| NA1 | `na1.api.riotgames.com` |
| EUW1 | `euw1.api.riotgames.com` |
| EUN1 | `eun1.api.riotgames.com` |
| BR1 | `br1.api.riotgames.com` |

주요 지역 호스트:

| 지역 | 호스트 |
| --- | --- |
| ASIA | `asia.api.riotgames.com` |
| AMERICAS | `americas.api.riotgames.com` |
| EUROPE | `europe.api.riotgames.com` |
| SEA | `sea.api.riotgames.com` |

## API Key 주의사항

- 개발자 포털에서 개발용 API Key를 발급받는다.
- 개발용 API Key는 임시 키라 주기적으로 갱신해야 한다.
- API Key는 코드나 공개 저장소에 넣지 않는다.
- API Key는 이 프로젝트의 `secrets/keys.yaml`처럼 Git에서 제외된 파일에 둔다.
- 401은 인증 정보 누락, 403은 잘못된 키/권한/경로 문제, 429는 rate limit 초과로 보면 된다.
- 429 응답을 받으면 `Retry-After` 헤더에 맞춰 대기한다.

## LoL 데이터 수집 기본 흐름

데이터베이스 구축 기준으로 가장 기본적인 수집 순서는 아래와 같다.

1. Riot ID로 PUUID 조회
2. PUUID로 LoL 소환사 정보 조회
3. Summoner ID로 랭크 정보 조회
4. PUUID로 Match ID 목록 조회
5. Match ID로 매치 상세 조회
6. Match ID로 타임라인 조회

## 1. Riot ID로 PUUID 조회

Riot ID는 `gameName`과 `tagLine` 조합이다. 예: `Faker#KR1`

Account API는 지역 라우팅을 사용한다.

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
```

예시:

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Faker/KR1"
```

주요 응답:

| 필드 | 의미 |
| --- | --- |
| `puuid` | 전역 플레이어 ID |
| `gameName` | Riot ID 이름 |
| `tagLine` | Riot ID 태그 |

PUUID로 Riot ID를 다시 조회할 수도 있다.

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://asia.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
```

## 2. PUUID로 소환사 정보 조회

Summoner API는 플랫폼 라우팅을 사용한다.

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}"
```

주요 응답:

| 필드 | 의미 |
| --- | --- |
| `id` | 암호화된 Summoner ID. League API에서 사용 |
| `accountId` | 암호화된 Account ID |
| `puuid` | 전역 플레이어 ID |
| `profileIconId` | 프로필 아이콘 ID |
| `summonerLevel` | 소환사 레벨 |

Summoner ID로도 조회할 수 있다.

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://kr.api.riotgames.com/lol/summoner/v4/summoners/{encryptedSummonerId}"
```

주의: Riot은 소환사 이름보다 Riot ID와 PUUID 기반 조회를 권장한다. 소환사 이름 기반 엔드포인트는 deprecated 상태로 보고 신규 구현에서는 피한다.

## 3. 랭크 정보 조회

League API는 플랫폼 라우팅을 사용한다.

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{encryptedSummonerId}"
```

주요 응답:

| 필드 | 의미 |
| --- | --- |
| `queueType` | 랭크 큐 종류 |
| `tier` | 티어 |
| `rank` | 디비전 |
| `leaguePoints` | LP |
| `wins` | 승 |
| `losses` | 패 |
| `hotStreak` | 연승 여부 |
| `veteran` | 베테랑 여부 |
| `freshBlood` | 신규 진입 여부 |
| `inactive` | 휴면 여부 |

주요 큐 값:

| 값 | 의미 |
| --- | --- |
| `RANKED_SOLO_5x5` | 솔로 랭크 |
| `RANKED_FLEX_SR` | 자유 랭크 |

상위권 리그 조회:

```bash
curl -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"

curl -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://kr.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5"

curl -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://kr.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5"
```

티어/디비전 단위 조회:

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/DIAMOND/I?page=1"
```

## 4. Match ID 목록 조회

Match API는 지역 라우팅을 사용한다.

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20"
```

자주 쓰는 쿼리 파라미터:

| 파라미터 | 의미 |
| --- | --- |
| `start` | 가져오기 시작 위치 |
| `count` | 가져올 매치 수 |
| `queue` | 큐 ID 필터 |
| `type` | `ranked`, `normal`, `tourney`, `tutorial` 등 |
| `startTime` | Unix timestamp 초 단위 시작 시각 |
| `endTime` | Unix timestamp 초 단위 종료 시각 |

예시:

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=100"
```

## 5. 매치 상세 조회

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}"
```

주요 데이터:

| 위치 | 의미 |
| --- | --- |
| `metadata.matchId` | Match ID |
| `metadata.participants` | 참여자 PUUID 목록 |
| `info.gameCreation` | 게임 생성 시각 |
| `info.gameDuration` | 게임 길이 |
| `info.gameMode` | 게임 모드 |
| `info.gameType` | 게임 타입 |
| `info.gameVersion` | 게임 버전 |
| `info.mapId` | 맵 ID |
| `info.queueId` | 큐 ID |
| `info.participants` | 플레이어별 챔피언, 룬, 아이템, KDA, 승패 등 |
| `info.teams` | 팀별 밴, 오브젝트, 승패 등 |

DB 저장 시 기본 키 후보:

| 테이블 | 기본 키 후보 |
| --- | --- |
| match | `matchId` |
| participant | `matchId + puuid` |
| team | `matchId + teamId` |
| ban | `matchId + teamId + pickTurn` |

## 6. 매치 타임라인 조회

```bash
curl \
  -H "X-Riot-Token: ${RIOT_API_KEY}" \
  "https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}/timeline"
```

타임라인은 분 단위 `frames`와 이벤트를 제공한다.

자주 보는 이벤트:

| 이벤트 | 의미 |
| --- | --- |
| `CHAMPION_KILL` | 챔피언 처치 |
| `ELITE_MONSTER_KILL` | 드래곤, 전령, 바론 등 오브젝트 처치 |
| `BUILDING_KILL` | 포탑, 억제기 등 건물 파괴 |
| `ITEM_PURCHASED` | 아이템 구매 |
| `ITEM_SOLD` | 아이템 판매 |
| `ITEM_UNDO` | 아이템 구매 되돌리기 |
| `SKILL_LEVEL_UP` | 스킬 레벨업 |
| `LEVEL_UP` | 챔피언 레벨업 |
| `WARD_PLACED` | 와드 설치 |
| `WARD_KILL` | 와드 제거 |

## LoL API 기능별 요약

### 계정과 ID

| API | 기능 | 대표 호출 |
| --- | --- | --- |
| `account-v1` | Riot ID로 PUUID 조회 | `GET /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}` |
| `account-v1` | PUUID로 Riot ID 조회 | `GET /riot/account/v1/accounts/by-puuid/{puuid}` |
| `account-v1` | RSO 로그인 사용자 조회 | `GET /riot/account/v1/accounts/me` |

### 소환사

| API | 기능 | 대표 호출 |
| --- | --- | --- |
| `summoner-v4` | PUUID로 소환사 조회 | `GET /lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}` |
| `summoner-v4` | Summoner ID로 소환사 조회 | `GET /lol/summoner/v4/summoners/{encryptedSummonerId}` |
| `summoner-v4` | 소환사 이름으로 조회 | `GET /lol/summoner/v4/summoners/by-name/{summonerName}` |

### 랭크와 리그

| API | 기능 | 대표 호출 |
| --- | --- | --- |
| `league-v4` | 소환사의 랭크 엔트리 조회 | `GET /lol/league/v4/entries/by-summoner/{encryptedSummonerId}` |
| `league-v4` | 챌린저 리그 조회 | `GET /lol/league/v4/challengerleagues/by-queue/{queue}` |
| `league-v4` | 그랜드마스터 리그 조회 | `GET /lol/league/v4/grandmasterleagues/by-queue/{queue}` |
| `league-v4` | 마스터 리그 조회 | `GET /lol/league/v4/masterleagues/by-queue/{queue}` |
| `league-v4` | 티어/디비전별 엔트리 조회 | `GET /lol/league/v4/entries/{queue}/{tier}/{division}` |
| `league-v4` | League ID로 리그 조회 | `GET /lol/league/v4/leagues/{leagueId}` |
| `league-exp-v4` | 대량 랭크 엔트리 조회 | `GET /lol/league-exp/v4/entries/{queue}/{tier}/{division}` |

### 매치

| API | 기능 | 대표 호출 |
| --- | --- | --- |
| `match-v5` | PUUID로 Match ID 목록 조회 | `GET /lol/match/v5/matches/by-puuid/{puuid}/ids` |
| `match-v5` | 매치 상세 조회 | `GET /lol/match/v5/matches/{matchId}` |
| `match-v5` | 매치 타임라인 조회 | `GET /lol/match/v5/matches/{matchId}/timeline` |
| `lol-rso-match-v1` | RSO 권한 기반 매치 조회 | RSO access token 필요 |

### 챔피언 숙련도

| API | 기능 | 대표 호출 |
| --- | --- | --- |
| `champion-mastery-v4` | 전체 챔피언 숙련도 조회 | `GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}` |
| `champion-mastery-v4` | 특정 챔피언 숙련도 조회 | `GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}/by-champion/{championId}` |
| `champion-mastery-v4` | 상위 숙련도 챔피언 조회 | `GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}/top` |
| `champion-mastery-v4` | 총 숙련도 점수 조회 | `GET /lol/champion-mastery/v4/scores/by-puuid/{encryptedPUUID}` |

### 챔피언 로테이션

| API | 기능 | 대표 호출 |
| --- | --- | --- |
| `champion-v3` | 무료 챔피언 로테이션 조회 | `GET /lol/platform/v3/champion-rotations` |

### 도전과제

| API | 기능 | 대표 호출 |
| --- | --- | --- |
| `lol-challenges-v1` | 전체 도전과제 설정 | `GET /lol/challenges/v1/challenges/config` |
| `lol-challenges-v1` | 전체 도전과제 퍼센타일 | `GET /lol/challenges/v1/challenges/percentiles` |
| `lol-challenges-v1` | 특정 도전과제 설정 | `GET /lol/challenges/v1/challenges/{challengeId}/config` |
| `lol-challenges-v1` | 특정 도전과제 리더보드 | `GET /lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/{level}` |
| `lol-challenges-v1` | 특정 도전과제 퍼센타일 | `GET /lol/challenges/v1/challenges/{challengeId}/percentiles` |
| `lol-challenges-v1` | 플레이어 도전과제 데이터 | `GET /lol/challenges/v1/player-data/{puuid}` |

### Clash

| API | 기능 | 대표 호출 |
| --- | --- | --- |
| `clash-v1` | 소환사의 Clash 플레이어 정보 | `GET /lol/clash/v1/players/by-summoner/{summonerId}` |
| `clash-v1` | 팀 조회 | `GET /lol/clash/v1/teams/{teamId}` |
| `clash-v1` | 전체 토너먼트 조회 | `GET /lol/clash/v1/tournaments` |
| `clash-v1` | 팀 기준 토너먼트 조회 | `GET /lol/clash/v1/tournaments/by-team/{teamId}` |
| `clash-v1` | 토너먼트 ID 조회 | `GET /lol/clash/v1/tournaments/{tournamentId}` |

### 관전과 상태

| API | 기능 | 대표 호출 |
| --- | --- | --- |
| `spectator-v5` | 현재 게임 관전 정보 | `GET /lol/spectator/v5/active-games/by-summoner/{encryptedPUUID}` |
| `spectator-v5` | 추천 게임 목록 | `GET /lol/spectator/v5/featured-games` |
| `lol-status-v4` | 서버 상태와 공지 조회 | `GET /lol/status/v4/platform-data` |

### 토너먼트

토너먼트 API는 승인된 키와 별도 정책 확인이 필요하다. 테스트에는 `tournament-stub-v5`, 실제 운영에는 `tournament-v5`를 사용한다.

| API | 기능 | 대표 호출 |
| --- | --- | --- |
| `tournament-stub-v5` | 테스트 Provider 생성 | `POST /lol/tournament-stub/v5/providers` |
| `tournament-stub-v5` | 테스트 Tournament 생성 | `POST /lol/tournament-stub/v5/tournaments` |
| `tournament-stub-v5` | 테스트 코드 생성 | `POST /lol/tournament-stub/v5/codes` |
| `tournament-v5` | Provider 생성 | `POST /lol/tournament/v5/providers` |
| `tournament-v5` | Tournament 생성 | `POST /lol/tournament/v5/tournaments` |
| `tournament-v5` | 토너먼트 코드 생성 | `POST /lol/tournament/v5/codes` |
| `tournament-v5` | 토너먼트 코드 조회 | `GET /lol/tournament/v5/codes/{tournamentCode}` |
| `tournament-v5` | 토너먼트 코드 수정 | `PUT /lol/tournament/v5/codes/{tournamentCode}` |
| `tournament-v5` | 로비 이벤트 조회 | `GET /lol/tournament/v5/lobby-events/by-code/{tournamentCode}` |

## Data Dragon

Data Dragon은 챔피언, 아이템, 룬, 소환사 주문, 프로필 아이콘 같은 LoL 정적 데이터와 이미지 자산을 제공한다. 일반 Riot API Key가 필요 없다.

최신 버전 목록:

```bash
curl "https://ddragon.leagueoflegends.com/api/versions.json"
```

한국어 챔피언 목록:

```bash
curl "https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/champion.json"
```

한국어 아이템 목록:

```bash
curl "https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/item.json"
```

한국어 소환사 주문 목록:

```bash
curl "https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/summoner.json"
```

큐, 맵, 게임 모드 상수:

```text
https://static.developer.riotgames.com/docs/lol/queues.json
https://static.developer.riotgames.com/docs/lol/maps.json
https://static.developer.riotgames.com/docs/lol/gameModes.json
https://static.developer.riotgames.com/docs/lol/gameTypes.json
```

## Python 호출 예시

```python
import requests


def riot_get(url: str, api_key: str, params: dict | None = None) -> dict:
    response = requests.get(
        url,
        headers={"X-Riot-Token": api_key},
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


account = riot_get(
    "https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Faker/KR1",
    api_key,
)

summoner = riot_get(
    f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{account['puuid']}",
    api_key,
)

rank_entries = riot_get(
    f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner['id']}",
    api_key,
)

match_ids = riot_get(
    f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{account['puuid']}/ids",
    api_key,
    params={"type": "ranked", "start": 0, "count": 20},
)
```

## 이 프로젝트 기준 최소 구현 순서

1. `config.yaml`에 `platform: kr`, `region: asia` 같은 지역 설정을 둔다.
2. `secrets/keys.yaml`에서 Riot API Key를 읽는다.
3. Riot ID를 입력받아 `account-v1`로 PUUID를 얻는다.
4. `summoner-v4`로 Summoner ID, 레벨, 아이콘을 저장한다.
5. `league-v4`로 티어, LP, 승패를 저장한다.
6. `match-v5`로 Match ID 목록을 저장한다.
7. 매치 상세와 타임라인을 별도 테이블로 저장한다.

최소 수집 테이블 후보:

| 테이블 | 주요 값 |
| --- | --- |
| `account` | `puuid`, `gameName`, `tagLine` |
| `summoner` | `puuid`, `summonerId`, `profileIconId`, `summonerLevel` |
| `rank_entry` | `summonerId`, `queueType`, `tier`, `rank`, `leaguePoints`, `wins`, `losses` |
| `match` | `matchId`, `gameCreation`, `gameDuration`, `gameVersion`, `queueId` |
| `match_participant` | `matchId`, `puuid`, `championId`, `teamId`, `win`, `kills`, `deaths`, `assists` |
| `match_team` | `matchId`, `teamId`, `win`, `objectives` |
| `match_timeline_event` | `matchId`, `timestamp`, `type`, `participantId`, `raw_json` |
