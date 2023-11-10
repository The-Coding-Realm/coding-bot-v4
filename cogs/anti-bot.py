import discord
from discord.ext import commands

class AntiBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.blacklisted_nicks = ['discord.gg/', 'dsc.gg/']

    @commands.Cog.listener()
    async def on_ready(self):
        for member in self.bot.get_guild(681882711945641997).members:
            for w in self.bot.blacklisted_nicks:
                check_name = [word for word in member.name.split() if word.startswith(w)]
                check_nick = []
                if member.nick:
                    check_nick = [word for word in member.nick.split() if word.startswith(w)]
                logs = self.bot.get_guild(681882711945641997).get_channel(791160138199335013)

                if check_nick or check_name:
                    try:
                        await member.send(f"You have been kicked from **The Coding Academy** \nReason: Invite link in username.")
                    except:
                        pass
                    await member.kick(reason="Invite link in username/nickname.")
                    await logs.send(embed=discord.Embed(title=":boot: Auto-kick", description=f":boot: **Kicked: {member.name}** ({member.id}) \n**:page_facing_up: Reason:** Invite link in username/nickname"))
                    break

    @commands.Cog.listener()
    async def on_member_join(self, member):
        for w in self.bot.blacklisted_nicks:
            check = [word for word in member.name.split() if word.startswith(w)]
            if check:
                try:
                    await member.send(f"You have been kicked from **The Coding Academy** \nReason: Invite link in username.")
                except:
                    pass
                await member.kick(reason="Invite link in username")
                logs = self.bot.get_guild(681882711945641997).get_channel(791160138199335013) # Channel -> #warns-and-ban-logs
                await logs.send(embed=discord.Embed(title=":boot: Auto-kick", description=f":boot: **Kicked: {member.name}** ({member.id}) \n**:page_facing_up: Reason:** Invite link in username"))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        for w in self.bot.blacklisted_nicks:
            check_name = [word for word in after.name.split() if word.startswith(w)]
            check_nick = []
            if after.nick:
                check_nick = [word for word in after.nick.split() if word.startswith(w)]
            logs = self.bot.get_guild(681882711945641997).get_channel(791160138199335013)

            if check_nick or check_name:
                try:
                    await after.send(f"You have been kicked from **The Coding Academy** \nReason: Invite link in username.")
                except:
                    pass
                await after.kick(reason="Invite link in username/nickname.")
                await logs.send(embed=discord.Embed(title=":boot: Auto-kick", description=f":boot: **Kicked: {after.name}** ({after.id}) \n**:page_facing_up: Reason:** Invite link in username/nickname"))
                break
        

    
def setup(bot):
    bot.add_cog(AntiBot(bot))