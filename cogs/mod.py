import discord
from discord.ext import commands

class Moderation(commands.Cog):
  
    def __init__(self, bot):
        self.bot = bot
        
    async def log(self, **kwargs):
        action = kwargs.pop(type)
        action_string = action + 'ed' if not action.endswith('e') else action + 'd'
        moderator = kwargs.pop(moderator)
        target = kwargs.pop(target)
        reason = kwargs.get('reason')
        if action == 'kick':
            color = discord.Color.yellow()
        elif action == 'ban':
            color = discord.Color.red()
        elif action == 'warn':
            color = discord.Color.green()
        elif action == 'mute':
            color = discord.Color.blue()
        else:
            raise ValueError('Incorrect Type')
        embed = discord.Embed(title=f'Member {action_string}'
                              color=color)
        embed.add_field(name='Moderator',
                        description=moderator.mention)
        embed.add_field(name='Target',
                        description=target.mention)
        embed.add_field(name='Reason',
                        description=reason)
        logs = bot.get_channel(757433319569883146)
        await logs.send(embed=embed)
        
    @commands.command(name='kick')
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.has_guild_permissions(kick_members=True)
    async def _kick(self, ctx, target: discord.Member, reason: str = None):
        if ctx.author.top_role <= target.top_role:
            return await ctx.send(embed=ctx.error('You cannot use moderation commands on users higher or equal to you.'))
        try:
            await target.send(f'You have been kicked from **{ctx.guild.name}**. \nReason: {reason}')
        except:
            pass
        await self.log(action='kick', moderator=ctx.author, target=target, reason=reason)
        await target.kick(reason=f'{ctx.author.id}: {reason}')
        await ctx.send(embed=discord.Embed(title='Member kicked',
                                           description=f'{target.mention} has been kicked \nReason: {reason}'))

def setup(bot):
    bot.add_cog(Moderation(bot))
