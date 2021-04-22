import discord
from discord.ext import commands
import datetime
import asyncio
from discord.ext.commands import has_guild_permissions

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
                # send a DM
                await user.send(embed = discord.Embed(title = "Ticket Successfully Created!", description = f"Your ticket was successfully created, we should've pinged you and the available moderators at the time!\n**Ticket:** {ticket.mention}", color = author.color, timestamp = datetime.datetime.utcnow()))
                # log the event
                logs = self.client.get_channel(829936676021075999)
                em = discord.Embed(title=  "New Ticket!", color = author.color, description = "A new ticket was created!")
                em.set_author(name = user.name, icon_url = user.avatar_url)
                em.add_field(name = "Access point:", value = ticket.mention)
                em.add_field(name = "User:", value = user.mention)
                await logs.send(embed = em)

    @commands.command()
    @has_guild_permissions(ban_members = True)
    async def close(self, ctx, *,  reason = None):
        channel = ctx.channel
        name = channel.name
        if name.startswith("ticket-"):
            messageEmbed = discord.Embed(title = "Ticket Closing!", color = ctx.author.color,
            description = "This ticket will close in ten seconds. Thanks for your time!")
            seconds = 10
            messageEmbed.add_field(name= "Time remaining:", value = f"`{seconds}`")
            messageEmbed.add_field(name = "Moderator:", value = f"{ctx.author.mention}")
            messageEmbed.add_field(name = "Reason:", value = f"`{reason}`")
            await ctx.send(embed = messageEmbed)
            logs = self.client.get_channel(829936676021075999)
            try:
                _arg, username = name.split('-')
                em = discord.Embed(title=  "Ticket Closes!", color = ctx.author.color, description = "A ticket was closed!")
                em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
                em.add_field(name = "User:", value = f"{username}")
                em.add_field(name = "Moderator:", value = f"{ctx.author.mention}")
                em.add_field(name = "Reason:", value = f"`{reason}`")
            except:
                """
                if the user has a name like: `My Friend`
                when creating the ticket it'll come out like this:
                ticket-my-friend

                This means that: ticket_type, username = name.split('-') would raise an error
                """
                em = discord.Embed(title = "Ticket Closes!", color = ctx.author.color, description = "A ticket was closed!")
                em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
                em.add_field(name = "Moderator:", value = ctx.author.mention)
                em.add_field(name = "Reason:", value = f"`{reason}`")
                em.set_footer(text = "Minimal Info", icon_url = ctx.author.avatar_url)
            await logs.send(embed = em)
            # sleep and delete channel
            await asyncio.sleep(10)
            # now delete the channel
            await channel.delete()
        else:
            em = discord.Embed(title = "Closing Failed!", color= ctx.author.color)
            em.add_field(name = "Reason:", value = f'This channel ({ctx.channel.mention}) is not a ticket channel!')
            em.add_field(name = "Try in another channel", value = "Only a channel which has been a ticket can be closed!")
            em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = em)
    
    @commands.command(aliases=["add", "addmemberticket", "assignticket"])
    @has_guild_permissions(kick_members = True)
    async def addmember(self, ctx, member_id: int = None, *, reason = None):
        channel = ctx.channel
        name = channel.name
        if name.startswith("ticket-"):
            ticketMember = None
            for member in ctx.guild.members:
                if member.id == member_id:
                    ticketMember = member
                    await channel.set_permissions(member, send_messages = True, read_messages = True)
                    await ctx.send(f"{member.mention} was successfully added to the ticket!")
                    break
            if ticketMember is None:
                await ctx.send("Invalid member ID!")
                return
            logs = self.client.get_channel(829936676021075999)
            try:
                _arg, username = ctx.channel.name.split('-')
                em = discord.Embed(title=  "New Ticket Member!", color = ctx.author.color, description = f"A wild {ticketMember.name} appeared in {ctx.channel.mention}!")
                em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
                em.add_field(name = "User who was added:", value = f"{ticketMember.mention}")
                em.add_field(name = "The User who's ticket it was:", value = f"`{username}`")
                em.add_field(name = "Moderator:", value = f"{ctx.author.mention}")
                em.add_field(name = "Reason:", value = f"`{reason}`")
            except:
                em = discord.Embed(title=  "New Ticket Member!", color = ctx.author.color, description = f"A wild {ticketMember.name} appeared in `{ctx.channel.name}`!")
                em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
                em.add_field(name = "Moderator:", value = f"{ctx.author.mention}")
                em.add_field(name = "Reason:", value = f"`{reason}`")
            await logs.send(embed = em)
        else:
            await ctx.send('This channel isn\'t a ticket channel')
            return
    
    @commands.command()
    @has_guild_permissions(kick_members = True)
    async def claim(self, ctx):
        """Claims a ticket!"""
        channel = ctx.channel
        name = channel.name
        if name.startswith("ticket-"):
            em = discord.Embed(title = 'Ticket Claimed!', color = ctx.author.color, timestamp = datetime.datetime.now())
            await channel.send(embed = em)
            logs = self.client.get_channel(829936676021075999)
            try:
                _arg, username = ctx.channel.name.split('-')
                em = discord.Embed(title=  "Ticket Claimed!", color = ctx.author.color, description = f"{ctx.author.mention} has claimed {channel.mention}!")
                em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
                em.add_field(name = "Mod who claimed:", value = f"{ctx.author.mention}")
                em.add_field(name = "The User who's ticket it was:", value = f"`{username}`")
            except:
                em = discord.Embed(title=  "Ticket Claimed!", color = ctx.author.color, description = f"{ctx.author.mention} has claimed {channel.mention}!")
                em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
                em.add_field(name = "Mod who claimed:", value = f"{ctx.author.mention}")
                em.set_footer(text = 'Minimal Logging')
            await logs.send(embed = em)
        else:
            return await ctx.send('Not a ticket channel!')

def setup(bot):
    bot.add_cog(ReactionTickets(bot))
