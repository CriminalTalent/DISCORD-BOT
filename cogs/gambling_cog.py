# cogs/gambling_cog.py
# 도박 관련 명령어

import discord
from discord.ext import commands
import random
from datetime import datetime
import pytz

class GamblingCog(commands.Cog, name="도박"):
    """베팅 및 도박 게임"""
    
    MAX_BETS_PER_DAY = 3
    
    def __init__(self, bot, sheet_manager):
        self.bot = bot
        self.sheet = sheet_manager
    
    @commands.command(name='베팅', aliases=['bet', 'gamble'])
    async def bet(self, ctx, amount: int):
        """갈레온을 베팅합니다. (배당률: -5x ~ +5x, 하루 최대 3번)"""
        user_id = str(ctx.author.id)
        
        user = self.sheet.find_user(user_id)
        if not user:
            await ctx.send('먼저 !등록 명령어로 등록하세요.')
            return
        
        if amount <= 0:
            await ctx.send('1 이상의 갈레온만 베팅할 수 있습니다.')
            return
        
        if user['galleons'] < 0:
            await ctx.send('빚쟁이는 베팅할 수 없습니다.')
            return
        
        if user['galleons'] < amount:
            await ctx.send(f'갈레온이 부족합니다. (보유: {user["galleons"]}G)')
            return
        
        kst = pytz.timezone('Asia/Seoul')
        today = datetime.now(kst).strftime('%Y-%m-%d')
        
        if user['last_bet_date'] == today:
            bet_count = user['bet_count']
        else:
            bet_count = 0
        
        if bet_count >= self.MAX_BETS_PER_DAY:
            await ctx.send(f'오늘은 이미 {self.MAX_BETS_PER_DAY}번 베팅했습니다. 내일 다시 시도하세요.')
            return
        
        multiplier = random.randint(-5, 5)
        profit_loss = amount * multiplier
        new_galleons = user['galleons'] + profit_loss
        new_bet_count = bet_count + 1
        
        self.sheet.update_user(user_id, {
            'galleons': new_galleons,
            'last_bet_date': today,
            'bet_count': new_bet_count
        })
        
        self.sheet.log_message(
            user=ctx.author.name,
            command='베팅',
            content=f'{amount}G × {multiplier} = {profit_loss:+d}G'
        )
        
        if profit_loss > 0:
            result = '승리'
        elif profit_loss < 0:
            result = '패배'
        else:
            result = '무승부'
        
        msg = f'베팅 결과: {result}\n'
        msg += f'베팅 금액: {amount}G\n'
        msg += f'배당률: x{multiplier}\n'
        msg += f'손익: {profit_loss:+d}G\n'
        msg += f'현재 잔액: {new_galleons}G\n'
        msg += f'오늘 사용: {new_bet_count}/{self.MAX_BETS_PER_DAY}'
        
        await ctx.send(msg)

async def setup(bot):
    """Cog 로드"""
    sheet_manager = bot.sheet_manager
    await bot.add_cog(GamblingCog(bot, sheet_manager))
