import json
import traceback
import discord
import sys
import datetime
import asyncpg
import asyncio
import discord
import inspect
from discord.ext import commands
from discord_slash import SlashContext as SlashCtx


class Bot(commands.Bot):

    async def logout(self, *args, **kwargs):
        if hasattr(self.pools,'config'):
            try:
                await asyncio.wait_for(self.pools.config.close(), timeout=5)
            except Exception as e:
                print(e)
        if hasattr(self, 'sr_api'):
            try:
                await asyncio.wait_for(self.sr_api.close(), timeout=5)
            except Exception as e:
                print(e)
        if hasattr(self,'wavelink'):
            if not self.wavelink.session.closed:
                await asyncio.wait_for(self.wavelink.session.close(), timeout=5)
        await super().logout(*args, **kwargs)

class Embed(discord.Embed):
    def __repr__(self):
        return self.description or ''

class Context(commands.Context):

    Embed = Embed

    def embed(self, description=None, *args,**kwargs):
        default = {
            'timestamp': self.message.created_at,
            'description': description
        }
        default.update(kwargs)
        return_embed = self.Embed(*args,**default)
        return_embed.set_footer(icon_url=self.author.avatar_url,text=f'Requested by {self.author}')
        return return_embed

    def error(self, description=None, *args,**kwargs):
        default = {
            'title': 'Error',
            'color': discord.Color.red(),
            'timestamp': self.message.created_at,
            'description': description
        }
        default.update(kwargs)
        return_embed = self.Embed(*args,**default)
        return_embed.set_author(name=self.author,icon_url=self.author.avatar_url)
        return_embed.set_footer(icon_url=self.bot.user.avatar_url,text=f'If you think this is a mistake please contact {self.bot.get_user(self.bot.owner_ids[0])}')
        return return_embed


async def init_connection(connection):
    await connection.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )

def storage(bot, key=None, value=None, method=None, override=False):
    try:
        with open('./storage/config.json','r') as f:
            data = json.load(f)
    except:
        with open('./storage/config.json','w+') as f:
            f.write('{}')
        with open('./storage/config.json','r') as f:
            data = json.load(f)
    data['cogs'] = data.get('cogs', [])
    data['blacklisted'] = data.get('blacklisted', [])
    data['disabled'] = data.get('disabled', False)
    data['owners'] = data.get('owners', [690420846774321221])
    bot.restart_channel = data.get('restart_channel', None)
    data['restart_channel'] = None
    if key and value:
        if method == 'append':
            if not value in data[key] or override:
                data[key].append(value)
        elif method == 'remove':
            if value in data[key] or override:
                data[key].remove(value)
        else:
            data[key] = value
    with open('./storage/config.json','w') as f:
        json.dump(data,f,indent=4)
    return data

async def prepare(bot, guild=None):
    try:
        connection = await bot.pools.config.acquire()
        await bot.pools.config.release(connection)
    except:
        try:
            bot.pools.config = await asyncio.wait_for(asyncpg.create_pool(database='codingbot', init=init_connection), timeout=5)
        except:
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
            data = await connection.fetchrow('SELECT * FROM serverconf WHERE id = $1', guild.id)
            bot.server_cache[guild.id] = bot.server_cache.get(guild.id, {
                    'prefixes': [],
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
    except:
        await prepare(ctx.bot, ctx.guild)
        try:
            data = ctx.bot.server_cache[ctx.guild.id].copy()
        except:
            data = {}
    ids_to_check = [ctx.guild.id, ctx.channel.id, ctx.author.id] + [r.id for r in ctx.author.roles]
    for id_ in ids_to_check:
        data[int(id_)] = data.get(int(id_), [])
        if True in data[int(id_)] or ctx.command.qualified_name in data[int(id_)]:
            return True
    return False

async def prefix(bot, message):
    return_prefixes = bot.default_prefixes
    if not message.guild:
        return_prefixes.append('')
    else:
        try:
            data = bot.server_cache[message.guild.id]['prefixes']
        except:
            await prepare(bot, message.guild)
            try:
                data = bot.server_cache[message.guild.id]['prefixes']
            except:
                data = bot.default_prefixes
        return_prefixes = data or return_prefixes
    return return_prefixes


async def log_command_error(ctx,error,handled):
    if not handled:
        channel = ctx.bot.get_channel(787461422896513104)
    else:
        channel = ctx.bot.get_channel(787476834689744926)
    title = 'Ignoring exception in command {}:'.format(ctx.command)
    err = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    try:
        embed = discord.Embed(title=title,description=f'```py\n{err}```',timestamp=ctx.message.created_at,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url)
        await channel.send(embed=embed)
    except:
        try:
            await channel.send(f"**<@{ctx.bot.owner_ids[0]}> An error occurred but I couldn't log it here**")
        except:
            pass
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    finally:
        return

async def log_error(bot, event_method, *args, **kwargs):
    channel = bot.get_channel(812359854890156073)
    try:
        title = 'Ignoring exception in {}'.format(event_method)
        err = ''.join(traceback.format_exc())
        embed = discord.Embed(title=title,description=f'```py\n{err}```',timestamp=datetime.datetime.utcnow(),color=discord.Color.red())
        await channel.send(embed=embed)
    except:
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()
