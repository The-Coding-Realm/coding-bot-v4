import discord
from discord.ext import commands

class Moderation(commands.Cog):
  
    def __init__(self, bot):
        self.bot = bot
        
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
        await target.kick(reason=f'{ctx.author.id}: {reason}')
        await ctx.send(embed=discord.Embed(title='Member kicked',
                                           description=f'{target.mention} has been kicked \nReason: {reason}'))

def setup(bot):
    bot.add_cog(Moderation(bot))
