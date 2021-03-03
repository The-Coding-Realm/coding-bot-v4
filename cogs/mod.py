import discord
import datetime
from discord.ext import commands

class Moderation(commands.Cog):
  
    def __init__(self, bot):
        self.bot = bot
        
    async def log(self, **kwargs):
        action = kwargs.pop('action')
        moderator = kwargs.pop('moderator')
        target = kwargs.pop('target')
        reason = kwargs.get('reason')
        if action == 'kick':
            color = discord.Color.yellow()
            action_string = 'kicked'
        elif action == 'ban':
            color = discord.Color.red()
            action_string = 'banned'
        elif action == 'warn':
            color = discord.Color.green()
            action_string = 'warned'
        elif action == 'mute':
            color = discord.Color.blue()
            action_string = 'muted'
        else:
            raise ValueError('Incorrect Type')
        embed = discord.Embed(title=f'Member {action_string}',
                              color=color,
                              timestamp=datetime.datetime.utcnow())
        embed.add_field(name='Moderator',
                        value=moderator.mention)
        embed.add_field(name='Target',
                        value=target.mention)
        embed.add_field(name='Reason',
                        value=reason)
        logs = self.bot.get_channel(757433319569883146)
        await logs.send(embed=embed)
        
    @commands.check
    async def moderation_check(self):
        target = self.kwargs.get('target')
        if not target:
            return True
        if self.author.top_role <= target.top_role:
            await self.send(embed=self.error('You cannot use moderation commands on users higher or equal to you.'))
            return False
        return True
        
    @commands.command(name='kick')
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.has_guild_permissions(kick_members=True)
    @moderation_check
    async def _kick(self, ctx, target: discord.Member, *, reason: str = None):
        try:
            await target.send(f'You have been :boot: kicked :boot: from **{ctx.guild.name}**. \nReason: {reason}')
        except:
            pass
        await self.log(action='kick', moderator=ctx.author, target=target, reason=reason)
        await target.kick(reason=f'{ctx.author.id}: {reason}')
        await ctx.send(embed=discord.Embed(title=':boot: Member Kicked :boot:',
                                           description=f'{target.mention} has been kicked \nReason: {reason}'))
        
    @commands.command(name='ban')
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    @moderation_check
    async def _ban(self, ctx, target: discord.Member, *, reason: str = None):
        try:
            await target.send(f'You have been :no_entry: banned :no_entry: from **{ctx.guild.name}**. \nReason: {reason}')
        except:
            pass
        await self.log(action='ban', moderator=ctx.author, target=target, reason=reason)
        await target.kick(reason=f'{ctx.author.id}: {reason}')
        await ctx.send(embed=discord.Embed(title=':no_entry: Member Banned :no_entry:',
                                           description=f'{target.mention} has been banned \nReason: {reason}'))

    @commands.command(name='warn')
    @commands.has_guild_permissions(kick_members=True)
    @moderation_check
    async def _warn(self, ctx, target: discord.Member, *, reason: str = None):
        try:
            await target.send(f'You have been :warning: warned :warning: in **{ctx.guild.name}**. \nReason: {reason}')
        except:
            pass
        await self.log(action='warn', moderator=ctx.author, target=target, reason=reason)
        # warn them here
        await ctx.send(embed=discord.Embed(title=':warning: Member Warned :warning:',
                                           description=f'{target.mention} has been warned \nReason: {reason}'))
    

def setup(bot):
    bot.add_cog(Moderation(bot))
