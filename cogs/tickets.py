import discord
from discord.ext import commands

class ReactionTickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # define variables
        react = str(payload.emoji)
        guild = self.bot.get_guild(payload.guild_id)
        # check if the user is a bot
        user = guild.get_member(payload.user_id)
        if user.bot:
            return
        # check if it is the ticket message
        if payload.message_id == 788799999327993858:
            channel = self.bot.get_channel(788798300274425896)
            message = await channel.fetch_message(788799999327993858)
            # check for a valid reaction
            if react == "📩":
                ticket = await guild.create_text_channel(f'ticket-{user.name}')
                # set perms for user to type
                await ticket.set_permissions(user, read_messages = True, send_messages = True, attach_files=True)
                # set role for ticket ping
                ticket_ping = guild.get_role(788799215417032705)
                await ticket.set_permissions(ticket_ping, read_messages = True, send_messages = True, attach_files=True)
                # make sure @everyone can't speak
                await ticket.set_permissions(guild.default_role, read_messages = False, send_messages = False)
                # ping ticket ping
                msg = await ticket.send(f'{user.mention} {ticket_ping.mention}')
                await msg.delete()
                # send embed
                em = discord.Embed(title = "Support Ticket", color = user.color)
                em.add_field(name = "Info:", value = f"I have opened a ticket for you and staff to communicate, use this channel wisely!")
                em.add_field(name = "Tips:", value = "Be as clear and concise as you can get with your problem / issues!")
                em.set_author(name = user.name, icon_url = user.icon_url)
                await ticket.send(embed = em)
        
def setup(bot):
    bot.add_cog(ReactionTickets(bot))
