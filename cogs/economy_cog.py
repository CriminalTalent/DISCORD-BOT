# cogs/economy_cog.py
# 경제 관련 명령어

import discord
from discord.ext import commands

class EconomyCog(commands.Cog, name="경제"):
    """갈레온 및 아이템 관리"""
    
    def __init__(self, bot, sheet_manager):
        self.bot = bot
        self.sheet = sheet_manager
    
    @commands.command(name='등록', aliases=['register'])
    async def register(self, ctx, *, name: str = None):
        """게임에 등록합니다."""
        user_id = str(ctx.author.id)
        
        existing = self.sheet.find_user(user_id)
        if existing:
            await ctx.send(f'이미 등록되어 있습니다. (이름: {existing["name"]})')
            return
        
        if not name:
            name = ctx.author.name
        
        success = self.sheet.create_user(user_id, name, initial_galleons=100)
        
        if success:
            await ctx.send(f'{name}님 등록 완료! 초기 갈레온 100개가 지급되었습니다.')
        else:
            await ctx.send('등록 중 오류가 발생했습니다.')
    
    @commands.command(name='주머니', aliases=['pouch', '가방'])
    async def pouch(self, ctx, member: discord.Member = None):
        """소지품을 확인합니다."""
        target = member if member else ctx.author
        user_id = str(target.id)
        
        user = self.sheet.find_user(user_id)
        if not user:
            if target == ctx.author:
                await ctx.send('아직 등록되지 않았습니다. !등록 명령어를 사용하세요.')
            else:
                await ctx.send(f'{target.mention}님은 등록되지 않았습니다.')
            return
        
        items_dict = self.sheet.get_user_items(user_id)
        
        if items_dict:
            items_text = '\n'.join([
                f'{name} x{count}' if count > 1 else name
                for name, count in items_dict.items()
            ])
        else:
            items_text = '없음'
        
        msg = f'**{user["name"]}의 주머니**\n\n'
        msg += f'갈레온: {user["galleons"]}개\n'
        msg += f'아이템:\n{items_text}'
        
        await ctx.send(msg)
    
    @commands.command(name='상점', aliases=['shop', 'store'])
    async def shop(self, ctx):
        """상점 아이템 목록을 봅니다."""
        items = self.sheet.get_all_items(sellable_only=True)
        
        if not items:
            await ctx.send('현재 판매 중인 아이템이 없습니다.')
            return
        
        msg = '**상점 아이템 목록**\n\n'
        for item in items:
            desc = item['description'][:100] if item['description'] else '신비한 물건...'
            msg += f'{item["name"]} - {item["price"]}G\n{desc}\n\n'
        
        await ctx.send(msg)
    
    @commands.command(name='구매', aliases=['buy'])
    async def buy(self, ctx, *, item_name: str):
        """아이템을 구매합니다."""
        user_id = str(ctx.author.id)
        
        user = self.sheet.find_user(user_id)
        if not user:
            await ctx.send('먼저 !등록 명령어로 등록하세요.')
            return
        
        if user['galleons'] < 0:
            await ctx.send('빚을 갚기 전까지는 물건을 살 수 없습니다.')
            return
        
        item = self.sheet.find_item(item_name)
        if not item:
            await ctx.send(f'"{item_name}"은(는) 상점에 없는 물건입니다.')
            return
        
        if not item['sellable']:
            await ctx.send(f'"{item_name}"은(는) 현재 판매하지 않습니다.')
            return
        
        if user['galleons'] < item['price']:
            await ctx.send(f'갈레온이 부족합니다. (필요: {item["price"]}G, 보유: {user["galleons"]}G)')
            return
        
        new_galleons = user['galleons'] - item['price']
        self.sheet.update_user(user_id, {'galleons': new_galleons})
        self.sheet.add_item_to_user(user_id, item_name)
        
        self.sheet.log_message(
            user=ctx.author.name,
            command='구매',
            content=f'{item_name} - {item["price"]}G'
        )
        
        await ctx.send(f'{item_name} 구매 완료! 남은 갈레온: {new_galleons}G')
    
    @commands.command(name='사용', aliases=['use'])
    async def use_item(self, ctx, *, item_name: str):
        """아이템을 사용합니다."""
        user_id = str(ctx.author.id)
        
        user = self.sheet.find_user(user_id)
        if not user:
            await ctx.send('먼저 !등록 명령어로 등록하세요.')
            return
        
        items_dict = self.sheet.get_user_items(user_id)
        if item_name not in items_dict:
            await ctx.send(f'"{item_name}"을(를) 가지고 있지 않습니다.')
            return
        
        item = self.sheet.find_item(item_name)
        if not item:
            await ctx.send('아이템 정보를 찾을 수 없습니다.')
            return
        
        if not item['usable']:
            await ctx.send(f'"{item_name}"은(는) 사용할 수 없는 아이템입니다.')
            return
        
        self.sheet.remove_item_from_user(user_id, item_name)
        
        self.sheet.log_message(
            user=ctx.author.name,
            command='사용',
            content=item_name
        )
        
        description = item['description']
        if '/' in description:
            import random
            choices = [d.strip() for d in description.split('/')]
            description = random.choice(choices)
        
        msg = f'{item_name} 사용!\n'
        if description:
            msg += f'\n{description}'
        
        await ctx.send(msg)
    
    @commands.command(name='양도', aliases=['give', 'transfer'])
    async def transfer(self, ctx, member: discord.Member, amount_or_item: str):
        """갈레온 또는 아이템을 양도합니다."""
        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)
        
        if sender_id == receiver_id:
            await ctx.send('자기 자신에게는 양도할 수 없습니다.')
            return
        
        sender = self.sheet.find_user(sender_id)
        if not sender:
            await ctx.send('먼저 !등록 명령어로 등록하세요.')
            return
        
        if sender['galleons'] < 0:
            await ctx.send('빚이 있는 상태에서는 양도할 수 없습니다.')
            return
        
        receiver = self.sheet.find_user(receiver_id)
        if not receiver:
            await ctx.send(f'{member.mention}님은 아직 등록되지 않았습니다.')
            return
        
        if amount_or_item.isdigit():
            amount = int(amount_or_item)
            
            if amount <= 0:
                await ctx.send('1 이상의 갈레온만 양도할 수 있습니다.')
                return
            
            if sender['galleons'] < amount:
                await ctx.send(f'갈레온이 부족합니다. (보유: {sender["galleons"]}G)')
                return
            
            self.sheet.update_user(sender_id, {'galleons': sender['galleons'] - amount})
            self.sheet.update_user(receiver_id, {'galleons': receiver['galleons'] + amount})
            
            self.sheet.log_message(
                user=ctx.author.name,
                command='양도',
                content=f'{amount}G → {member.name}'
            )
            
            await ctx.send(f'{member.mention}님에게 {amount}G를 양도했습니다.')
        
        else:
            item_name = amount_or_item
            items_dict = self.sheet.get_user_items(sender_id)
            
            if item_name not in items_dict:
                await ctx.send(f'"{item_name}"을(를) 가지고 있지 않습니다.')
                return
            
            self.sheet.remove_item_from_user(sender_id, item_name)
            self.sheet.add_item_to_user(receiver_id, item_name)
            
            self.sheet.log_message(
                user=ctx.author.name,
                command='양도',
                content=f'{item_name} → {member.name}'
            )
            
            await ctx.send(f'{member.mention}님에게 {item_name}을(를) 양도했습니다.')

async def setup(bot):
    """Cog 로드"""
    sheet_manager = bot.sheet_manager
    await bot.add_cog(EconomyCog(bot, sheet_manager))
