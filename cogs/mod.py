import datetime

import discord
import humanize
import time_str
from discord.ext import commands


class BelowMember(discord.Member):
    pass


class BelowMemberConverter(commands.MemberConverter):
    async def convert(self, ctx, *args, **kwargs):
        res = await super().convert(ctx, *args, **kwargs)
        if ctx.author.top_role.position <= res.top_role.position: raise commands.CheckFailure(
            'You do not have permissions to interact with that user')
        return res


commands.converter.BelowMemberConverter = BelowMemberConverter
BelowMember.__module__ = "discord.belowmember"


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def execute(self, ctx, coro):
        try:
            await coro
        except discord.errors.Forbidden:
            await ctx.send(embed=ctx.error('I do not have permission to interact with that user'))

    async def log(self, **kwargs):
        action = kwargs.pop('action')
        moderator = kwargs.pop('moderator')
        target = kwargs.pop('target')
        undo = kwargs.get('undo')
        reason = kwargs.get('reason')
        duration = kwargs.get('duration')
        if undo:
            color = discord.Color.green()
        if action == 'kick':
            if undo:
                raise ValueError('Cannot un-kick')
            color = discord.Color.orange()
            action_string = 'kicked'
            icon = ':boot:'
        elif action == 'ban':
            if undo:
                action_string = 'unbanned'
                icon = ':unlock:'
            else:
                color = discord.Color.red()
                action_string = 'banned'
                icon = ':hammer:'
        elif action == 'warn':
            warn = kwargs.get('warn')
            if undo:
                if warn:
                    action_string = f'removed warning ({warn}) from'
                else:
                    action_string = 'removed all warnings from'
                icon = ':flag_white:'
            else:
                color = discord.Color.yellow()
                action_string = 'warned'
                icon = ':warning:'
        elif action == 'mute':
            if undo:
                action_string = 'unmuted'
                icon = ':loud_sound:'
            else:
                color = discord.Color.grey()
                action_string = 'muted'
                icon = ':mute:'
        else:
            raise ValueError('Incorrect Type')
        description = (f'**{icon} {action_string.title()} {target.name}**#'
                       f'{target.discriminator} *(ID: {target.id})* \n**'
                       f':page_facing_up: Reason:** {reason}') + (' \n**:clock2: Duration:** '
                                                                  f'{humanize.precisedelta(duration)}') if duration else ''
        embed = discord.Embed(description=description, color=color, timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f'{moderator} (ID: {moderator.id}', icon_url=moderator.avatar_url)
        embed.set_thumbnail(url=target.avatar_url)
        logs = self.bot.get_channel(816512034228666419)
        await logs.send(embed=embed)

    @commands.check
    async def trainee_check(self):
        if not self.guild.id == 681882711945641997:
            return False
        trainee = self.guild.get_role(729537643951554583)
        helper = self.guild.get_role(726650418444107869)
        if (self.author.top_role >= trainee or self.author.guild_permissions.kick_members):
            return True
        if helper in self.author.roles:
            if self.command.qualified_name == 'mute':
                return True

    @commands.command(name='kick')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.has_guild_permissions(kick_members=True)
    async def _kick(self, ctx, target: BelowMember, *, reason: str = None):
        try:
            await target.send(('You have been :boot: **Kicked** :boot: from '
                               f'**{ctx.guild.name}**. \nReason: {reason}'))
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            pass
        await self.log(action='kick', moderator=ctx.author, target=target, reason=reason)
        await self.execute(ctx, target.kick(reason=f'{ctx.author.id}: {reason}'))
        await ctx.send(embed=discord.Embed(title=':boot: Member Kicked :boot:',
            description=f'{target.mention} has been kicked \nReason: {reason}'))

    @commands.command(name='ban')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    async def _ban(self, ctx, target: BelowMember, *, reason: str = None):
        try:
            await target.send(('You have been :hammer: **Banned** :hammer: from '
                               f'**{ctx.guild.name}**. \nReason: {reason}'))
        except discord.errors.Forbidden:
            pass
        await self.log(action='ban', moderator=ctx.author, target=target, reason=reason)
        await self.execute(ctx, target.ban(reason=f'{ctx.author.id}: {reason}'))
        await ctx.send(embed=discord.Embed(title=':hammer: Member Banned :hammer:',
            description=f'{target.mention} has been banned \nReason: {reason}'))

    @commands.command(name='massban')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    async def _massban(self, ctx, reason, *targets: commands.Greedy[BelowMember]):
        fails = 0
        for target in targets:
            fails += await self.execute(ctx, target.ban(reason=f'{ctx.author.id}: {reason}'))
            if fails >= 5:
                return await ctx.send_error('Too many failed bans, aborting.')

    @commands.command(name='unban')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    @commands.has_any_role(795136568805294097, 725899526350831616)
    async def _unban(self, ctx, target: discord.User, *, reason: str = None):
        try:
            await target.send(('You have been :unlock: **Unbanned** :unlock: from '
                               f'**{ctx.guild.name}**. \nReason: {reason}'))
        except discord.errors.Forbidden:
            pass
        await self.log(action='ban', moderator=ctx.author, target=target, reason=reason, undo=True)
        try:
            await ctx.guild.fetch_ban(target)
        except discord.NotFound:
            return await ctx.send(embed=ctx.error('That user is not banned'))
        await self.execute(ctx, ctx.guild.unban(target, reason=f'{ctx.author.id}: {reason}'))
        await ctx.send(embed=discord.Embed(title=':unlock: Member Unbanned :unlock:',
            description=(f'{target.mention} has been unbanned \nReason: '
                         f'{reason}')))

    @commands.command(name='warn')
    @commands.guild_only()
    @trainee_check
    async def _warn(self, ctx, target: BelowMember, *, reason: str = None):
        try:
            await target.send(('You have been :warning: **Warned** :warning: '
                               f'in **{ctx.guild.name}**. \nReason: {reason}'))
        except discord.errors.Forbidden:
            pass
        await self.log(action='warn', moderator=ctx.author, target=target, reason=reason)
        # warn them here
        await ctx.send(embed=discord.Embed(title=':warning: Member Warned :warning:',
            description=(f'{target.mention} has been warned \nReason: '
                         f'{reason}')))

    @commands.command(name='mute')
    @commands.guild_only()
    @trainee_check
    async def _mute(self, ctx, target: BelowMember, duration: time_str.convert = datetime.timedelta(hours=1), *,
                    reason: str = None):
        trainee = self.guild.get_role(729537643951554583)
        helper = self.guild.get_role(726650418444107869)
        if not (self.author.top_role >= trainee or self.author.guild_permissions.kick_members):
            duration = datetime.timedelta(minutes=15)
        try:
            await target.send((f'You have been :mute: **Muted** :mute: in **{ctx.guild.name}'
                               f'**. \nReason: {reason} \n**Duration**: '
                               f'{humanize.precisedelta(duration)}'))
        except discord.errors.Forbidden:
            pass
        await self.log(action='mute', moderator=ctx.author, target=target, duration=duration, reason=reason)
        mute_role = ([role for role in ctx.guild.roles if 'muted' in role.name.lower()])
        if len(mute_role) == 0:
            return await ctx.send(error=ctx.error('I couldn\'t find a mute role'))
        else:
            mute_role = mute_role[0]
        await self.execute(ctx, target.add_roles(mute_role, reason=f'{ctx.author.id}: {reason}'))
        await ctx.send(embed=discord.Embed(title=':mute: Member Muted :mute:',
            description=(f'{target.mention} has been muted \nReason: {reason} \n'
                         f'**Duration**: {duration}')))

    @commands.command(name='unmute')
    @commands.guild_only()
    @trainee_check
    async def _unmute(self, ctx, target: BelowMember, *, reason: str = None):
        try:
            await target.send(('You have been :mute: **Muted** :mute: in '
                               f'**{ctx.guild.name}**. \nReason: {reason}'))
        except discord.errors.Forbidden:
            pass
        await self.log(action='mute', moderator=ctx.author, target=target, reason=reason, undo=True)
        mute_roles = (role for role in ctx.guild.roles if 'muted' in role.name.lower())
        await self.execute(ctx, target.remove_roles(*mute_roles, reason=f'{ctx.author.id}: {reason}'))
        await ctx.send(embed=discord.Embed(title=':loud_sound: Member Unmuted :loud_sound:',
            description=(f'{target.mention} has been unmuted \nReason: '
                         f'{reason}')))

    @commands.command(name='delete', aliases=['del'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def _delete(self, ctx, target: int = None):
        """
        Delete a message by it's ID or by replying.
        """
        if not target:
            target = ctx.message.reference.message_id
        message = await ctx.channel.fetch_message(target)
        await message.delete()
        await ctx.send(f'ok boomer ||(msg {target} deleted by {ctx.author}||')

    @commands.command(name='verify', aliases=['v'])
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def _verify(self, ctx, *, target: BelowMember):
        """
        Manually verify a member.
        """
        if not ctx.guild.id == 681882711945641997:
            return await ctx.send(embed=ctx.error('Must be in The Coding Academy'))
        member = ctx.guild.get_role(744403871262179430)
        if member in target.roles:
            return await ctx.send(embed=ctx.error('Member is already verified'))
        await target.add_roles(member)
        await ctx.send(
            embed=ctx.embed(title='Member Verified', description=f'{target.mention} was successfully verified.'))

    @commands.command(name='nickname', aliases=['nick'])
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def _nickname(self, ctx, target: BelowMember, *, nick=None):
        """
        Change a members nickname
        """
        await target.edit(nick=nick)
        await ctx.send(embed=ctx.embed(title='Updated Nickname',
                                       description=f'Updated the nickname of {target.mention} to {nick}' if nick else f'Removed the nickname of {target.mention}'))

    @commands.command(name='slowmode')
    @commands.guild_only()
    @trainee_check
    async def _slowmode(self, ctx, *, delay: time_str.convert = datetime.timedelta(seconds=1)):
        if not 0 <= delay.total_seconds() <= 21600:
            return await ctx.send(embed=ctx.error(
                f'Slowmode cannot be more than {humanize.precisedelta(datetime.timedelta(seconds=21600))} or less than 0 seconds'))
        await ctx.channel.edit(slowmode_delay=delay.total_seconds())
        await ctx.send(embed=ctx.embed(title='Successfully changed slowmode',
                                       description=f'Set to {humanize.precisedelta(delay)}'))


def setup(bot):
    bot.add_cog(Moderation(bot))
