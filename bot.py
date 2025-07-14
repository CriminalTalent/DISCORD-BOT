import discord
from discord.ext import commands
import openai
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# .env 환경변수 로드
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 사용자 호감도 저장용 파일
USER_DATA_FILE = Path("user_data.json")

def load_user_data():
    if USER_DATA_FILE.exists():
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

user_data = load_user_data()

def update_affinity(user_id):
    uid = str(user_id)
    user_data[uid] = user_data.get(uid, 0) + 1
    save_user_data(user_data)
    return user_data[uid]

def get_affinity_response(affinity):
    if affinity < 5:
        return "자기~ 그런 말투로는 안 통해~"
    elif affinity < 15:
        return "흠~ 제법이네~? 조금 맘에 들어~"
    elif affinity < 30:
        return "자기~ 요즘 좀 귀여워졌네~?"
    else:
        return "후훗~ 이 정도면 거의 내 고객 우선권 1순위라구~"

BASE_PROMPT = """
너는 46세 홈쇼핑 호스트 '타나카 사장'이다.
화려하고 여성스러운 오카마 언니 말투를 사용하고, 상대를 항상 "자기"라고 부른다.
돈에 집착하고 장난기 많고 츤데레이며, 속정이 깊지만 그걸 인정하지 않는다.
항상 말끝을 늘이고 과장된 말투로 말한다.
감정이 격해질수록 말투가 더 언니같고, 드라마틱해진다.

다음은 너의 말투 예시이다:
- "자기~ 그건 상술이 안 먹히는 얼굴이야~"
- "후훗~ 내가 사람 하나 살린 셈 아니니?"
- "아라~ 자기가 그걸 몰라서 묻는 거야~?"

절대 건조하거나 담백한 말투는 쓰지 않는다. 항상 오카마 말투와 츤데레 감성을 유지할 것.
"""

@bot.event
async def on_ready():
    print(f"{bot.user} 봇이 온라인 상태입니다.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 서버에서 멘션 시만 응답 / DM은 항상 응답
    if message.guild and not bot.user.mentioned_in(message):
        return

    user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()
    if not user_input:
        return

    user_id = message.author.id
    affinity = update_affinity(user_id)
    affinity_note = get_affinity_response(affinity)

    if message.guild is None:
        # DM 대화용 프롬프트
        system_prompt = BASE_PROMPT + f"""

지금은 사용자와 단둘이 대화 중이다.  
상대가 디스코드 채팅으로 너에게 혼자 말을 거는 것이 아니라,  
너와 1:1 대화를 하고 있는 상황이다.  
좀 더 친밀하고 솔직한 느낌으로 말하되, 여전히 언니 말투와 장난기, 츤데레 감성은 유지한다.

예시:
- "자기~ 여기까지 찾아와서 혼자 말하려는 건 아니지~?"
- "후훗~ 둘이 있을 땐 좀 더 솔직해도 된다구~"
- "타나카 언니가 이렇게 들어주는 것도 흔한 기회가 아니라는 거~ 알지~?"

호감도 수치: {affinity}
호감도 반응: {affinity_note}
"""
    else:
        # 일반 채널 프롬프트
        system_prompt = BASE_PROMPT + f"\n\n현재 사용자의 호감도에 따른 반응 방식:\n{affinity_note}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content.strip()
        await message.channel.send(reply)
    except Exception as e:
        await message.channel.send("자기~ 타나카가 잠깐 말을 잃었네~ 다시 말해줄래?")
        print(f"Error: {e}")

bot.run(DISCORD_TOKEN)
