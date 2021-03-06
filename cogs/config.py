import discord
import asyncpg
from discord.ext import commands


async def convert(ctx, target):
    try:
        target = await discord.ext.commands.MemberConverter().convert(ctx,
                                                                      target)
    except discord.ext.commands.errors.MemberNotFound:
        try:
            target = await discord.ext.commands.TextChannelConverter().convert(
                ctx, target)
        except discord.ext.commands.errors.ChannelNotFound:
            try:
                target = await discord.ext.commands.RoleConverter().convert(
                    ctx, target)
            except discord.ext.commands.errors.RoleNotFound:
                await ctx.send(f'I couldn\'t find `{target}`')
                return None
    return target


class Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def config(self, ctx):
        await ctx.send_help('config')

    @config.command(name='prefix')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def _prefix(self, ctx, *prefixes):
        prefixes = list(prefixes)
        prefixes = (prefixes if not (prefixes == ['default']
                    or prefixes == self.bot.default_prefixes) else None)
        previous_prefixes = self.bot.default_prefixes
        try:
            async with self.bot.pools.config.acquire() as connection:

                data = await connection.fetchval(
                    'SELECT prefixes FROM serverconf WHERE id = $1',
                    ctx.guild.id)
                insert = (
                    self.bot.default_prefixes if prefixes is None
                    else prefixes)
                if prefixes == []:
                    previous_prefixes = data or previous_prefixes
                else:
                    if not data:
                        await connection.execute(
                            f'''INSERT INTO serverconf (prefixes, id)
                            VALUES (ARRAY{insert}, {ctx.guild.id})''')
                    else:
                        await connection.execute(
                            f'''UPDATE serverconf
                            SET prefixes = ARRAY{insert}
                            WHERE id = {ctx.guild.id}''')
        except asyncpg.exceptions._base.InterfaceError:
            pass

        if prefixes == []:
            embed = ctx.embed(title='Prefix', description=(
                f'Current Prefix(es): `{"`, `".join(previous_prefixes)}`\n\nOr'
                ', you can mention me as a prefix (try "'
                f'{self.bot.user.mention} help")'))
            embed.add_field(name='To reset:', value=(
                f'`{ctx.prefix + ctx.command.qualified_name} default` to reset'
                ' the prefix to default, or replace default with your own '
                'prefix'))
            return await ctx.send(embed=embed)
        prefixes = prefixes or ['set to default']
        embed = ctx.embed(title='Successfully changed prefix', description=(
            f'Prefixes are now `{"`, `".join(prefixes)}``'
            if len(prefixes) > 1 else f'Prefix is now {prefixes[0]}'))
        await self.bot.helpers.prepare(self.bot, ctx.guild)
        await ctx.send(embed=embed)

    @config.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def disabled(self, ctx):
        """

        """
        try:
            commands = self.bot.server_cache[ctx.guild.id]['commands']
        except KeyError:
            await self.bot.helpers.prepare(self.bot, ctx.guild)
            commands = self.bot.server_cache[ctx.guild.id]['commands']
        if not commands:
            return await ctx.send(embed=ctx.error('No commands are disabled'))
        if len(commands) == 0:
            return await ctx.send(embed=ctx.error('No commands are disabled'))

        content = ('\n'.join([
            (await convert(ctx, command)).mention + ': '
            + (('`' + '`, `'.join(commands[command]) + '`.')
               if True not in commands[command] else 'All Commands')
            for command in commands if commands.get(command, None)])
            or 'No Commands are disabled')
        await ctx.send(embed=ctx.embed(content, title='Disabled Commands'))

    @config.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def disable(self, ctx):
        """

        """
        await ctx.send_help('config disable')

    @config.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def enable(self, ctx):
        """

        """
        await ctx.send_help('config enable')

    @disable.command(name='command')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def _disable_command(self, ctx, command, *, target=None):
        """
        Disable a command on the bot. Target can be a member, channel, or role.
        The command will be disabled for the target. If no target is specified,
        it will disable the command for the whole server. If the command
        contains a space you must "wrap it in quotes like this."
        """
        if target is not None:
            try:
                target = await discord.ext.commands.MemberConverter().convert(
                    ctx, target)
            except discord.ext.commands.errors.MemberNotFound:
                try:
                    target = (await discord.ext.commands.TextChannelConverter()
                              ).convert(ctx, target)
                except discord.ext.commands.errors.ChannelNotFound:
                    try:
                        target = (await discord.ext.commands.RoleConverter()
                                  ).convert(ctx, target)
                    except discord.ext.commands.errors.RoleNotFound:
                        return await ctx.send(f'I couldn\'t find `{target}`')
            the_for = ' for ' + target.mention
        else:
            target = ctx.guild
            the_for = ''
        command = self.bot.get_command(command)
        if not command:
            return await ctx.send(embed=ctx.error('That isn\'t a command!'))
        if command.qualified_name.split()[0] in ['config', 'help']:
            return await ctx.send(embed=ctx.error(
                "You cannot disable the config or help commands."))
        embed = ctx.embed(title='Command Disabled', description=(
            f'I will now ignore the command {command.qualified_name}{the_for}.'
            ))

        async with self.bot.pools.config.acquire() as connection:
            data = await connection.fetchrow(
                'SELECT * FROM serverconf WHERE id = $1', ctx.guild.id)
            if not data:
                commands = {
                    str(target.id): [command.qualified_name]
                }
                await connection.execute(
                    '''INSERT INTO serverconf (id, commands)
                    VALUES ($1, $2::json)''', ctx.guild.id, commands)
            else:
                commands = data['commands']
                if isinstance(commands, dict):
                    commands[str(target.id)] = commands.get(str(target.id), [])
                else:
                    commands = {
                        str(target.id): [command.qualified_name]
                    }
                if command.qualified_name in commands[str(target.id)]:
                    return await ctx.send(embed=ctx.error((
                        f'`{command.qualified_name}` is already disabled'
                        f'{the_for}.')))
                commands[str(target.id)].append(command.qualified_name)
                await connection.execute(
                    'UPDATE serverconf SET commands = $1 WHERE id = $2',
                    commands, ctx.guild.id)
        await self.bot.helpers.prepare(self.bot, ctx.guild)
        await ctx.send(embed=embed)

    @disable.command(name='all')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def _disable_all(self, ctx, *, target=None):
        query = target
        target = None
        if query is not None:
            try:
                target = await discord.ext.commands.MemberConverter().convert(
                    ctx, query)
            except discord.ext.commands.errors.MemberNotFound:
                pass
        else:
            target = ctx.channel
        if target is None:
            try:
                target = await discord.ext.commands.TextChannelConverter(
                    ).convert(ctx, query)
            except discord.ext.commands.errors.ChannelNotFound:
                pass
        if target is None:
            try:
                target = await discord.ext.commands.RoleConverter().convert(
                    ctx, query)
            except discord.ext.commands.errors.RoleNotFound:
                return await ctx.send(f'I couldn\'t find `{query}`')
        the_for = ' for ' + target.mention
        embed = ctx.embed(title='Commands Disabled', description=(
            f'I will now ignore all commands{the_for}.'))

        async with self.bot.pools.config.acquire() as connection:
            data = await connection.fetchrow(
                'SELECT * FROM serverconf WHERE id = $1', ctx.guild.id)
            if not data:
                commands = {
                    str(target.id): [True]
                }
                await connection.execute('''INSERT INTO serverconf (id, commands)
                    VALUES ($1, $2::json)''', ctx.guild.id, commands)
            else:
                commands = data['commands']
                if isinstance(commands, dict):
                    commands[str(target.id)] = commands.get(str(target.id), [])
                else:
                    commands = {
                        str(target.id): [True]
                    }
                if True in commands[str(target.id)]:
                    return await ctx.send(embed=ctx.error(
                        f'All commands are already disabled{the_for}.'))
                commands[str(target.id)].append(True)
                await connection.execute(
                    'UPDATE serverconf SET commands = $1::json WHERE id = $2',
                    commands, ctx.guild.id)
        await self.bot.helpers.prepare(self.bot, ctx.guild)
        await ctx.send(embed=embed)

    @enable.command(name='all')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def _enable_all(self, ctx, *, target=None):
        """
        Enable a command on the bot. Target can be a member, channel, or role.
        The command will be disabled for the target. If no target is specified,
        it will enable the command for the whole server. If the command
        contains a space you must "wrap it in quotes like this."
        """
        query = target
        target = None
        if query is not None:
            try:
                target = await discord.ext.commands.MemberConverter().convert(
                    ctx, query)
            except discord.ext.commands.errors.MemberNotFound:
                pass
        else:
            target = ctx.channel
        if target is None:
            try:
                target = await discord.ext.commands.TextChannelConverter(
                    ).convert(ctx, query)
            except discord.ext.commands.errors.ChannelNotFound:
                pass
        if target is None:
            try:
                target = await discord.ext.commands.RoleConverter().convert(
                    ctx, query)
            except discord.ext.commands.errors.RoleNotFound:
                return await ctx.send(f'I couldn\'t find `{query}`')
        the_for = ' for ' + target.mention
        embed = ctx.embed(title='Commands Enabled', description=(
            f'I will now stop ignoring all commands{the_for}.'))

        async with self.bot.pools.config.acquire() as connection:
            data = await connection.fetchrow(
                'SELECT * FROM serverconf WHERE id = $1', ctx.guild.id)
            if not data:
                return await ctx.send(embed=ctx.error(
                    f'Commands are not disabled{the_for}.'))
            else:
                commands = data['commands']
                if isinstance(commands, dict):
                    commands[str(target.id)] = commands.get(str(target.id), [])
                else:
                    return await ctx.send(embed=ctx.error(
                        f'Commands are not disabled{the_for}.'))
                try:
                    commands[str(target.id)].remove(True)
                except ValueError:
                    return await ctx.send(embed=ctx.error(
                        f'Commands are not disabled{the_for}.'))
                await connection.execute('''UPDATE serverconf
                SET commands = $1::json WHERE id = $2''', commands,
                                         ctx.guild.id)
        await self.bot.helpers.prepare(self.bot, ctx.guild)
        await ctx.send(embed=embed)

    @enable.command(name='command')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def _enable_command(self, ctx, command, *, target=None):
        """
        Enable a command on the bot. Target can be a member, channel, or role.
        The command will be disabled for the target. If no target is specified,
        it will enable the command for the whole server. If the command
        contains a space you must "wrap it in quotes like this."
        """
        query = target
        target = None
        the_for = ''
        if query is not None:
            try:
                target = await discord.ext.commands.MemberConverter().convert(
                    ctx, query)
            except discord.ext.commands.errors.MemberNotFound:
                pass
        else:
            target = ctx.guild
            the_for = ''
        if target is None:
            try:
                target = await discord.ext.commands.TextChannelConverter(
                    ).convert(ctx, query)
            except discord.ext.commands.errors.ChannelNotFound:
                pass
        if target is None:
            try:
                target = await discord.ext.commands.RoleConverter().convert(
                    ctx, query)
            except discord.ext.commands.errors.RoleNotFound:
                return await ctx.send(f'I couldn\'t find `{query}`')
        if the_for is None:
            the_for = ' for ' + target.mention
        command = self.bot.get_command(command)
        try:
            assert command
        except AssertionError:
            return await ctx.send(embed=ctx.error('That isn\'t a command!'))
        embed = ctx.embed(title='Command Enabled', description=(
            f'I will now stop ignoring the command {command.qualified_name}'
            f'{the_for}.'))

        async with self.bot.pools.config.acquire() as connection:
            data = await connection.fetchrow(
                'SELECT * FROM serverconf WHERE id = $1', ctx.guild.id)
            if not data:
                return await ctx.send(embed=ctx.error(
                    f'`{command.qualified_name}` is not disabled{the_for}.'))
            else:
                commands = data['commands']
                if isinstance(commands, dict):
                    commands[str(target.id)] = commands.get(str(target.id), [])
                else:
                    return await ctx.send(embed=ctx.error(
                        f'Commands are not disabled{the_for}.'))
                try:
                    commands[str(target.id)].remove(command.qualified_name)
                except ValueError:
                    return await ctx.send(embed=ctx.error(
                        f'`{command.qualified_name}` is not disabled{the_for}.'
                    ))
                await connection.execute('''UPDATE serverconf
                SET commands = $1::json WHERE id = $2''', commands,
                                         ctx.guild.id)
        await self.bot.helpers.prepare(self.bot, ctx.guild)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Config(bot))
