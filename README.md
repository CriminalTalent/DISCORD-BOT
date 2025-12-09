# 디스코드 RPG 봇

디스코드 채널에서 갈레온(화폐) 관리, 아이템 거래, 도박, 타로 등을 즐길 수 있는 RPG 봇입니다.
구글 시트를 데이터베이스로 사용합니다.

## 주요 기능

### 경제 시스템
- !등록 <이름> - 게임 등록 (초기 갈레온 100개)
- !주머니 - 소지품 확인
- !상점 - 판매 중인 아이템 목록
- !구매 <아이템> - 아이템 구매
- !사용 <아이템> - 아이템 사용
- !양도 @사용자 <갈레온/아이템> - 갈레온 또는 아이템 양도

### 도박
- !베팅 <금액> - 갈레온 베팅 (배당: -5x ~ +5x, 하루 3번)

### 재미 기능
- !타로 - 타로 카드 뽑기 (78장 풀덱 + 추천)
- !주사위 [면수] - 주사위 굴리기
- !동전 - 동전 던지기
- !yn - YES/NO 답변
- !운세 - 오늘의 운세

### 관리자 명령어
- !갈레온지급 @사용자 <금액> - 갈레온 지급
- !reload - Cog 재로드

## 설치 및 설정

### 1. Python 설치
Python 3.8 이상 필요

```bash
python --version
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 디스코드 봇 생성

1. Discord Developer Portal 접속
   https://discord.com/developers/applications

2. 새 애플리케이션 생성
   - "New Application" 클릭
   - 봇 이름 입력

3. 봇 설정
   - 좌측 메뉴 "Bot" 선택
   - "Add Bot" 클릭
   - MESSAGE CONTENT INTENT 활성화 (필수)
   - SERVER MEMBERS INTENT 활성화 (필수)

4. 토큰 복사
   - "Reset Token" 클릭
   - 토큰 복사 (절대 공유 금지)

5. 봇 초대
   - "OAuth2" → "URL Generator"
   - Scopes: bot
   - Bot Permissions:
     - Send Messages
     - Read Message History
     - Add Reactions
     - Embed Links
   - 생성된 URL로 서버 초대

### 4. 구글 시트 설정

1. Google Cloud Console 접속
   https://console.cloud.google.com

2. 프로젝트 생성

3. API 활성화
   - Google Sheets API
   - Google Drive API

4. 서비스 계정 생성
   - "API 및 서비스" → "사용자 인증 정보"
   - "서비스 계정" 생성
   - JSON 키 다운로드 → credentials.json으로 저장

5. 구글 시트 생성
   - 새 스프레드시트 생성
   - URL에서 ID 복사
   - 서비스 계정 이메일과 편집자 권한으로 공유

### 5. 환경 변수 설정

.env.example을 .env로 복사 후 수정:

```env
DISCORD_TOKEN=your_actual_token_here
GOOGLE_SHEET_ID=your_actual_sheet_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json
TZ=Asia/Seoul
```

### 6. 실행

```bash
python bot.py
```

성공 메시지:
```
[BOT] 로그인 성공: YourBot (ID: 123456789)
[SHEET] 구글 시트 연결 완료
[COG] cogs.economy_cog 로드 완료
[COG] cogs.gambling_cog 로드 완료
[COG] cogs.fun_cog 로드 완료
[BOT] 준비 완료! 명령어 대기 중...
```

## 파일 구조

```
discord_bot_clean/
├── bot.py                   # 메인 봇 파일
├── sheet_manager.py         # 구글 시트 연동
├── cogs/                    # 명령어 모듈
│   ├── __init__.py
│   ├── economy_cog.py       # 경제 명령어
│   ├── gambling_cog.py      # 도박 명령어
│   └── fun_cog.py           # 재미 명령어
├── requirements.txt         # Python 패키지
├── .env.example            # 환경 변수 템플릿
├── .env                    # 환경 변수 (생성 필요)
├── credentials.json        # 구글 인증 (생성 필요)
├── .gitignore
└── README.md
```

## 구글 시트 구조

봇이 자동으로 다음 시트를 생성합니다:

### 사용자 시트
| ID | 이름 | 갈레온 | 아이템 | 메모 | 기숙사 | 마지막베팅날짜 | 베팅횟수 | 출석날짜 | 마지막타로날짜 | 기숙사점수 |

### 아이템 시트
| 아이템명 | 설명 | 가격 | 판매여부 | 사용가능여부 |

### 로그 시트
| 타임스탬프 | 사용자 | 명령어 | 내용 |

## 아이템 추가 방법

구글 시트의 "아이템" 탭에서 직접 추가:

예시:
| 아이템명 | 설명 | 가격 | 판매여부 | 사용가능여부 |
| 마법의 쿠키 | 달콤함이 기분을 좋게 해줍니다 | 10 | TRUE | TRUE |
| 행운의 부적 | 행운이 +10 증가합니다/불운이 물러갑니다 | 50 | TRUE | TRUE |

설명 필드에서 슬래시(/)로 구분하면 사용 시 랜덤으로 하나 선택됩니다.

## 커스터마이징

### 베팅 설정 변경
cogs/gambling_cog.py에서:
- MAX_BETS_PER_DAY: 하루 최대 베팅 횟수
- multiplier = random.randint(-5, 5): 배당률 범위

### 타로 카드 수정
cogs/fun_cog.py의 TAROT_DATA 딕셔너리 수정

## 24시간 실행

### VPS/클라우드
AWS, GCP, Azure, DigitalOcean 등

### PM2 (Node.js 필요)
```bash
npm install -g pm2
pm2 start bot.py --interpreter python3 --name rpg-bot
pm2 save
pm2 startup
```

### Screen (Linux)
```bash
screen -S rpg-bot
python bot.py
# Ctrl+A, D로 분리
```

## 보안 주의사항

절대 Git에 커밋하지 말 것:
- .env
- credentials.json

.gitignore에 포함되어 있습니다.

## 문제 해결

### "구글 시트 연결 실패"
- credentials.json 위치 확인
- 서비스 계정 이메일 공유 확인
- API 활성화 확인

### "MESSAGE CONTENT INTENT 오류"
- Discord Developer Portal에서 Intent 활성화
- 봇 재초대 필요할 수 있음

### "명령어가 작동하지 않음"
- 접두사 확인 (!)
- !도움말 명령어로 사용법 확인

## 라이선스

MIT License
