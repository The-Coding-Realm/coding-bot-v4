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
        if ctx.author.top_role.position <= res.top_role.position: raise commands.CheckFailure('You do not have permissions to interact with that user')
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
            await ctx.send(embed=ctx.error(
                'I do not have permission to interact with that user'
            ))

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
                       f':page_facing_up: Reason:** {reason}') + (
                            ' \n**:clock2: Duration:** '
                            f'{humanize.precisedelta(duration)}'
                       ) if duration else ''
        embed = discord.Embed(description=description, color=color,
                              timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f'{moderator} (ID: {moderator.id}',
                         icon_url=moderator.avatar_url)
        embed.set_thumbnail(url=target.avatar_url)
        logs = self.bot.get_channel(816512034228666419)
        await logs.send(embed=embed)

    @commands.check
    async def trainee_check(self):
        if not self.guild.id == 681882711945641997:
            return False
        trainee = self.guild.get_role(729537643951554583)
        helper = self.guild.get_role(726650418444107869)
        if (self.author.top_role >= trainee or
                self.author.guild_permissions.kick_members):
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
        except discord.errors.Forbidden:
            pass
        await self.log(action='kick', moderator=ctx.author, target=target,
                       reason=reason)
        await self.execute(ctx,
                           target.kick(reason=f'{ctx.author.id}: {reason}'))
        await ctx.send(embed=discord.Embed(
            title=':boot: Member Kicked :boot:',
            description=f'{target.mention} has been kicked \nReason: {reason}')
        )

    @commands.command(name='ban')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    async def _ban(self, ctx, target: BelowMember, *, reason: str = None):
        try:
            await target.send(
                ('You have been :hammer: **Banned** :hammer: from '
                 f'**{ctx.guild.name}**. \nReason: {reason}')
            )
        except discord.errors.Forbidden:
            pass
        await self.log(action='ban', moderator=ctx.author, target=target,
                       reason=reason)
        await self.execute(ctx,
                           target.ban(reason=f'{ctx.author.id}: {reason}'))
        await ctx.send(embed=discord.Embed(
            title=':hammer: Member Banned :hammer:',
            description=f'{target.mention} has been banned \nReason: {reason}')
        )

    @commands.command(name='unban')
    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    @commands.has_any_role(795136568805294097, 725899526350831616)
    async def _unban(self, ctx, target: discord.User, *, reason: str = None):
        try:
            await target.send(
                ('You have been :unlock: **Unbanned** :unlock: from '
                 f'**{ctx.guild.name}**. \nReason: {reason}')
            )
        except discord.errors.Forbidden:
            pass
        await self.log(action='ban', moderator=ctx.author, target=target,
                       reason=reason, undo=True)
        try:
            await ctx.guild.fetch_ban(target)
        except discord.NotFound:
            return await ctx.send(embed=ctx.error('That user is not banned'))
        await self.execute(
            ctx,
            ctx.guild.unban(target, reason=f'{ctx.author.id}: {reason}')
        )
        await ctx.send(embed=discord.Embed(
            title=':unlock: Member Unbanned :unlock:',
            description=(f'{target.mention} has been unbanned \nReason: '
                         f'{reason}')
        ))

    @commands.command(name='warn')
    @commands.guild_only()
    @trainee_check
    async def _warn(self, ctx, target: BelowMember, *, reason: str = None):
        try:
            await target.send(('You have been :warning: **Warned** :warning: '
                               f'in **{ctx.guild.name}**. \nReason: {reason}'))
        except discord.errors.Forbidden:
            pass
        await self.log(action='warn', moderator=ctx.author, target=target,
                       reason=reason)
        # warn them here
        await ctx.send(embed=discord.Embed(
            title=':warning: Member Warned :warning:',
            description=(f'{target.mention} has been warned \nReason: '
                         f'{reason}')))

    @commands.command(name='mute')
    @commands.guild_only()
    @trainee_check
    async def _mute(self, ctx, target: BelowMember,
                    duration: time_str.convert = datetime.timedelta(hours=1),
                    *, reason: str = None):
        trainee = self.guild.get_role(729537643951554583)
        helper = self.guild.get_role(726650418444107869)
        if not (self.author.top_role >= trainee or
                self.author.guild_permissions.kick_members):
            duration = datetime.timedelta(minutes=15)
        try:
            await target.send((
                f'You have been :mute: **Muted** :mute: in **{ctx.guild.name}'
                f'**. \nReason: {reason} \n**Duration**: '
                f'{humanize.precisedelta(duration)}'
            ))
        except discord.errors.Forbidden:
            pass
        await self.log(action='mute', moderator=ctx.author, target=target,
                       duration=duration, reason=reason)
        mute_role = (
            [role for role in ctx.guild.roles if 'muted' in role.name.lower()]
        )
        if len(mute_role) == 0:
            return await ctx.send(
                error=ctx.error('I couldn\'t find a mute role')
            )
        else:
            mute_role = mute_role[0]
        await self.execute(
            ctx,
            target.add_roles(mute_role, reason=f'{ctx.author.id}: {reason}')
        )
        await ctx.send(embed=discord.Embed(
            title=':mute: Member Muted :mute:',
            description=(
                f'{target.mention} has been muted \nReason: {reason} \n'
                f'**Duration**: {duration}'
            )))

    @commands.command(name='unmute')
    @commands.guild_only()
    @trainee_check
    async def _unmute(self, ctx, target: BelowMember, *,
                      reason: str = None):
        try:
            await target.send(('You have been :mute: **Muted** :mute: in '
                               f'**{ctx.guild.name}**. \nReason: {reason}'))
        except discord.errors.Forbidden:
            pass
        await self.log(action='mute', moderator=ctx.author, target=target,
                       reason=reason, undo=True)
        mute_roles = (
            role for role in ctx.guild.roles if 'muted' in role.name.lower()
        )
        await self.execute(
            ctx,
            target.remove_roles(*mute_roles,
                                reason=f'{ctx.author.id}: {reason}')
        )
        await ctx.send(embed=discord.Embed(
            title=':loud_sound: Member Unmuted :loud_sound:',
            description=(f'{target.mention} has been unmuted \nReason: '
                         f'{reason}')))


def setup(bot):
    bot.add_cog(Moderation(bot))
