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
        await ctx.send_help('trainee')
        
    @trainee.command(name='list')
    async def trainee_list(self, ctx):
        """List trainees"""
        role = self.bot.get_guild(self.guild).get_role(self.role)
        members = [member.mention for member in role.members]
        if len(members) == 0:
            return await ctx.send('no trainees :sob:')
        embed = ctx.embed(title='Trainees', description='\n'.join(members))
        await ctx.send(embed=embed)
    
    @trainee.command(name='ping')
    @commands.has_guild_permissions(administrator=True)
    async def trainee_ping(self, ctx, toggle: bool = None):
        """Toggle trainee pings"""
        if toggle is None:
            toggle = not self.enabled
        self.enabled = toggle
        await ctx.send(embed=ctx.embed(title='Trainee Pinging', description="enabled" if self.enabled else "disabled"))
        self.ping_trainees.cancel()
        await asyncio.sleep(5)
        self.ping_trainees.start()

    @tasks.loop(hours=1)
    async def ping_trainees(self):
        role = self.bot.get_guild(self.guild).get_role(self.role)
        channel = self.bot.get_guild(self.guild).get_channel(self.channel)
        if self.enabled:
            target = random.choice([trainee.mention for trainee in role.members])
            msg = await channel.send(target + ' lol')
            await msg.delete()
            
    async def cog_check(self, ctx):
        return ctx.guild.id == 681882711945641997

def setup(bot):
    bot.add_cog(Trainee(bot))
