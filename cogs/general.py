"""
Coding Bot v4
~~~~~~~~~~~~~~~~~~
This file contains elements that are under the following licenses:
Copyright (c) 2015 Rapptz
license MIT, see https://github.com/Rapptz/RoboDanny/blob/e1c3c28fe20eb192463f7fc224a399141f0d915d/LICENSE.txt for more details.
"""

import discord
import time
import asyncio
import re
import url_parser
from jishaku.codeblocks import codeblock_converter
from discord.ext import commands


async def filter_links(bot, message):
    if message.author.permissions_in(message.channel).manage_messages:
        return
    regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    matches = re.findall(regex, message.content, re.MULTILINE)
    urls = []
    for link in matches:
        try:
            urls = [''.join(url_parser.get_base_url(str(link)).split('//')[1:])]
            async with bot.http._HTTPClient__session.get(link) as resp:
                urls.append(str(''.join(url_parser.get_base_url(str(resp.real_url)).split('//')[1:])))
            for url in urls:
                for blocked in [
                    'grabify.link',                         # Ip Grabber
                    'pornhub.com',                          # Porn,
                    'bobdotcom.xyz'                         # testing
                ]:
                    if url.startswith(blocked):
                        await message.delete()
                        await message.channel.send(f':warning: {message.author.mention} That link is not allowed :warning:', delete_after=5)
                        break
        except:
            pass
            

async def filter_invite(bot, message, content=None):
    if message.channel.id in [
        754992725480439809,
        801641781028454420
    ]:
        return
    pattern = r"discord(?:(?:(?:app)?\.com)\/invite|\.gg)/([a-zA-z0-9\-]{2,})(?!\S)"
    matches = re.findall(pattern,message.content, re.MULTILINE)
    if len(matches) > 5:
        await message.delete()
        await message.channel.send(f':warning: {message.author.mention} Invite links are not allowed :warning:', delete_after=5)
        return True
    for code in matches:
        invite = await bot.fetch_invite(code)
        if invite:
            if invite.guild.id != message.guild.id:
                await message.delete()
                await message.channel.send(f':warning: {message.author.mention} Invite links are not allowed :warning:', delete_after=5)
                return True
        

class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
       
        start = time.perf_counter()
        if before.content != after.content: # invoke the command again if it is edited
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)
        if after.guild:
            if after.guild.id == 681882711945641997:
                invite = await filter_invite(self.bot, after)
                if not invite:
                    await filter_links(self.bot, after)
        end = time.perf_counter()
        print(f'parsed message in {end - start}')

    @commands.Cog.listener()
    async def on_message(self, message):
        start = time.perf_counter()
        if message.guild:
            if message.guild.id == 681882711945641997:
                invite = await filter_invite(self.bot, message)
                if not invite:
                    await filter_links(self.bot, message)
        end = time.perf_counter()
        print(f'parsed message in {end - start}')
                    
    @commands.command(name="source", aliases=["github", "code"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def source(self, ctx, *, command: str = None):
        """Displays my full source code or for a specific command.
        To display the source code of a subcommand you can separate it by
        periods, e.g. tag.create for the create subcommand of the tag command
        or by spaces.
        """
        source_url = 'https://github.com/The-Coding-Academy/coding-bot-v4'
        branch = 'main'
        if command is None:
            return await ctx.send(source_url)

        if command == 'help':
            src = type(self.client.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = self.client.get_command(command.replace('.', ' '))
            if obj is None:
                return await ctx.send('Could not find command.')

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith('discord'):
            # not a built-in command
            location = os.path.relpath(filename).replace('\\', '/')
        else:
            location = module.replace('.', '/') + '.py'
            source_url = 'https://github.com/Rapptz/discord.py'
            branch = 'master'

        final_url = f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
        embed = ctx.embed(title='<:githubwhite:804344724621230091> GitHub <:githubwhite:804344724621230091>', description=f'[Click Here]({final_url})')
        await ctx.send(embed=embed)

    @commands.command(name="mystbin",aliases=["mb"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def mystbin(self,ctx,*, code: codeblock_converter = None):
        """Send your code to [Mystb.in](https://mystb.in). You may use codeblocks(by putting your code inside \`\`\`, followed by the language you want to use) Currently, this bot recognizes python and javascript codeblocks, but will support more in the future."""
        code = code.content if code else None
        attachments = None

        if len(ctx.message.attachments) != 0:
            attachments = ctx.message.attachments
        elif ctx.message.reference:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            attachments = message.attachments
        if attachments:
            for attachment in attachments:
                code = await attachment.read()

        if not code:
            return await ctx.send(embed=ctx.error('Please either provide code in the command, attach a file, or react to a message that contains a file.'))
        async with self.bot.http._HTTPClient__session.post('https://mystb.in/documents', data=code) as r:
            res = await r.json()
            key = res["key"]
        embed = ctx.embed(title="Mystb.in Link", description='I pasted your code into a bin, click on the title access it!', url=f'https://mystb.in/{key}').set_thumbnail(url='https://cdn.discordapp.com/avatars/569566608817782824/14f120e096fb515d770eea38f9cddd88.png')
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        embed = ctx.embed(title='PONG!  :ping_pong:',description=f'**<a:DiscordSpin:795546311319355393> Websocket:** {(self.bot.latency * 1000):.2f}ms\n**:repeat: Round-Trip:** Calculating...\n**:elephant: Database:** Calculating...')
        start = time.perf_counter()
        message = await ctx.send(embed=embed)
        await asyncio.sleep(0.5)
        end = time.perf_counter()
        trip = end - start
        embed.description = f'**<a:DiscordSpin:795546311319355393> Websocket:** {(self.bot.latency * 1000):.2f}ms\n**:repeat: Round-Trip:** {(trip * 1000):.2f}ms\n**:elephant: Database:** Calcuating...'
        await message.edit(embed=embed)
        await asyncio.sleep(0.5)
        start = time.perf_counter()
        async with self.bot.pools.config.acquire() as connection:
            await connection.fetchval('SELECT prefixes FROM serverconf WHERE id = 0')
        end = time.perf_counter()
        database = end - start
        embed.description = f'**<a:DiscordSpin:795546311319355393> Websocket:** {(self.bot.latency * 1000):.2f}ms\n**:repeat: Round-Trip:** {(trip * 1000):.2f}ms\n**:elephant: Database:** {(database * 1000):.2f}ms'
        await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
