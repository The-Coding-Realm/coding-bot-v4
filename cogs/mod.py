import discord
import humanize
import time_str
import datetime
from discord.ext import commands

class Moderation(commands.Cog):
  
    def __init__(self, bot):
        self.bot = bot
        
    async def log(self, **kwargs):
        action = kwargs.pop('action')
        moderator = kwargs.pop('moderator')
        target = kwargs.pop('target')
        undo = kwargs.get('undo')
        reason = kwargs.get('reason')
        duration = kwargs.get('duration')
        if undo:
            color = discord.Color.green()
        if action == 'kick':
            if undo:
                raise ValueError('Cannot unkick')
            color = discord.Color.orange()
            action_string = 'kicked'
            icon = ':boot:'
        elif action == 'ban':
            if undo:
                action_string = 'unbanned'
                icon = ':unlock:'
            else:
                color = discord.Color.red()
                action_string = 'banned'
                icon = ':hammer:'
        elif action == 'warn':
            warn = kwargs.get('warn')
            if undo:
                if warn:
                    action_string = f'removed warning ({warn}) from'
                else:
                    action_string = f'removed all warnings from'
                icon = ':flag_white:'
            else:
                color = discord.Color.yellow()
                action_string = 'warned'
                icon = ':warning:'
        elif action == 'mute':
            if undo:
                action_string = 'unmuted'
                icon = ':loud_sound:'
            else:
                color = discord.Color.gray()
                action_string = 'muted'
                icon = ':mute:'
        else:
            raise ValueError('Incorrect Type')
        description = f'**{icon} {action_string.title()} {target.name}**{target.discriminator} *(ID: {target.id})*\n**:page_facing_up: Reason:** {reason}' + (f' \n**:clock2: Duration:** {humanize.precisedelta(duration)}' if duration else '')
        embed = discord.Embed(description=description
                              color=color,
                              timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f'{moderator} (ID: {moderator.id}',
                         icon_url=moderator.avatar_url)
        embed.set_thumbnail(url=target.avatar_url)
        logs = self.bot.get_channel(791160138199335013)
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
            await target.send(f'You have been :boot: **Kicked** :boot: from **{ctx.guild.name}**. \nReason: {reason}')
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
            await target.send(f'You have been :no_entry: **Banned** :no_entry: from **{ctx.guild.name}**. \nReason: {reason}')
        except:
            pass
        await self.log(action='ban', moderator=ctx.author, target=target, reason=reason)
        await target.kick(reason=f'{ctx.author.id}: {reason}')
        await ctx.send(embed=discord.Embed(title=':no_entry: Member Banned :no_entry:',
                                           description=f'{target.mention} has been banned \nReason: {reason}'))

    @commands.command(name='unban')
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    @commands.has_any_role(795136568805294097, 725899526350831616)
    @moderation_check
    async def _unban(self, ctx, target: int, *, reason: str = None):
        try:
            await target.send(f'You have been :unlock: **Unbanned** :unlock: from **{ctx.guild.name}**. \nReason: {reason}')
        except:
            pass
        await self.log(action='ban', moderator=ctx.author, target=target, reason=reason, undo=True)
        some_member = discord.Object(id=userid)
        await guild.unban(some_member)

    @commands.command(name='warn')
    @commands.has_guild_permissions(kick_members=True)
    @moderation_check
    async def _warn(self, ctx, target: discord.Member, *, reason: str = None):
        try:
            await target.send(f'You have been :warning: **Warned** :warning: in **{ctx.guild.name}**. \nReason: {reason}')
        except:
            pass
        await self.log(action='warn', moderator=ctx.author, target=target, reason=reason)
        # warn them here
        await ctx.send(embed=discord.Embed(title=':warning: Member Warned :warning:',
                                           description=f'{target.mention} has been warned \nReason: {reason}'))
    

def setup(bot):
    bot.add_cog(Moderation(bot))
