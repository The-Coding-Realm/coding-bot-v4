import discord, random, asyncio 
from discord.ext import commands, tasks


class Trainee(commands.Cog):

    def __init__(self,bot):
        """Trainee commands"""
        self.bot = bot
        self.guild = 681882711945641997
        self.channel = 743817386792058971
        self.role = 729537643951554583
        self.managing_ids = [690420846774321221]
        self.enabled = False

    @commands.group(invoke_without_command=True)
    async def trainee(self, ctx):
        """List trainees"""
        role = self.bot.get_guild(self.guild).get_role(self.role)
        members = [member.mention for member in role.members]
        if len(members) == 0:
            return await ctx.send('no trainees :sob:')
        embed = discord.Embed(title='Trainees',description='\n'.join(members))
        await ctx.send(embed=embed)
    
    @trainee.command()
    async def ping(self, ctx, toggle: bool = None):
        """Toggle trainee pings"""
        if not ctx.author.id in self.managing_ids and not ctx.author.guild_permissions.administrator:
            return await ctx.send('no. only the admins can make the trainees suffer')
        if toggle is None:
            toggle = not self.enabled
        self.enabled = toggle
        await ctx.send(f'Trainee pinging: {self.enabled}')
        try:
            self.trainee_pings.cancel()
        except:
            pass
        await asyncio.sleep(5)
        await self.ping_trainees.start()

    @tasks.loop(hours=1)
    async def ping_trainees(self):
        role = self.bot.get_guild(self.guild).get_role(self.role)
        channel = self.bot.get_guild(self.guild).get_channel(self.channel)
        if self.enabled:
            target = random.choice([trainee.mention for trainee in role.members])
            msg = await channel.send(target + ' lol')
            await msg.delete()

def setup(bot):
    bot.add_cog(Trainee(bot))
