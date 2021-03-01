import discord
import os
import json
import sys 
import traceback
import datetime
import inspect
import math
import random
import asyncio
import DiscordUtils
import humanize
import asyncpg
import pytest
import ext.helpers as helpers
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext


async def prefix(bot, message):
    return commands.when_mentioned_or(*(await helpers.prefix(bot, message)))(bot, message)

class CustomHelp(commands.HelpCommand):
    """This is an example of a HelpCommand that utilizes embeds.
    It's pretty basic but it lacks some nuances that people might expect.
    1. It breaks if you have more than 25 cogs or more than 25 subcommands. (Most people don't reach this)
    2. It doesn't DM users. To do this, you have to override `get_destination`. It's simple.
    Other than those two things this is a basic skeleton to get you started. It should
    be simple to modify if you desire some other behaviour.
    
    To use this, pass it to the bot constructor e.g.:
       
    bot = commands.Bot(help_command=EmbedHelpCommand())
    """

    def get_ending_note(self):
        return 'Use {0}{1} [command] for more info on a command.'.format(self.clean_prefix, self.invoked_with)

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='Bot Commands')
        description = self.context.bot.description
        if description:
            embed.description = description

        for cog, commands in mapping.items():
            name = 'No Category' if cog is None else cog.qualified_name
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                value = '\u2002'.join(c.name for c in commands)
                if cog and cog.description:
                    value = '{0}\n{1}'.format(cog.description, value)

                embed.add_field(name=name, value=value)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title='{0.qualified_name} Commands'.format(cog))
        if cog.description:
            embed.description = cog.description

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(name=self.get_command_signature(command), value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=group.qualified_name)
        if group.help:
            embed.description = group.help

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            for command in filtered:
                embed.add_field(name=self.get_command_signature(command), value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    # This makes it so it uses the function above
    # Less work for us to do since they're both similar.
    # If you want to make regular command help look different then override it
    send_command_help = send_group_help

bot = helpers.Bot(command_prefix=prefix,description='Coding Bot v4',case_insensitive=True,embed_color=discord.Color.blurple(),intents=discord.Intents.all(), help_command=CustomHelp())

load_dotenv()
if len(sys.argv) > 2:
    bot.token = sys.argv[2]
else:
    bot.token = os.getenv('BOT_TOKEN')
bot.default_owner = os.getenv('OWNER_ID')
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ['JISHAKU_RETAIN'] = "True"
from jishaku.modules import ExtensionConverter # has to be after environ stuff ree
data = helpers.storage(bot)


class pools:
    config = asyncpg.create_pool(database="codingbot", init=helpers.init_connection)

bot.helpers = helpers
bot.tracker = DiscordUtils.InviteTracker(bot)
bot.default_prefixes = [',']
bot.server_cache = {}
bot.pools = pools
bot.owner_id = None
bot.owner_ids = data['owners']
bot.blacklisted = data['blacklisted']
bot.disabled = data['disabled']
bot.active_cogs = data['cogs']
bot.load_extension('jishaku')
bot.processing_commands = 0
bot.slash = SlashCommand(bot, sync_commands=True)
for cog in bot.active_cogs:
    try:
        bot.load_extension(cog)
        print(cog)
    except:
        if __name__ == "__main__":
            print(f'!!! {cog} !!!')
        else:
            raise

@bot.event
async def on_message(message):
    ctx = await bot.get_context(message, cls=helpers.Context)
    await bot.invoke(ctx)

@bot.event
async def on_ready():
    await bot.tracker.cache_invites()
    await helpers.prepare(bot)
    print('Ready')
    if bot.restart_channel:
        channel = bot.get_channel(bot.restart_channel)
        bot.restart_channel = None
        embed = discord.Embed(title="I'm back online!")
        await channel.send(embed=embed)
    if not __name__ == "__main__":
        await bot.logout()
        
@bot.event
async def on_invite_create(invite):
    await bot.tracker.update_invite_cache(invite)

@bot.event
async def on_guild_join(guild):
    await bot.tracker.update_guild_cache(guild)

@bot.event
async def on_invite_delete(invite):
    await bot.tracker.remove_invite_cache(invite)

@bot.event
async def on_guild_remove(guild):
    await bot.tracker.remove_guild_cache(guild)
    
@bot.event
async def on_member_join(member):
    if not member.guild.id == 681882711945641997:
        return
    try:
        inviter = await bot.tracker.fetch_inviter(member)
    except:
        inviter = None
    embed = discord.Embed(title='Welcome to The Coding Academy!',
                          description=f'''Welcome {member.mention}, we're glad you joined! Before you get started, here are some things to check out:
**Read the Rules:** {guild.rules_channel.mention}
**Get roles:** <#816069037737377852> and <#816069037737377852>
**Want help? Read here:** <#816069037737377852> and <#816069037737377852>
''',
                          timestamp=datetime.datetime.utcnow())
    message = f'{member} joined, {"invited by " + str(inviter) + "(ID: " + inviter.id + ")" if inviter else "but I could not find who invited them"}'
    channel = member.guild.get_channel(743817386792058971)
    await channel.send(content=message, embed=embed)

@bot.event
async def on_error(event_method, *args, **kwargs):
    await helpers.log_error(bot, event_method, *args, *kwargs)

@bot.event
async def on_command_error(ctx, error):
    exception = error
    if hasattr(ctx.command, 'on_error'):
        pass
    #ignored = (commands.MissingRequiredArgument, commands.BadArgument, commands.NoPrivateMessage, commands.CheckFailure, commands.CommandNotFound, commands.DisabledCommand, commands.CommandInvokeError, commands.TooManyArguments, commands.UserInputError, commands.CommandOnCooldown, commands.NotOwner, commands.MissingPermissions, commands.BotMissingPermissions)   
    error = getattr(error, 'original', error)

    if ctx.author.id in ctx.bot.owner_ids:
        if isinstance(error, commands.DisabledCommand) or isinstance(error, commands.CommandOnCooldown) or isinstance(error, commands.MissingPermissions) or isinstance(error, commands.MaxConcurrencyReached):
            return await ctx.reinvoke()

    if isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.NoPrivateMessage) or isinstance(error, commands.CheckFailure) or isinstance(error, commands.DisabledCommand) or isinstance(error, commands.CommandInvokeError) or isinstance(error, commands.TooManyArguments) or isinstance(error, commands.UserInputError) or isinstance(error, commands.NotOwner) or isinstance(error, commands.MissingPermissions) or isinstance(error, commands.BotMissingPermissions) or isinstance(error, commands.MaxConcurrencyReached) or isinstance(error, commands.CommandNotFound):
        await helpers.log_command_error(ctx,exception,True)
        if not isinstance(error, commands.CommandNotFound):
            if await helpers.is_disabled(ctx):
                return
        text = None
        if isinstance(error, commands.CheckFailure):
            if bot.disabled:
                text = 'The bot is currently disabled. It will be back soon.'
        if not isinstance(error, commands.CommandNotFound):
            error=str(error)
            await ctx.send(embed=ctx.embed(title="Error",description=text or error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url).set_footer(icon_url=bot.user.avatar_url,text=f'If you think this is a mistake please contact {bot.get_user(ctx.bot.owner_ids[0])}'))

    elif isinstance(error, commands.CommandOnCooldown):
        await helpers.log_command_error(ctx,exception,True)
        time = datetime.timedelta(seconds=math.ceil(error.retry_after))
        error = f'You are on cooldown. Try again after {humanize.precisedelta(time)}'
        await ctx.send(embed=ctx.embed(title="Error",description=error,color=discord.Color.red()).set_author(name=ctx.author,icon_url=ctx.author.avatar_url).set_footer(icon_url=bot.user.avatar_url,text=f'If you think this is a mistake please contact {bot.get_user(ctx.bot.owner_ids[0])}'))
    
    else:
        try:
            embed = ctx.embed(title='Oh no!',description=f"An error occurred. My developer has been notified of it, but if it continues to occur please DM <@{ctx.bot.owner_ids[0]}>",color=discord.Color.red())
            await ctx.send(embed=embed)
        except:
            pass
        await helpers.log_command_error(ctx,exception,False)

class Developer(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load',aliases=['l'])
    @commands.is_owner()
    async def _load(self, ctx, cog, save: bool=False):
        if save:
            helpers.storage(self.bot, key='cogs', value=cog, method='append')
        self.bot.load_extension(cog)
        embed = ctx.embed(title='Success', description='Saved Preference' if save else None, color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(name='unload',aliases=['u'])
    @commands.is_owner()
    async def _unload(self, ctx, cog, save: bool=False):
        if save:
            helpers.storage(self.bot, key='cogs', value=cog, method='remove')
        self.bot.unload_extension(cog)
        embed = ctx.embed(title='Success',description='Saved Preference' if save else None,color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(name='reload',aliases=['r'])
    @commands.is_owner()
    async def _reload(self, ctx, cog):
        self.bot.reload_extension(cog)
        embed = ctx.embed(title='Success',color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(name='loadall', aliases=['la'])
    @commands.is_owner()
    async def _loadall(self, ctx):
        data = helpers.storage(self.bot)
        cogs = {
            'loaded': [],
            'not': []
        }
        for cog in data['cogs']:
            if cog in bot.extensions:
                continue
            try:
                self.bot.load_extension(cog)
                cogs['loaded'].append(cog)
            except:
                cogs['not'].append(cog)
        embed = ctx.embed(title='Load all cogs',description='\n'.join([('\U00002705' if cog in cogs['loaded'] else '\U0000274c') + cog for cog in data['cogs']]))
        await ctx.send(embed=embed)

    @commands.command(name='unloadall',aliases=['ua'])
    @commands.is_owner()
    async def _unloadall(self, ctx):
        data = helpers.storage(self.bot)
        cogs = {
            'unloaded': [],
            'not': []
        }
        processing = bot.extensions.copy()
        for cog in processing:
            try:
                self.bot.unload_extension(cog)
                cogs['unloaded'].append(cog)
            except:
                cogs['not'].append(cog)
        embed = ctx.embed(title='Unload all cogs',description='\n'.join([('\U00002705' if cog in cogs['unloaded'] else '\U0000274c') + cog for cog in processing]))
        await ctx.send(embed=embed)

    @commands.command(name='reloadall',aliases=['ra'])
    @commands.is_owner()
    async def _reloadall(self, ctx):
        data = helpers.storage(self.bot)
        cogs = {
            'reloaded': [],
            'not': []
        }
        processing = bot.extensions.copy()
        for cog in processing:
            try:
                self.bot.reload_extension(cog)
                cogs['reloaded'].append(cog)
            except:
                cogs['not'].append(cog)
        embed = ctx.embed(title='Reload all cogs',description='\n'.join([('\U00002705' if cog in cogs['reloaded'] else '\U0000274c') + cog for cog in processing]))
        await ctx.send(embed=embed)

bot.add_cog(Developer(bot))


@bot.before_invoke
async def before_invoke(ctx):
    bot.processing_commands += 1

@bot.after_invoke
async def after_invoke(ctx):
    bot.processing_commands -= 1

@tasks.loop(seconds=60)
async def status_change():
    statuses = ['over TCA', 'you', 'swas', '@everyone', 'general chat']
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(statuses) + ' | ' + bot.default_prefixes[0] + 'help'))

@status_change.before_loop
async def before_status_change():
    await bot.wait_until_ready()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'Starting up...'))
    await asyncio.sleep(15)

@bot.check
def blacklist(ctx):
    return not ctx.author.id in bot.blacklisted or ctx.author.id in bot.owner_ids

@bot.check
def disabled(ctx):
    return (not bot.disabled) or ctx.author.id in bot.owner_ids

@bot.check
async def disabled_command(ctx):
    return (not await helpers.is_disabled(ctx)) or ctx.author.id in bot.owner_ids or ctx.author.id == ctx.guild.owner.id


@bot.slash.slash(name='help', description='Get the help for the bot')
async def slash_help(ctx: SlashContext):
    await ctx.send(embeds=[discord.Embed(title='Hello There!', description=f'I use special command prefixes for my commands. Please type \n{bot.user.mention + " help"} \nfor my full help menu!')])

@bot.slash.slash(name='invite', description='Invite the bot to your server')
async def slash_invite(ctx: SlashContext):
    embed = discord.Embed(title='Invite', description=f"[Click Here](https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands) to invite me!", timestamp=datetime.datetime.utcnow())
    await ctx.send(embeds=[embed])

status_change.start()
if __name__ == "__main__":
    bot.run(bot.token)
