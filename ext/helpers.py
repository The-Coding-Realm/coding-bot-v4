import json
import traceback
import discord
import sys
import datetime
import asyncpg
import random
import asyncio
from discord.ext import commands


class Bot(commands.Bot):

    async def logout(self, *args, **kwargs):
        if hasattr(self.pools, 'config'):
            try:
                await asyncio.wait_for(self.pools.config.close(), timeout=5)
            except Exception as e:
                print(e)
        if hasattr(self, 'sr_api'):
            try:
                await asyncio.wait_for(self.sr_api.close(), timeout=5)
            except Exception as e:
                print(e)
        if hasattr(self, 'wavelink'):
            if not self.wavelink.session.closed:
                await asyncio.wait_for(self.wavelink.session.close(),
                                       timeout=5)
        await super().logout(*args, **kwargs)


class Embed(discord.Embed):
    def __repr__(self):
        return self.description or ''


class Context(commands.Context):

    Embed = Embed

    def embed(self, description=None, *args, **kwargs):
        discord_colors = {
            'Blurple': 0x5865F2,
            'Green': 0x57F287,
            'Yellow': 0xFEE75C,
            'Fuchsia': 0xEB459E,
            'Red': 0xed4245,
            'White': 0xFFFFFE,
            'Black': 0x23272A
            }
        default = {
            'timestamp': self.message.created_at,
            'description': description,
            'color': random.choice([discord_colors[color] for color in discord_colors])
            }
        default.update(kwargs)
        return_embed = self.Embed(*args, **default)
        return_embed.set_footer(icon_url=self.author.avatar.url,
                                text=f'Requested by {self.author}')
        return return_embed

    def error(self, description=None, *args, **kwargs):
        default = {
            'title': 'Error',
            'color': discord.Color.red(),
            'timestamp': self.message.created_at,
            'description': description
        }
        default.update(kwargs)
        return_embed = self.Embed(*args, **default)
        return_embed.set_author(name=self.author,
                                icon_url=self.author.avatar.url)
        return_embed.set_footer(icon_url=self.bot.user.avatar.url, text=(
            'If you think this is a mistake please contact '
            f'{self.bot.get_user(self.bot.owner_ids[0])}'))
        return return_embed

    def success(self, description=None, *args, **kwargs):
        default = {
            'title': 'Success',
            'color': discord.Color.green(),
            'timestamp': self.message.created_at,
            'description': description
            }
        default.update(kwargs)
        return_embed = self.Embed(*args, **default)
        return_embed.set_author(name=self.author,
                                icon_url=self.author.avatar.url)
        return_embed.set_footer(icon_url=self.bot.user.avatar.url, text='Action successful')
        return return_embed

    async def send_embed(self, *args, **kwargs):
        await self.send(embed=self.embed(*args, **kwargs))

    async def send_error(self, *args, **kwargs):
        await self.send(embed=self.error(*args, **kwargs))

    async def send_success(self, *args, **kwargs):
        await self.send(embed=self.success(*args, **kwargs))


async def init_connection(connection):
    await connection.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )


def storage(bot, key=None, value=None, method=None, override=False):
    try:
        with open('./storage/config.json', 'r') as f:
            data = json.load(f)
    except OSError:
        with open('./storage/config.json', 'w+') as f:
            f.write('{}')
        with open('./storage/config.json', 'r') as f:
            data = json.load(f)
    data['cogs'] = data.get('cogs', [])
    data['blacklisted'] = data.get('blacklisted', [])
    data['disabled'] = data.get('disabled', False)
    if bot.default_owner:
        temp_owner = int(bot.default_owner)
    else:
        temp_owner = 690420846774321221
    data['owners'] = data.get('owners', [temp_owner])
    bot.restart_channel = data.get('restart_channel', None)
    data['restart_channel'] = None
    if key and value is not None:
        if method == 'append':
            if value not in data[key] or override:
                data[key].append(value)
        elif method == 'remove':
            if value in data[key] or override:
                data[key].remove(value)
        else:
            data[key] = value
    with open('./storage/config.json', 'w') as f:
        json.dump(data, f, indent=4)
    return data


async def prepare(bot, guild=None):
    try:
        connection = await bot.pools.config.acquire()
        await bot.pools.config.release(connection)
    except asyncpg.exceptions._base.InterfaceError:
        try:
            bot.pools.config = await asyncio.wait_for(asyncpg.create_pool(
                database='codingbot_db', init=init_connection), timeout=5)
            connection = await bot.pools.config.acquire()
            await bot.pools.config.release(connection)
        except (OSError, asyncpg.exceptions._base.InterfaceError,
                asyncio.exceptions.TimeoutError):
            if guild:
                bot.server_cache[guild.id] = bot.server_cache.get(guild.id, {
                    'prefixes': bot.default_prefixes.copy(),
                    'commands': {}
                })
            return
    async with bot.pools.config.acquire() as connection:
        if guild:
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS serverconf (
                    id bigint,
                    commands json,
                    prefixes text[]
                );
            ''')
            data = await connection.fetchrow(
                'SELECT * FROM serverconf WHERE id = $1', guild.id)
            bot.server_cache[guild.id] = bot.server_cache.get(guild.id, {
                'prefixes': bot.default_prefixes.copy(),
                'commands': {}
            })
            if data:
                if isinstance(data['prefixes'], list):
                    bot.server_cache[guild.id]['prefixes'] = data['prefixes']
                if isinstance(data['commands'], dict):
                    bot.server_cache[guild.id]['commands'] = data['commands']


async def is_disabled(ctx):
    if not ctx.guild:
        return False
    try:
        data = ctx.bot.server_cache[ctx.guild.id].copy()
    except KeyError:
        await prepare(ctx.bot, ctx.guild)
        try:
            data = ctx.bot.server_cache[ctx.guild.id].copy()
        except KeyError:
            data = {}
    ids_to_check = [ctx.guild.id, ctx.channel.id, ctx.author.id]
    ids_to_check += [r.id for r in ctx.author.roles]
    for id_ in ids_to_check:
        data[int(id_)] = data.get(int(id_), [])
        if (True in data[int(id_)]
                or ctx.command.qualified_name in data[int(id_)]):
            return True
    return False


async def prefix(bot, message):
    return_prefixes = bot.default_prefixes.copy()
    if not message.guild:
        return_prefixes.append('')
    else:
        try:
            data = bot.server_cache[message.guild.id]['prefixes']
        except KeyError:
            try:
                bot.server_cache[message.guild.id] = bot.server_cache.get(
                    message.guild.id, {
                        'prefixes': return_prefixes,
                        'commands': {}
                    })
                bot.loop.create_task(prepare(bot, message.guild))
                data = bot.server_cache[message.guild.id]['prefixes']
            except KeyError:
                data = bot.default_prefixes
        return_prefixes = data or return_prefixes
    return return_prefixes


async def log_command_error(ctx, error, handled):
    if not handled:
        channel = ctx.bot.get_channel(826862029347749969)
    else:
        channel = ctx.bot.get_channel(826862028815597609)
    title = 'Ignoring exception in command {}:'.format(ctx.command)
    err = ''.join(traceback.format_exception(
        type(error), error, error.__traceback__))
    try:
        embed = discord.Embed(title=title, description=f'```py\n{err}```',
                              timestamp=ctx.message.created_at,
                              color=discord.Color.red())
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await channel.send(embed=embed)
    except discord.errors.Forbidden:
        try:
            await channel.send((f"**<@{ctx.bot.owner_ids[0]}> An error "
                                "occurred but I couldn't log it here**"))
        except discord.errors.Forbidden:
            pass
        print('Ignoring exception in command {}:'.format(ctx.command),
              file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__,
                                  file=sys.stderr)
    finally:
        return


async def log_error(bot, event_method, *args, **kwargs):
    channel = bot.get_channel(826861610173333595)
    try:
        title = 'Ignoring exception in {}'.format(event_method)
        err = ''.join(traceback.format_exc())
        embed = discord.Embed(title=title, description=f'```py\n{err}```',
                              timestamp=datetime.datetime.now(datetime.timezone.utc),
                              color=discord.Color.red())
        await channel.send(embed=embed)
    except discord.errors.Forbidden:
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()
