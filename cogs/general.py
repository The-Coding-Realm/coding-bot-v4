"""
Coding Bot v4
~~~~~~~~~~~~~~~~~~
This file contains elements that are under the following licenses:
Copyright (c) 2015 Rapptz
license MIT, see
https://github.com/Rapptz/RoboDanny/blob/e1c3c28fe20eb192463f7fc224a399141f0d915d/LICENSE.txt
for more details.
"""

import discord
import time
import asyncio
import re
import asyncpg
import os
import url_parser
import inspect
from jishaku.codeblocks import codeblock_converter
from discord.ext import commands


async def filter_links(bot, message):
    if not message.guild:
        return
    if message.author.permissions_in(message.channel).manage_messages:
        return
    regex = (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|'
             r'(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    matches = re.findall(regex, message.content, re.MULTILINE)
    urls = []
    for link in matches:
        try:
            urls = []
            async with bot.http._HTTPClient__session.get(link) as resp:
                urls.append(url_parser.get_url(link)._asdict())
                for redirect in resp.history:
                    urls.append(
                        url_parser.get_url(redirect.real_url)._asdict())
            for url in urls:
                for blocked in [  # "*" means any
                    # [http[s]://][sub.]<name>.<domain>[/path]         # Reason
                    ###########################################################

                    '*.grabify.link/*',                            # Ip Grabber
                    '*.pornhub.com/*',                                   # Porn
                ]:
                    parsed_blocked = url_parser.get_url(
                        blocked.replace('*', '-'))._asdict()
                    for k, v in parsed_blocked.items():
                        if k in ['protocol', 'www', 'dir', 'file', 'fragment',
                                 'query']:
                            continue
                        if v == url[k]:
                            continue
                        if isinstance(v, str):
                            if v.replace('.', '') == '-':
                                continue
                            if k == 'path':
                                if v[1:] == '-':
                                    continue
                        return
                    await message.delete()
                    await message.channel.send((
                        f':warning: {message.author.mention} That link is not '
                        'allowed :warning:'), delete_after=15)
                    return
        except Exception as e:
            print(e)


async def filter_invite(bot, message, content=None):
    if message.author.permissions_in(message.channel).manage_messages:
        return
    if message.channel.id in [
        754992725480439809,
        801641781028454420
    ]:
        return
    pattern = (
        r'discord(?:(?:(?:app)?\.com)\/invite|\.gg)/([a-zA-z0-9\-]{2,})(?!\S)')
    matches = re.findall(pattern, message.content, re.MULTILINE)
    if len(matches) > 5:
        await message.delete()
        await message.channel.send((
            f':warning: {message.author.mention} Invite links are not allowed '
            ':warning:'), delete_after=15)
        return True
    for code in matches:
        try:
            invite = await bot.fetch_invite(code)
        except discord.errors.NotFound:
            invite = None  # invite is fine
        if invite:
            if invite.guild.id not in [message.guild.id, 681882711945641997,
                                       782903894468198450]:
                await message.delete()
                await message.channel.send((
                    f':warning: {message.author.mention} Invite links are not '
                    'allowed :warning:'), delete_after=15)
                return True


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content:  # invoke the command again on edit
            if not after.author.bot:
                ctx = await self.bot.get_context(
                    after, cls=self.bot.helpers.Context)
                await self.bot.invoke(ctx)
        if after.guild:
            if after.guild.id == 681882711945641997:
                invite = await filter_invite(self.bot, after)
                if not invite:
                    await filter_links(self.bot, after)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            if message.guild.id == 681882711945641997:
                invite = await filter_invite(self.bot, message)
                if not invite:
                    await filter_links(self.bot, message)

    @commands.command(name="source", aliases=["github", "code"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def _source(self, ctx, *, command: str = None):
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
            src = type(self.bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = self.bot.get_command(command.replace('.', ' '))
            if obj is None:
                return await ctx.send('Could not find command.')

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

        final_url = (f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L'
                     f'{firstlineno + len(lines) - 1}>')
        github = '<:githubwhite:804344724621230091>'
        embed = ctx.embed(title=f'{github} GitHub {github}',
                          description=f'[Click Here]({final_url})')
        await ctx.send(embed=embed)

    @commands.command(name="mystbin", aliases=["mb"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def _mystbin(self, ctx, *, code: codeblock_converter = None):
        """Send your code to Mystb.in. You may use codeblocks if you want,
        or use code from inside a file."""
        code = code.content if code else None
        attachments = None

        if len(ctx.message.attachments) != 0:
            attachments = ctx.message.attachments
        elif ctx.message.reference:
            message = await ctx.channel.fetch_message(
                ctx.message.reference.message_id)
            attachments = message.attachments
        if attachments:
            for attachment in attachments:
                code = await attachment.read()

        if not code:
            return await ctx.send(embed=ctx.error((
                'Please either provide code in the command, attach a file, or '
                'react to a message that contains a file.')))
        async with self.bot.http._HTTPClient__session.post(
                'https://mystb.in/documents', data=code) as r:
            res = await r.json()
            key = res["key"]
        embed = ctx.embed(title="Mystb.in Link", description=(
            'I pasted your code into a bin, click on the title access it!'),
                          url=f'https://mystb.in/{key}')
        embed.set_thumbnail(url=(
            'https://cdn.discordapp.com/avatars/569566608817782824/'
            '14f120e096fb515d770eea38f9cddd88.png'))
        await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def _ping(self, ctx):
        loading = '<a:DiscordSpin:795546311319355393>'
        embed = ctx.embed(title='PONG!  :ping_pong:', description=(
            f'**{loading} Websocket:** {(self.bot.latency * 1000):.2f}ms\n**'
            ':repeat: Round-Trip:** Calculating...\n**:elephant: Database:** '
            'Calculating...'))
        start = time.perf_counter()
        message = await ctx.send(embed=embed)
        await asyncio.sleep(0.5)
        end = time.perf_counter()
        trip = end - start
        embed.description = (
            f'**{loading} Websocket:** {(self.bot.latency * 1000):.2f}ms\n**'
            f':repeat: Round-Trip:** {(trip * 1000):.2f}ms\n**:elephant: '
            'Database:** Calculating...')
        await message.edit(embed=embed)
        await asyncio.sleep(0.5)
        start = time.perf_counter()
        try:
            async with self.bot.pools.config.acquire() as connection:
                await connection.fetchval(
                    'SELECT prefixes FROM serverconf WHERE id = 0')
            end = time.perf_counter()
            database = end - start
            embed.description = (
                f'**{loading} Websocket:** {(self.bot.latency * 1000):.2f}ms\n'
                f'**:repeat: Round-Trip:** {(trip * 1000):.2f}ms\n**:elephant:'
                f' Database:** {(database * 1000):.2f}ms')
        except asyncpg.exceptions._base.InterfaceError:
            embed.description = (
                f'**{loading} Websocket:** {(self.bot.latency * 1000):.2f}ms'
                f'\n**:repeat: Round-Trip:** {(trip * 1000):.2f}ms\n**'
                ':elephant: Database:** *Did not respond!*')
        await message.edit(embed=embed)

    @commands.command(name='revive', aliases=['revivechat', 'chatrevive',
                                              'revchat', 'chatrev'])
    @commands.guild_only()
    @commands.cooldown(1, 1800, commands.BucketType.guild)
    @commands.has_any_role(729530191109554237, 795136568805294097,
                           725899526350831616)  # Senior Mod +
    async def _revive(self, ctx):
        mention = ctx.guild.get_role(759219083639783448).mention
        embed = ctx.embed(
            title='Revive Chat Ping!',
            description='Come back to chat and make it alive again!')
        await ctx.send(content=mention, embed=embed)

    @commands.command(name='reinvoke', aliases=['re'])
    async def _reinvoke(self, ctx):
        """
        Reinvoke a command, running it again. This does NOT bypass any permissions checks
        """
        try:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        except discord.errors.NotFound:
            return await ctx.send(embed=ctx.error('I couldn\'t find that message'))
        if message.author == ctx.author:
            await ctx.message.add_reaction('\U00002705')
            context = await self.bot.get_context(
                message, cls=self.bot.helpers.Context)
            await self.bot.invoke(context)
        else:
            await ctx.send(embed=ctx.error('That isn\'t your message'))

def setup(bot):
    bot.add_cog(General(bot))
