# bot.py
# 디스코드 봇 메인 코드

import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from sheet_manager import SheetManager

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

bot.sheet_manager = None

@bot.event
async def on_ready():
    """봇 준비 완료 이벤트"""
    print('=' * 60)
    print(f'[BOT] 로그인 성공: {bot.user.name} (ID: {bot.user.id})')
    print('=' * 60)
    
    try:
        bot.sheet_manager = SheetManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_ID)
        print('[SHEET] 구글 시트 연결 완료')
    except Exception as e:
        print(f'[ERROR] 구글 시트 연결 실패: {e}')
        print('[WARNING] 봇은 실행되지만 데이터 기능이 제한됩니다.')
    
    await load_cogs()
    
    print('=' * 60)
    print('[BOT] 준비 완료! 명령어 대기 중...')
    print('=' * 60)

async def load_cogs():
    """Cog 파일들 로드"""
    cogs = [
        'cogs.economy_cog',
        'cogs.gambling_cog',
        'cogs.fun_cog'
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'[COG] {cog} 로드 완료')
        except Exception as e:
            print(f'[ERROR] {cog} 로드 실패: {e}')

@bot.event
async def on_message(message):
    """메시지 수신 이벤트"""
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)

@bot.command(name='도움말', aliases=['help', 'commands'])
async def help_command(ctx, category: str = None):
    """봇 사용법을 안내합니다."""
    if not category:
        msg = '**디스코드 RPG 봇**\n\n'
        msg += '카테고리:\n'
        msg += '!도움말 경제 - 갈레온, 구매, 양도 등\n'
        msg += '!도움말 도박 - 베팅\n'
        msg += '!도움말 재미 - 타로, 주사위, 동전, 운세\n'
        
        await ctx.send(msg)
    
    elif category in ['경제', 'economy']:
        msg = '**경제 명령어**\n\n'
        msg += '!등록 <이름> - 게임에 등록 (초기 갈레온 100개)\n'
        msg += '!주머니 [@사용자] - 소지품 확인\n'
        msg += '!상점 - 판매 중인 아이템 목록\n'
        msg += '!구매 <아이템명> - 아이템 구매\n'
        msg += '!사용 <아이템명> - 아이템 사용\n'
        msg += '!양도 @사용자 <갈레온|아이템> - 갈레온 또는 아이템 양도\n'
        
        await ctx.send(msg)
    
    elif category in ['도박', 'gamble']:
        msg = '**도박 명령어**\n\n'
        msg += '!베팅 <금액> - 갈레온 베팅 (배당: -5x ~ +5x, 하루 최대 3번)\n'
        
        await ctx.send(msg)
    
    elif category in ['재미', 'fun']:
        msg = '**재미 명령어**\n\n'
        msg += '!타로 - 타로 카드 뽑기 (78장 풀덱)\n'
        msg += '!주사위 [면수] - 주사위 굴리기 (기본 6면)\n'
        msg += '!동전 - 동전 던지기\n'
        msg += '!yn - YES/NO 답변\n'
        msg += '!운세 - 오늘의 운세\n'
        
        await ctx.send(msg)
    
    else:
        await ctx.send(f'"{category}" 카테고리를 찾을 수 없습니다. 사용 가능: 경제, 도박, 재미')

@bot.command(name='reload')
@commands.has_permissions(administrator=True)
async def reload_cogs(ctx):
    """Cog 재로드 (관리자 전용)"""
    cogs = list(bot.extensions.keys())
    
    for cog in cogs:
        try:
            await bot.reload_extension(cog)
            print(f'[COG] {cog} 재로드 완료')
        except Exception as e:
            await ctx.send(f'{cog} 재로드 실패: {e}')
            return
    
    await ctx.send(f'{len(cogs)}개 Cog 재로드 완료')

@bot.command(name='갈레온지급', aliases=['addgalleons'])
@commands.has_permissions(administrator=True)
async def add_galleons(ctx, member: discord.Member, amount: int):
    """특정 사용자에게 갈레온 지급 (관리자 전용)"""
    if bot.sheet_manager is None:
        await ctx.send('구글 시트가 연결되지 않았습니다.')
        return
    
    user_id = str(member.id)
    user = bot.sheet_manager.find_user(user_id)
    
    if not user:
        await ctx.send(f'{member.mention}님은 등록되지 않았습니다.')
        return
    
    new_galleons = user['galleons'] + amount
    bot.sheet_manager.update_user(user_id, {'galleons': new_galleons})
    
    await ctx.send(f'{member.mention}님에게 {amount}G 지급 완료 (현재: {new_galleons}G)')

@bot.event
async def on_command_error(ctx, error):
    """명령어 에러 처리"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('필수 인자가 누락되었습니다. !도움말을 참고하세요.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('이 명령어를 사용할 권한이 없습니다.')
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.BadArgument):
        await ctx.send('잘못된 인자입니다. 사용법을 확인하세요.')
    else:
        print(f'[ERROR] {error}')
        await ctx.send(f'오류가 발생했습니다: {error}')

async def main():
    """비동기 메인 함수"""
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print('[ERROR] DISCORD_TOKEN이 설정되지 않았습니다.')
        print('       .env 파일을 확인하세요.')
        exit(1)
    
    if not GOOGLE_SHEET_ID:
        print('[ERROR] GOOGLE_SHEET_ID가 설정되지 않았습니다.')
        print('       .env 파일을 확인하세요.')
        exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n[INFO] 봇 종료 중...')
    except Exception as e:
        print(f'[ERROR] 봇 실행 실패: {e}')
