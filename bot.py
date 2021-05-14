import discord
import os
import sys
import unicodedata
import datetime
import math
import random
import asyncio
import DiscordUtils
import io
import humanize
import aiohttp
import asyncpg
import ext.helpers as helpers
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext


async def prefix(bot_, message):
    return commands.when_mentioned_or(*(await helpers.prefix(bot_, message)))(
        bot_, message)


class CustomHelp(commands.HelpCommand):

    def get_ending_note(self):
        return 'Use {0}{1} [command] for more info on a command.'.format(
            self.clean_prefix, self.invoked_with)

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

        for cog_, cmds in mapping.items():
            name = 'No Category' if cog_ is None else cog_.qualified_name
            filtered = await self.filter_commands(cmds, sort=True)
            if filtered:
                value = '\u2002'.join(c.name for c in cmds)
                if cog_ and cog_.description:
                    value = '{0}\n{1}'.format(cog_.description, value)

                embed.add_field(name=name, value=value)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog_):
        embed = discord.Embed(title='{0.qualified_name} Commands'.format(cog_))
        if cog_.description:
            embed.description = cog_.description

        filtered = await self.filter_commands(cog_.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(name=self.get_command_signature(command),
                            value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=group.qualified_name)
        if group.help:
            embed.description = group.help

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            for command in filtered:
                embed.add_field(name=self.get_command_signature(command),
                                value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    # This makes it so it uses the function above
    # Less work for us to do since they're both similar.
    # If you want to make regular command help look different then override it
    send_command_help = send_group_help


bot = helpers.Bot(command_prefix=prefix, description='Coding Bot v4',
                  case_insensitive=True, embed_color=discord.Color.blurple(),
                  intents=discord.Intents.all(), help_command=CustomHelp())
load_dotenv()
if len(sys.argv) > 2:
    bot.token = sys.argv[2]
else:
    bot.token = os.getenv('BOT_TOKEN')
bot.default_owner = os.getenv('OWNER_ID')
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ['JISHAKU_RETAIN'] = "True"
init_data = helpers.storage(bot)


class pools:
    config = asyncpg.create_pool(database='codingbot_db',
                                 init=helpers.init_connection)


bot.helpers = helpers
bot.tracker = DiscordUtils.InviteTracker(bot)
bot.default_prefixes = [',']
bot.server_cache = {}
bot.pools = pools
bot.owner_id = None
bot.owner_ids = init_data['owners']
bot.blacklisted = init_data['blacklisted']
bot.disabled = init_data['disabled']
bot.active_cogs = init_data['cogs']
bot.load_extension('jishaku')
bot.processing_commands = 0
bot.slash = SlashCommand(bot, sync_commands=True)
for cog in bot.active_cogs:
    try:
        bot.load_extension(cog)
        print(cog)
    except discord.DiscordException:
        if __name__ == "__main__":
            print(f'!!! {cog} !!!')
        else:
            raise


@bot.event
async def on_message(message):
    if not message.author.bot:
        ctx = await bot.get_context(message, cls=helpers.Context)
        await bot.invoke(ctx)
        for prefix_ in await prefix(bot, message):
            if message.content.startswith(f'\\{prefix_}') and bot.get_command(message.content.split()[0][len(prefix_) + 1:]):
                return await message.channel.send('lol')


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
    if not member.name.isalnum():
        await member.edit(nick=unicodedata.normalize('NFKD',member.name))
    if member.bot:
        channel = member.guild.get_channel(743817386792058971)
        return await channel.send(content=f'Bot added: {member.mention}')
    inviter = await bot.tracker.fetch_inviter(member)
    rules = member.guild.rules_channel.mention
    embed = discord.Embed(
        title='Welcome to The Coding Academy!',
        description=(
            f'Welcome {member.mention}, we\'re glad you joined! Before you get'
            ' started, here are some things to check out: \n**Read the Rules:'
            f'** {rules} \n**Get roles:** <#726074137168183356> and '
            '<#806909970482069556> \n**Want help? Read here:** '
            '<#799527165863395338> and <#754712400757784709>'),
        timestamp=datetime.datetime.utcnow())
    ago = datetime.datetime.utcnow() - member.created_at
    img = io.BytesIO(await member.avatar_url_as(format='png', size=128).read())
    try:
        img2 = io.BytesIO(await member.guild.banner_url_as(format='png', size=512).read())
    except:
        img2 = 'storage/banner.png'
    base = Image.open(img).convert("RGBA")
    base = base.resize((128, 128))
    txt = Image.open(img2).convert("RGBA")
    txt = txt.point(lambda p: p * 0.5)
    txt = txt.resize((512, 200))
    d = ImageDraw.Draw(txt)
    fill = (255, 255, 255, 255)
    font = ImageFont.truetype("storage/fonts/Poppins/Poppins-Bold.ttf", 25)
    text = "Welcome to The Coding Academy"
    text_width, text_height = d.textsize(text, font)
    d.text(((txt.size[0] - text_width) // 2, (txt.size[1] // 31) * 1), text, font=font, fill=fill, align='center')
    font = ImageFont.truetype("storage/fonts/Poppins/Poppins-Bold.ttf", 15)
    text = str(member)
    d.text(((txt.size[0] // 8) * 3, (txt.size[1] // 16) * 4), text, font=font, fill=fill, align='center')
    font = ImageFont.truetype("storage/fonts/Poppins/Poppins-Bold.ttf", 12)
    text = f'ID: {member.id}'
    d.text(((txt.size[0] // 8) * 3, (txt.size[1] // 16) * 6), text, font=font, fill=fill, align='center')
    if inviter:
        inv = sum(i.uses for i in (await member.guild.invites()) if i.inviter
                  and i.inviter.id == inviter.id)

        text = f'• Invited by: {inviter}'
        d.text(((txt.size[0] // 8) * 3, (txt.size[1] // 16) * 9), text, font=font, fill=fill, align='center')
        text = f'• ID: {inviter.id}, Invites: {inv}'
        d.text(((txt.size[0] // 8) * 3, (txt.size[1] // 16) * 11), text, font=font, fill=fill, align='center')
        text = f'• Account created: {humanize.naturaldelta(ago)} ago'
        d.text(((txt.size[0] // 8) * 3, (txt.size[1] // 16) * 13), text, font=font, fill=fill, align='center')
    else:
        try:
            invite = await member.guild.vanity_invite()
            text = f'• Joined using vanity invite: {invite.code} ({invite.uses} uses)'
        except discord.errors.HTTPException:
            text = 'I couldn\'t find who invited them'
        d.text(((txt.size[0] // 8) * 3, (txt.size[1] // 16) * 9), text, font=font, fill=fill, align='center')
        text = f'• Account created: {humanize.naturaldelta(ago)} ago'
        d.text(((txt.size[0] // 8) * 3, (txt.size[1] // 16) * 11), text, font=font, fill=fill, align='center')

    blur_radius = 1
    offset = 0
    offset = blur_radius * 2 + offset
    mask = Image.new("L", base.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, base.size[0] - offset, base.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
    txt.paste(base, (base.size[0] // 4, (base.size[1] // 8) * 3), mask)

    buf = io.BytesIO()
    txt.save(buf, format='png')
    buf.seek(0)
    file = discord.File(buf, filename='welcome.png')
    channel = member.guild.get_channel(743817386792058971)
    await channel.send(content=member.mention, file=file)
    verify_here = member.guild.get_channel(759220767711297566)
    await verify_here.send(f'Welcome {member.mention}! Please check your DMs or use `>verify` in this channel to get started.', embed=embed)
#     try:
#         await member.send(embed=embed)
#     except discord.errors.Forbidden:
#         pass


@bot.event
async def on_error(event_method, *args, **kwargs):
    await helpers.log_error(bot, event_method, *args, **kwargs)


@bot.event
async def on_command_error(ctx, error):
    exception = error
    if hasattr(ctx.command, 'on_error'):
        pass
    error = getattr(error, 'original', error)

    if ctx.author.id in ctx.bot.owner_ids:
        if (isinstance(error, (
                commands.MissingAnyRole,
                commands.CheckFailure,
                commands.DisabledCommand, commands.CommandOnCooldown,
                commands.MissingPermissions, commands.MaxConcurrencyReached))):
            try:
                await ctx.reinvoke()
            except discord.ext.commands.CommandError as e:
                pass
            else:
                return

    if (isinstance(error, (
            commands.BadArgument, commands.MissingRequiredArgument,
            commands.NoPrivateMessage, commands.CheckFailure,
            commands.DisabledCommand, commands.CommandInvokeError,
            commands.TooManyArguments, commands.UserInputError,
            commands.NotOwner, commands.MissingPermissions,
            commands.BotMissingPermissions, commands.MaxConcurrencyReached,
            commands.CommandNotFound))):
        await helpers.log_command_error(ctx, exception, True)
        if not isinstance(error, commands.CommandNotFound):
            if await helpers.is_disabled(ctx):
                return
        text = None
        if isinstance(error, commands.CheckFailure):
            if bot.disabled:
                text = 'The bot is currently disabled. It will be back soon.'
        if not isinstance(error, commands.CommandNotFound):
            embed = ctx.embed(title="Error", description=text or str(error),
                              color=discord.Color.red())
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            owner = bot.get_user(ctx.bot.owner_ids[0])
            embed.set_footer(
                icon_url=bot.user.avatar_url,
                text=f'If you think this is a mistake please contact {owner}')
            await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandOnCooldown):
        await helpers.log_command_error(ctx, exception, True)
        time = datetime.timedelta(seconds=math.ceil(error.retry_after))
        error = (f'You are on cooldown. Try again after '
                 f'{humanize.precisedelta(time)}')
        embed = ctx.embed(title="Error", description=error,
                          color=discord.Color.red())
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        owner = bot.get_user(ctx.bot.owner_ids[0])
        embed.set_footer(
            icon_url=bot.user.avatar_url,
            text=f'If you think this is a mistake please contact {owner}')
        await ctx.send(embed=embed)

    else:
        try:
            embed = ctx.embed(title='Oh no!', description=(
                'An error occurred. My developer has been notified of it, '
                'but if it continues to occur please DM '
                f'<@{ctx.bot.owner_ids[0]}>'), color=discord.Color.red())
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            pass
        await helpers.log_command_error(ctx, exception, False)


class Developer(commands.Cog):

    def __init__(self, bot_):
        self.bot = bot_

    @commands.command(name='load', aliases=['l'])
    @commands.is_owner()
    async def _load(self, ctx, cog_, save: bool = False):
        if save:
            helpers.storage(self.bot, key='cogs', value=cog_, method='append')
        self.bot.load_extension(cog_)
        embed = ctx.embed(
            title='Success', description='Saved Preference' if save else None,
            color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(name='unload', aliases=['u'])
    @commands.is_owner()
    async def _unload(self, ctx, cog_, save: bool = False):
        if save:
            helpers.storage(self.bot, key='cogs', value=cog_, method='remove')
        self.bot.unload_extension(cog_)
        embed = ctx.embed(
            title='Success', description='Saved Preference' if save else None,
            color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(name='reload', aliases=['r'])
    @commands.is_owner()
    async def _reload(self, ctx, cog_):
        self.bot.reload_extension(cog_)
        embed = ctx.embed(title='Success', color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(name='loadall', aliases=['la'])
    @commands.is_owner()
    async def _loadall(self, ctx):
        data = helpers.storage(self.bot)
        cogs = {
            'loaded': [],
            'not': []
        }
        for cog_ in data['cogs']:
            if cog_ in bot.extensions:
                continue
            try:
                self.bot.load_extension(cog_)
                cogs['loaded'].append(cog_)
            except discord.DiscordException:
                cogs['not'].append(cog_)
        embed = ctx.embed(title='Load all cogs', description='\n'.join([
            ('\U00002705' if cog_ in cogs['loaded'] else '\U0000274c')
            + cog_ for cog_ in data['cogs']]))
        await ctx.send(embed=embed)

    @commands.command(name='unloadall', aliases=['ua'])
    @commands.is_owner()
    async def _unloadall(self, ctx):
        cogs = {
            'unloaded': [],
            'not': []
        }
        processing = bot.extensions.copy()
        for cog_ in processing:
            try:
                self.bot.unload_extension(cog_)
                cogs['unloaded'].append(cog_)
            except discord.DiscordException:
                cogs['not'].append(cog_)
        embed = ctx.embed(title='Unload all cogs', description='\n'.join([
            ('\U00002705' if cog_ in cogs['unloaded'] else '\U0000274c')
            + cog_ for cog_ in processing]))
        await ctx.send(embed=embed)

    @commands.command(name='reloadall', aliases=['ra'])
    @commands.is_owner()
    async def _reloadall(self, ctx):
        cogs = {
            'reloaded': [],
            'not': []
        }
        processing = bot.extensions.copy()
        for cog_ in processing:
            try:
                self.bot.reload_extension(cog_)
                cogs['reloaded'].append(cog_)
            except discord.DiscordException:
                cogs['not'].append(cog_)
        embed = ctx.embed(title='Reload all cogs', description='\n'.join([
            ('\U00002705' if cog_ in cogs['reloaded'] else '\U0000274c')
            + cog_ for cog_ in processing]))
        await ctx.send(embed=embed)


bot.add_cog(Developer(bot))


@bot.before_invoke
async def before_invoke(ctx):
    bot.processing_commands += 1


@bot.after_invoke
async def after_invoke(ctx):
    bot.processing_commands -= 1


@tasks.loop(minutes=2)
async def status_change():
    statuses = ['over TCA', 'you', 'swas', '@everyone', 'general chat', 'discord', ',help', 'your mom', 
                'bob and shadow argue', 'swas simp for false', 'new members', 'the staff team', 
                random.choice(bot.get_guild(681882711945641997).get_role(795145820210462771).members).name, 
                'helpers', 'code', 'mass murders', 'karen be an idiot', 'a video', 'watches', 'bob', 
                'fight club', 'youtube', 'https://devbio.me/u/CodingBot']
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=random.choice(
            statuses) + ' | ' + bot.default_prefixes[0] + 'help'))


@status_change.before_loop
async def before_status_change():
    await bot.wait_until_ready()
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name='Starting up...'))
    await asyncio.sleep(15)


@tasks.loop(minutes=5)
async def booster_perms():
    guild = bot.get_guild(681882711945641997)
    nitro_booster = guild.get_role(737517726737629214)
    active = guild.get_role(726029173067481129)
    muted = guild.get_role(766469426429820949)
    for member in nitro_booster.members:
        if not (active in member.roles or muted in member.roles):
            try:
                await member.add_roles(active)
            except discord.errors.Forbidden:
                pass


@booster_perms.before_loop
async def before_booster_perms():
    await bot.wait_until_ready()


@bot.check
def blacklist(ctx):
    return (ctx.author.id not in bot.blacklisted
            or ctx.author.id in bot.owner_ids)


@bot.check
def disabled(ctx):
    return (not bot.disabled) or ctx.author.id in bot.owner_ids


@bot.check
async def disabled_command(ctx):
    return ((not await helpers.is_disabled(ctx))
            or ctx.author.id in bot.owner_ids
            or ctx.author.id == ctx.guild.owner.id)


@bot.slash.slash(name='help', description='Get the help for the bot')
async def slash_help(ctx: SlashContext):
    await ctx.send(embeds=[discord.Embed(title='Hello There!', description=(
        'I use special command prefixes for my commands. Please type \n'
        f'{bot.user.mention + " help"} \nfor my full help menu!'))])


@bot.slash.slash(name='invite', description='Invite the bot to your server')
async def slash_invite(ctx: SlashContext):
    embed = discord.Embed(title='Invite', description=(
        '[Click Here](https://discord.com/oauth2/authorize?client_id='
        f'{bot.user.id}&permissions=8&scope=bot%20applications.commands) '
        'to invite me!'), timestamp=datetime.datetime.utcnow())
    await ctx.send(embeds=[embed])

status_change.start()
booster_perms.start()
if __name__ == "__main__":
    bot.run(bot.token)
