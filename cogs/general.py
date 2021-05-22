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
import aiohttp
import asyncpg
import os
import sys
import traceback
import url_parser
import humanize
import inspect
from jishaku.codeblocks import codeblock_converter
from discord.ext import commands, menus


class ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        try:
            default = {
                # 'response_class': ClientResponse,
                'rickroll_queries': ["rickroll","rick roll","rick astley","never gonna give you up"],
                'block': [],
                'timeout': aiohttp.ClientTimeout(total=300, sock_read=10)  # to prevent attacks relating to sending massive payload and lagging the client
            }
            default.update(kwargs)

            self.rickroll_regex = re.compile('|'.join(default['rickroll_queries']), re.IGNORECASE)
            self.block_list = default['block']
            del default['rickroll_queries']
            del default['block']
            super().__init__(*args, **default)
        except:
            raise
            super().__init__(*args, **kwargs)

    async def _request(self, *args, **kwargs):
        req = await super()._request(*args, **kwargs)
        regex = self.rickroll_regex
        content = str(await req.content.read())
        req.rickroll = bool(regex.search(content))
        blocked_urls = self.block_list
        urls = [str(redirect.url_obj) for redirect in req.history]
        req.blocked = bool(await check_links(urls, blocked_urls))
        return req


class RedirectMenu(menus.ListPageSource):
    def __init__(self, data, ctx, rickroll=False):
        grouped = [' \n'.join(data[i:i + 5]) for i in range(0, len(data), 5)]
        super().__init__(grouped, per_page=1)
        self.ctx = ctx
        self.rickroll = rickroll

    async def format_page(self, menu, entry):
        embed = self.ctx.embed(title='Redirect Checker', description=entry)
        embed.set_footer(text=f'Page {menu.current_page + 1}/{menu._source.get_max_pages()} | ' + embed.footer.text, icon_url=embed.footer.icon_url)
        if self.rickroll:
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/814195797380825088/844955986674712646/rick.gif')
        return embed
    
async def check_link_base(url, block_list):
    url = url_parser.get_url(url)._asdict()
    for blocked in block_list:
        parsed_blocked = url_parser.get_url(
            blocked.replace('*', '-'))._asdict()
        delete = True
        for k in ['sub_domain', 'domain', 'top_domain', 'path']:
            rep = parsed_blocked[k]
            if k == 'path':
                rep = rep[1:]
            if url[k] != rep and rep.replace('.','') != '-':
                delete = False
                break
        if delete:
            return True

async def check_links(urls, block_list):
    for url in urls:
        if await check_link_base(url, block_list):
            return True


def convert_link(content):
    base_regex = r'(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$'
    if re.match(r'^http[s]?://' + base_regex, content):
        return content
    elif re.match(r'^' + base_regex, content):
        return 'https://' + content
    else:
        raise ValueError('Not a link')

async def check_link(url):
    return await check_link_base(url, [  # "*" means any
        # [http[s]://][sub.]<name>.<tld>[/path]                 # Reason
        ################################################################

        '*.grabify.link/*',                                 # Ip Grabber
        '*.pornhub.com/*',                                        # Porn
        '*.guilded.gg/*',                                  # Advertising
        '*.tornadus.net/orange',                       # Discord Crasher
        'giant.gfycat.com/SizzlingScrawnyBudgie.mp4',  # Discord Crasher
    ])

async def find_links(cog, content, channel=None):
    regex = (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|'
             r'(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    matches = re.findall(regex, content, re.MULTILINE)
    urls = []
    rickroll = False
    for link in matches:
        location = link
        try:
            for i in range(10):
                if await check_link(location) or await check_invite(cog.bot, location, channel): 
                    return 1
                async with cog.session.get(location, allow_redirects=False) as resp:
                    location = resp.headers.get('Location')
                    if resp.rickroll:
                        rickroll = True
                    if location == resp.real_url or location is None:
                        break
        except Exception as error:
            print('Ignoring exception in url filter {}:'.format(content), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    if rickroll:
        return 2


async def filter_links(cog, message):
    if ((not isinstance(message.author, discord.Member)) or
            message.author.permissions_in(message.channel).manage_messages):
        return
    checked = await find_links(cog, message.content, message.channel)
    if checked == 1:
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass
        await message.channel.send((
            f':warning: {message.author.mention} That link is not '
            'allowed :warning:'), delete_after=15)
    elif checked == 2:
        await message.add_reaction(cog.bot.get_emoji(844957433511542794))
    return

async def check_invite(bot, content, channel=None):
    pattern = (
        r'discord(?:(?:(?:app)?\.com)\/invite|\.gg)/([a-zA-z0-9\-]{2,})\b')
    matches = re.findall(pattern, content, re.MULTILINE)
    if channel.id in [
        754992725480439809,
        801641781028454420
    ]:
        return False
    if len(matches) > 5:
        return True
    for code in matches:
        try:
            invite = await bot.fetch_invite(code)
        except discord.errors.NotFound:
            invite = None  # invite is fine
        if invite:
            if invite.guild.id not in [
                    channel.guild.id if channel else None,
                    681882711945641997,  # TCA
                    782903894468198450,  # Swasville
                    336642139381301249,  # Discord.py
                    267624335836053506,  # Python
                    412754940885467146,  # Blurple
                    613425648685547541,  # Discord Developers
                    ]:
                return True
    
    return False


async def filter_invite(bot, message=None, content=None):
    if ((not isinstance(message.author, discord.Member)) or
            message.author.permissions_in(message.channel).manage_messages):
        return
    matched = await check_invite(bot, message.content, message.channel)
    if matched:
        await message.delete()
        await message.channel.send((
            f':warning: {message.author.mention} Invite links are not allowed '
            ':warning:'), delete_after=15)
        return True
    
def gcd(a, b):
    """
    calculate the greatest common divisor of a and b.
    """
    while b:
        a, b = b, a % b
    return a


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession()

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
                    await filter_links(self, after)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            if message.guild.id == 681882711945641997:
                invite = await filter_invite(self.bot, message)
                if not invite:
                    await filter_links(self, message)

    @commands.command(name="source", aliases=["github", "code"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def _source(self, ctx, *, command: str = None):
        """Displays my full source code or for a specific command.
        To display the source code of a subcommand you can separate it by
        periods or spaces.
        """
        github = '<:githubwhite:804344724621230091>'
        embed = ctx.embed(title=f'{github} GitHub (Click Here) {github}')
        source_url = 'https://github.com/The-Coding-Academy/coding-bot-v4'
        branch = 'main'
        if command is None:
            embed.url = source_url
            return await ctx.send(embed=embed)

        if command == 'help':
            src = type(self.bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = self.bot.get_command(command.replace('.', ' '))
            if obj is None:
                return await ctx.send(embed=ctx.error('Could not find command.'))

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

        final_url = (f'{source_url}/blob/{branch}/{location}#L{firstlineno}-L'
                     f'{firstlineno + len(lines) - 1}')
        embed.url = final_url
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
        ws_ping = f'{(self.bot.latency * 1000):.2f}ms ' \
                  f'({humanize.precisedelta(datetime.timedelta(seconds=self.bot.latency))})'
        embed = ctx.embed(title='PONG!  :ping_pong:', description=(
            f'**{loading} Websocket:** {ws_ping}\n**'
            ':repeat: Round-Trip:** Calculating...\n**:elephant: Database:** '
            'Calculating...'))
        start = time.perf_counter()
        message = await ctx.send(embed=embed)
        end = time.perf_counter()
        await asyncio.sleep(0.5)
        trip = end - start
        rt_ping = f'{(trip * 1000):.2f}ms ({humanize.precisedelta(datetime.timedelta(seconds=trip))})'
        embed.description = (
            f'**{loading} Websocket:** {ws_ping}\n**'
            f':repeat: Round-Trip:** {rt_ping}\n**:elephant: '
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
            db_ping = f'{(database * 1000):.2f}ms ({humanize.precisedelta(datetime.timedelta(seconds=database))})'
            embed.description = (
                f'**{loading} Websocket:** {ws_ping}\n'
                f'**:repeat: Round-Trip:** {rt_ping}\n**:elephant:'
                f' Database:** {db_ping}')
        except asyncpg.exceptions._base.InterfaceError:
            embed.description = (
                f'**{loading} Websocket:** {ws_ping}'
                f'\n**:repeat: Round-Trip:** {rt_ping}\n**'
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
            
    @commands.command(name="joined")
    async def _joined(self, ctx, position: int):
        async with ctx.typing():
            if position > ctx.guild.member_count:
                return await ctx.send(embed=ctx.error('There are not that many members here'))
            all_members = list(ctx.guild.members)
            all_members.sort(key=lambda m: m.joined_at)
            def ord(n):
                return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))
            embed = ctx.embed(title = f"The {ord(position)} person to join is: ", description=all_members[position - 1].mention)
            await ctx.send(embed=embed)
        
    @commands.command(name="joinposition", aliases=['joinpos'])
    async def _join_position(self, ctx, member: discord.Member):
        async with ctx.typing():
            all_members = list(ctx.guild.members)
            all_members.sort(key=lambda m: m.joined_at)
            def ord(n):
                return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))
            embed = ctx.embed(title = "Member info", description = f'{member.mention} was the {ord(all_members.index(member) + 1)} person to join')
            await ctx.send(embed=embed)
            
    @commands.group(invoke_without_command=True)
    async def math(self, ctx):
        await ctx.send_help('math')
        
    @math.command(name='simplify')
    async def _math_simplify(self, ctx, fraction):
        try:
            numerator, denominator = (int(x) for x in fraction.split('/'))
        except:
            return await ctx.send_error('Not a fraction')
        if denominator == 0:
            return await ctx.send_error("Division by 0")

        common_divisor = gcd(numerator, denominator)
        (reduced_numerator, reduced_denominator) = (numerator / common_divisor, denominator / common_divisor)

        if reduced_denominator == 1:
            final = int(reduced_numerator)
        elif common_divisor == 1:
            final = f'{int(numerator)}/{int(denominator)}'
        else:
            final = f'{int(reduced_numerator)}/{int(reduced_denominator)}'
        await ctx.send(embed=ctx.embed(title='Reduced Fraction', description=final))
        
    @commands.command(name='redirects', aliases=['checklink'])
    async def _redirects(self, ctx, url: convert_link):
        hl = []
        status_map = {
            1: '\U0001f504',
            2: '\U00002705',
            3: '\U000027a1',
            4: '\U0000274c',
            5: '\U000026a0'
            }
        
        def build_string(res):
            return f'{status_map[int(res.status / 100)]} [{(res.url_obj.host + res.url_obj.path).strip("/")}]({res.url_obj}) ({res.status} {res.reason})'
        
        rickroll = False
        try:
            async with ctx.typing():
                r = await self.session.get(url)
                for res in r.history:
                    hl.append(build_string(res))
                hl.append(build_string(r))
                rickroll = r.rickroll
        except:
            return await ctx.send_error(f'Could not reach "{url}"')
        pages = menus.MenuPages(source=RedirectMenu(hl, ctx, rickroll=rickroll), delete_message_after=True)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(General(bot))
