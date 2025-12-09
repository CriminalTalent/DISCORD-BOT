# bot.py
# 디스코드 봇 메인 코드

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from sheet_manager import SheetManager

# 환경 변수 로드
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용 읽기 권한 필수
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 구글 시트 매니저 초기화
sheet_manager = None

@bot.event
async def on_ready():
    """봇 준비 완료 이벤트"""
    global sheet_manager
    
    print(f'[BOT] 로그인 성공: {bot.user.name} (ID: {bot.user.id})')
    print('=' * 50)
    
    # 구글 시트 연결
    try:
        sheet_manager = SheetManager(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_ID)
        print('[BOT] 구글 시트 연결 완료')
    except Exception as e:
        print(f'[BOT ERROR] 구글 시트 연결 실패: {e}')
        print('[BOT] 봇은 실행되지만 로그 기능은 비활성화됩니다.')
    
    print('=' * 50)
    print('[BOT] 준비 완료! 명령어 대기 중...')

@bot.event
async def on_message(message):
    """메시지 수신 이벤트"""
    # 봇 자신의 메시지는 무시
    if message.author == bot.user:
        return
    
    # 명령어 처리
    await bot.process_commands(message)

# ============================================
# 명령어: !log <내용>
# 내용을 구글 시트에 저장
# ============================================
@bot.command(name='log')
async def log_command(ctx, *, content: str):
    """
    메시지를 구글 시트에 로그로 저장합니다.
    
    사용법: !log <내용>
    예시: !log 회의 내용 정리 완료
    """
    if sheet_manager is None:
        await ctx.send('❌ 구글 시트가 연결되지 않았습니다.')
        return
    
    # 사용자 정보
    username = f"{ctx.author.name}#{ctx.author.discriminator}"
    
    # 로그 저장
    success = sheet_manager.log_message(
        user=username,
        command='log',
        content=content
    )
    
    if success:
        await ctx.send(f'✅ 로그 저장 완료!\n```{content}```')
    else:
        await ctx.send('❌ 로그 저장 실패!')

# ============================================
# 명령어: !show [개수]
# 최근 로그 조회
# ============================================
@bot.command(name='show')
async def show_command(ctx, limit: int = 10):
    """
    최근 로그를 조회합니다.
    
    사용법: !show [개수]
    예시: !show 5
    """
    if sheet_manager is None:
        await ctx.send('❌ 구글 시트가 연결되지 않았습니다.')
        return
    
    # 최대 20개로 제한
    limit = min(limit, 20)
    
    logs = sheet_manager.get_recent_logs(limit)
    
    if not logs:
        await ctx.send('📭 저장된 로그가 없습니다.')
        return
    
    # 로그 포맷팅
    embed = discord.Embed(
        title=f'📋 최근 로그 ({len(logs)}개)',
        color=discord.Color.blue()
    )
    
    for log in logs:
        timestamp = log.get('타임스탬프', 'N/A')
        user = log.get('사용자', 'Unknown')
        content = log.get('내용', '')
        
        # 내용이 너무 길면 자르기
        if len(content) > 100:
            content = content[:97] + '...'
        
        embed.add_field(
            name=f'[{timestamp}] {user}',
            value=content or '(내용 없음)',
            inline=False
        )
    
    await ctx.send(embed=embed)

# ============================================
# 명령어: !search <키워드>
# 로그 검색
# ============================================
@bot.command(name='search')
async def search_command(ctx, *, keyword: str):
    """
    키워드로 로그를 검색합니다.
    
    사용법: !search <키워드>
    예시: !search 회의
    """
    if sheet_manager is None:
        await ctx.send('❌ 구글 시트가 연결되지 않았습니다.')
        return
    
    results = sheet_manager.search_logs(keyword)
    
    if not results:
        await ctx.send(f'🔍 "{keyword}"에 대한 검색 결과가 없습니다.')
        return
    
    # 최대 10개만 표시
    results = results[-10:]
    
    embed = discord.Embed(
        title=f'🔍 검색 결과: "{keyword}" ({len(results)}개)',
        color=discord.Color.green()
    )
    
    for log in results:
        timestamp = log.get('타임스탬프', 'N/A')
        user = log.get('사용자', 'Unknown')
        content = log.get('내용', '')
        
        # 키워드 강조 (볼드 처리)
        content_highlighted = content.replace(
            keyword,
            f'**{keyword}**'
        )
        
        if len(content_highlighted) > 150:
            content_highlighted = content_highlighted[:147] + '...'
        
        embed.add_field(
            name=f'[{timestamp}] {user}',
            value=content_highlighted or '(내용 없음)',
            inline=False
        )
    
    await ctx.send(embed=embed)

# ============================================
# 명령어: !clear (관리자 전용)
# 로그 초기화
# ============================================
@bot.command(name='clear')
@commands.has_permissions(administrator=True)
async def clear_command(ctx):
    """
    로그를 초기화합니다. (관리자 전용)
    
    사용법: !clear
    """
    if sheet_manager is None:
        await ctx.send('❌ 구글 시트가 연결되지 않았습니다.')
        return
    
    # 확인 메시지
    confirm_msg = await ctx.send('⚠️ 정말로 모든 로그를 삭제하시겠습니까? (10초 내 ✅ 반응 추가)')
    await confirm_msg.add_reaction('✅')
    
    def check(reaction, user):
        return (
            user == ctx.author 
            and str(reaction.emoji) == '✅' 
            and reaction.message.id == confirm_msg.id
        )
    
    try:
        await bot.wait_for('reaction_add', timeout=10.0, check=check)
        
        # 로그 삭제 실행
        success = sheet_manager.clear_logs()
        
        if success:
            await ctx.send('🗑️ 모든 로그가 삭제되었습니다.')
        else:
            await ctx.send('❌ 로그 삭제 실패!')
            
    except:
        await ctx.send('⏱️ 시간 초과. 취소되었습니다.')

# ============================================
# 명령어: !help
# 도움말
# ============================================
@bot.command(name='help')
async def help_command(ctx):
    """봇 사용법을 안내합니다."""
    embed = discord.Embed(
        title='🤖 디스코드 로그 봇 사용법',
        description='구글 시트에 메시지를 로그로 저장하는 봇입니다.',
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name='📝 !log <내용>',
        value='내용을 구글 시트에 저장합니다.\n예: `!log 회의 내용 작성 완료`',
        inline=False
    )
    
    embed.add_field(
        name='📋 !show [개수]',
        value='최근 로그를 조회합니다. (기본 10개)\n예: `!show 5`',
        inline=False
    )
    
    embed.add_field(
        name='🔍 !search <키워드>',
        value='키워드로 로그를 검색합니다.\n예: `!search 회의`',
        inline=False
    )
    
    embed.add_field(
        name='🗑️ !clear (관리자 전용)',
        value='모든 로그를 삭제합니다.',
        inline=False
    )
    
    await ctx.send(embed=embed)

# ============================================
# 에러 핸들러
# ============================================
@bot.event
async def on_command_error(ctx, error):
    """명령어 에러 처리"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'❌ 필수 인자가 누락되었습니다. `!help`를 참고하세요.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('❌ 이 명령어를 사용할 권한이 없습니다.')
    elif isinstance(error, commands.CommandNotFound):
        pass  # 없는 명령어는 무시
    else:
        print(f'[ERROR] {error}')
        await ctx.send(f'❌ 오류가 발생했습니다: {error}')

# ============================================
# 봇 실행
# ============================================
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
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f'[ERROR] 봇 실행 실패: {e}')
