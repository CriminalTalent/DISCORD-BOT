# cogs/fun_cog.py
# 재미 기능 (타로, 주사위, 동전, YN, 운세)

import discord
from discord.ext import commands
import random
from datetime import datetime
import pytz

class FunCog(commands.Cog, name="재미"):
    """타로, 주사위 등 재미 명령어"""
    
    TAROT_DATA = {
        "THE FOOL": "순수한 마음으로 새로운 모험을 시작할 때라네. 망설이지 말고 발을 내딛게.",
        "THE MAGICIAN": "지금이 바로 손재주를 발휘할 때라네. 가진 걸 믿고 써먹어보게.",
        "THE HIGH PRIESTESS": "겉보다 속을 봐야 할 때라네. 조용히 듣고 관찰하게.",
        "THE EMPRESS": "풍요로움이 넘치는 시기라네. 마음을 열고 주변과 나누게.",
        "THE EMPEROR": "책임감 있게 자리를 지켜야 할 때라네. 네가 중심을 잡아야 하지.",
        "THE HIEROPHANT": "배움에는 끝이 없다네. 전통 속에서 해답을 찾아보게.",
        "THE LOVERS": "선택의 순간이라네. 마음이 진짜 원하는 걸 따라가게.",
        "THE CHARIOT": "의지와 집중으로 돌파해야 할 때라네. 흔들리지 말게.",
        "STRENGTH": "진짜 힘은 온화함에서 나온다네. 조급하지 않게 마음을 다스리게.",
        "THE HERMIT": "혼자 있는 시간 속에 답이 있다네. 등불을 켜고 내면을 들여다보게.",
        "WHEEL OF FORTUNE": "운명의 수레바퀴가 돌다네. 이번엔 바람이 어디로 불지 모르지.",
        "JUSTICE": "공정하게 판단해야 할 때라네. 감정은 잠시 접어두게.",
        "THE HANGED MAN": "잠시 멈춰보게. 다른 각도에서 보면 세상이 달라진다네.",
        "DEATH": "끝이 있어야 새 시작이 있지. 두려워 말고 털고 일어나게.",
        "TEMPERANCE": "균형을 잡아야 한다네. 너무 많지도 적지도 않게 조절하게.",
        "THE DEVIL": "유혹이 다가오네. 하지만 스스로 묶이지 말게.",
        "THE TOWER": "모래성처럼 무너질 수도 있지. 하지만 잔해 위에서 새 출발을 하게.",
        "THE STAR": "별빛이 아직 남았구먼. 희망을 잃지 말게.",
        "THE MOON": "착각과 진실이 뒤섞여 있네. 확신은 잠시 미뤄두게.",
        "THE SUN": "햇살이 쨍하구먼. 지금은 웃어도 좋은 때라네.",
        "JUDGEMENT": "심판의 나팔이 울린다네. 과거를 정리하고 다시 일어설 차례라네.",
        "THE WORLD": "모든 것이 제자리에 돌아왔구먼. 완성의 기쁨을 누리게.",
        
        "ACE OF WANDS": "불씨가 피어오르네. 새 아이디어가 네 손끝에 깃들었다네.",
        "TWO OF WANDS": "앞날을 내다보게. 결정의 시기라네.",
        "THREE OF WANDS": "기다림의 끝이 다가오네. 준비한 만큼 보답을 받을 걸세.",
        "FOUR OF WANDS": "축하할 일이 있구먼. 작은 성취를 즐기게.",
        "FIVE OF WANDS": "의견 충돌이 있겠네. 하지만 경쟁 속에서 성장한다네.",
        "SIX OF WANDS": "승리의 행진이라네. 모두가 자네를 주목하고 있네.",
        "SEVEN OF WANDS": "수세에 몰렸구먼. 그래도 물러서지 말게, 끝까지 버티는 거야.",
        "EIGHT OF WANDS": "빠른 변화가 몰려온다네. 행동할 때라네.",
        "NINE OF WANDS": "피곤하겠지만 아직 끝이 아니네. 마지막까지 지켜내게.",
        "TEN OF WANDS": "너무 많은 짐을 짊어졌구먼. 잠시 내려놓을 줄도 알아야지.",
        "PAGE OF WANDS": "열정적인 전령이라네. 새로운 일에 도전할 마음이 가득하네.",
        "KNIGHT OF WANDS": "불같은 추진력이 느껴지네. 하지만 성급함은 경계하게.",
        "QUEEN OF WANDS": "당당하고 매력적인 인물이로군. 자신감을 잃지 말게.",
        "KING OF WANDS": "리더십이 필요한 순간이라네. 결단하고 이끌어야 할 때라네.",
        
        "ACE OF CUPS": "감정의 샘이 터졌구먼. 사랑이 피어날 조짐이라네.",
        "TWO OF CUPS": "좋은 인연이 찾아온다네. 상호 존중이 열쇠일세.",
        "THREE OF CUPS": "함께 웃을 일이 있구먼. 친구들과 기쁨을 나누게.",
        "FOUR OF CUPS": "마음이 지쳐있네. 지금은 잠시 쉬어가도 좋네.",
        "FIVE OF CUPS": "잃은 것만 보이네? 남은 컵도 바라보게.",
        "SIX OF CUPS": "추억이 향기를 풍기네. 과거의 정이 다시 스며든다네.",
        "SEVEN OF CUPS": "환상 속에서 헤매지 말게. 진짜 원하는 걸 고르게.",
        "EIGHT OF CUPS": "이제 미련을 두지 말게. 떠나야 할 때라네.",
        "NINE OF CUPS": "소원이 이루어진다네. 마음껏 누려보게.",
        "TEN OF CUPS": "평화와 조화가 찾아오네. 진심으로 웃을 수 있을 때라네.",
        "PAGE OF CUPS": "감성이 풍부하구먼. 예술적인 영감이 찾아오고 있다네.",
        "KNIGHT OF CUPS": "낭만적인 제안이 다가오네. 하지만 현실도 잊지 말게.",
        "QUEEN OF CUPS": "따뜻하고 이해심 깊은 사람이로군. 감정의 파도 속에서도 중심을 잡게.",
        "KING OF CUPS": "감정의 주인이라네. 냉정함과 따뜻함을 함께 품게.",
        
        "ACE OF SWORDS": "진실이 번쩍하네. 이성의 칼로 길을 열게.",
        "TWO OF SWORDS": "갈림길에서 머뭇거리고 있구먼. 결단이 필요하다네.",
        "THREE OF SWORDS": "가슴이 저미는 아픔이 있겠네. 하지만 진실은 언제나 통증을 동반하지.",
        "FOUR OF SWORDS": "지친 정신을 쉬게 하게. 잠시 휴식이 약이라네.",
        "FIVE OF SWORDS": "이긴 듯 보여도 상처가 남는 싸움이라네. 현명하게 물러설 줄도 알아야지.",
        "SIX OF SWORDS": "고통을 떠나 평온을 찾아가는 여정이라네.",
        "SEVEN OF SWORDS": "누군가 속임수를 쓰고 있구먼. 눈을 부릅뜨게.",
        "EIGHT OF SWORDS": "스스로 묶여있네. 하지만 그 끈은 자네 손에 있다네.",
        "NINE OF SWORDS": "불안과 후회가 밤을 지배하겠네. 하지만 새벽은 반드시 오지.",
        "TEN OF SWORDS": "끝장 같지만, 다시 일어설 기회라네. 완전한 끝은 없지.",
        "PAGE OF SWORDS": "호기심 많은 학생이로군. 지식을 향한 갈증이 느껴진다네.",
        "KNIGHT OF SWORDS": "단호하고 빠른 자라네. 하지만 무모함은 금물이지.",
        "QUEEN OF SWORDS": "이성적이고 냉철한 인물이로군. 감정보다 진실을 중시하네.",
        "KING OF SWORDS": "법과 논리의 상징이라네. 명확한 판단으로 일처리하게.",
        
        "ACE OF PENTACLES": "기회가 눈앞에 있네. 현실적인 성취가 시작된다네.",
        "TWO OF PENTACLES": "균형이 필요하네. juggling을 잘해야 한다네.",
        "THREE OF PENTACLES": "협력의 힘이 중요하네. 함께 일할 때 결과가 좋다네.",
        "FOUR OF PENTACLES": "손에 쥔 걸 너무 꽉 쥐지 말게. 때로는 나눔이 더 큰 이익을 부르네.",
        "FIVE OF PENTACLES": "추운 겨울을 걷는 기분이겠네. 하지만 도움의 손길이 멀지 않다네.",
        "SIX OF PENTACLES": "주는 것도, 받는 것도 배움이라네. 균형이 중요하지.",
        "SEVEN OF PENTACLES": "인내의 시간이라네. 씨를 뿌렸다면 기다릴 줄도 알아야지.",
        "EIGHT OF PENTACLES": "노력은 결코 배신하지 않네. 꾸준히 다듬게.",
        "NINE OF PENTACLES": "자립의 시기라네. 스스로 이룬 것의 열매를 맛보게.",
        "TEN OF PENTACLES": "유산과 번영이 흐르네. 가족, 안정, 전통이 중심이 된다네.",
        "PAGE OF PENTACLES": "배움을 즐기는 학생이로군. 새로운 기술이 자랄 때라네.",
        "KNIGHT OF PENTACLES": "성실하고 꾸준한 인물이네. 느리지만 끝까지 간다네.",
        "QUEEN OF PENTACLES": "현실적이면서 따뜻한 사람이라네. 돌봄 속에서 풍요가 자라지.",
        "KING OF PENTACLES": "성공과 책임의 상징이라네. 자네의 노력이 결실을 맺을 때라네."
    }
    
    COLORS = [
        "에메랄드 그린", "로얄 블루", "아이보리", "스칼렛 레드", "마룬",
        "실버 그레이", "골드", "진한 네이비", "포레스트 그린", "샌드 베이지"
    ]
    
    PLACES = [
        "도서관 금서 구역 옆 통로", "천문학탑 야간 관측 공간", "금지된 숲 가장자리",
        "호그스미드 삼선술집 창가", "변신술 교실 창문 아래", "그리핀도르 휴게실 난로 앞"
    ]
    
    ITEMS = [
        "시간을 머금은 모래시계", "그리핀의 깃털 펜", "빛바랜 주문노트",
        "작은 수정구", "포션 샘플 병", "행운의 깃털 장식"
    ]
    
    def __init__(self, bot, sheet_manager):
        self.bot = bot
        self.sheet = sheet_manager
    
    @commands.command(name='타로', aliases=['tarot'])
    async def tarot(self, ctx):
        """타로 카드를 뽑습니다. (78장 풀덱)"""
        card_name, message = random.choice(list(self.TAROT_DATA.items()))
        
        color = random.choice(self.COLORS)
        place = random.choice(self.PLACES)
        item = random.choice(self.ITEMS)
        
        user_id = str(ctx.author.id)
        user = self.sheet.find_user(user_id)
        if user:
            kst = pytz.timezone('Asia/Seoul')
            today = datetime.now(kst).strftime('%Y-%m-%d')
            self.sheet.update_user(user_id, {'last_tarot_date': today})
            self.sheet.log_message(
                user=ctx.author.name,
                command='타로',
                content=card_name
            )
        
        msg = f'**{card_name}**\n\n'
        msg += f'{message}\n\n'
        msg += f'추천 색: {color}\n'
        msg += f'추천 장소: {place}\n'
        msg += f'추천 물건: {item}'
        
        await ctx.send(msg)
    
    @commands.command(name='주사위', aliases=['dice', 'd'])
    async def dice(self, ctx, sides: int = 6):
        """주사위를 굴립니다."""
        if sides < 2 or sides > 100:
            await ctx.send('주사위는 2~100면까지만 가능합니다.')
            return
        
        result = random.randint(1, sides)
        
        await ctx.send(f'{sides}면 주사위: {result}')
    
    @commands.command(name='동전', aliases=['coin', 'flip'])
    async def coin(self, ctx):
        """동전을 던집니다."""
        result = random.choice(['앞면', '뒷면'])
        
        await ctx.send(f'결과: {result}')
    
    @commands.command(name='yn', aliases=['yesno'])
    async def yn(self, ctx):
        """YES 또는 NO로 답합니다."""
        result = random.choice(['YES', 'NO'])
        
        await ctx.send(f'{result}')
    
    @commands.command(name='운세', aliases=['fortune'])
    async def fortune(self, ctx):
        """오늘의 운세를 봅니다."""
        fortunes = [
            "오늘은 행운이 가득한 날이에요.",
            "조심스럽게 행동하는 게 좋겠어요.",
            "새로운 기회가 찾아올 거예요.",
            "친구와의 대화에서 중요한 힌트를 얻을 수 있어요.",
            "오늘은 쉬는 게 최선이에요.",
            "예상치 못한 행운이 찾아올지도 몰라요.",
            "인내심이 필요한 하루가 될 거예요.",
            "웃음이 행운을 부를 거예요.",
            "직감을 믿고 행동하세요.",
            "평범하지만 평화로운 하루예요."
        ]
        
        luck_score = random.randint(1, 100)
        fortune_text = random.choice(fortunes)
        
        msg = f'**{ctx.author.name}님의 오늘 운세**\n\n'
        msg += f'{fortune_text}\n'
        msg += f'행운 지수: {luck_score}/100'
        
        await ctx.send(msg)

async def setup(bot):
    """Cog 로드"""
    sheet_manager = bot.sheet_manager
    await bot.add_cog(FunCog(bot, sheet_manager))
