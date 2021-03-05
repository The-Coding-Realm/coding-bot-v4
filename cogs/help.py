import re
import datetime
import asyncio
from discord.ext import commands


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.check
    async def callstaff_check(self):
        if self.guild:
            if self.guild.id == 681882711945641997:
                if (datetime.datetime.utcnow()
                        - self.author.joined_at).days > 1:
                    return True
        return False

    @commands.check
    async def helper_check(self):
        if self.guild:
            if self.guild.id == 681882711945641997:
                if self.channel.id in [
                    767641462179233792,  # help-a
                    767641487210315796,  # help-b
                    767641504092913674,  # help-c
                    776272365223018516,  # help-d
                    776272386856583178,  # help-e
                    797861120185991198,  # exclusive-help
                    681892318915330084,  # python
                    731170873221972049,  # java
                    681893466682425407,  # javascript
                    681892921074778184,  # html-css-php
                    725880738293219479,  # c-cpp-cs
                    726028249922273351,  # discord-py
                    726028289939996713,  # discord-js
                ]:
                    return True
                # active = self.guild.get_role(726029173067481129)
                # if active in self.author.roles:
                #     if (datetime.datetime.utcnow()
                #             - self.author.joined_at).days > 7:
                #         return True
        return False

    @commands.command()
    @commands.guild_only()
    @helper_check
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def helper(self, ctx, language=None, *, description=None):
        """
        Request help for your code. Misusing this command may result in a
        punishment.
        """
        roles = {
            'Python': 807098700589301791,
            'JavaScript': 807098827185717299,
            'Java': 807098903127916584,
            'C++': 807098975986384947,
            'C#': 807099060883423272,
            'HTML/CSS': 807099145278062602,
            'Other': 806920884441972767
        }
        if not language:
            msg = await ctx.send(embed=ctx.embed(
                title='What would you like help with?',
                description=f'**Options:** `{"`, `".join(roles)}`'))

            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author
            try:
                message = await self.bot.wait_for(
                    'message', check=check, timeout=30)
                await msg.delete()
            except asyncio.TimeoutError:
                ctx.command.reset_cooldown(ctx)
                return await ctx.send(embed=ctx.error('Timed out!'))
            language = message.clean_content
        rep = {
            "Python": [
                "python",
                'py',
            ],
            "JavaScript": [
                "javascript",
                'js',
            ],
            'Java': 'java',
            'C++': [
                'cpp',
                'c++',
            ],
            'C#': [
                'csharp',
                'c#',
                'cs',
            ],
            'HTML/CSS': [
                'html',
                'css',
                'html/css',
            ],
            'Other': 'other',
        }
        items = []
        for k, v in rep.items():
            if isinstance(v, list):
                for e in v:
                    items.append((k, e))
            else:
                items.append((k, v))
        rep = dict((re.escape(v), k) for k, v in items)
        pattern = re.compile("|".join(rep.keys()))
        language = pattern.sub(lambda m: rep[re.escape(m.group(0))],
                               language.lower())
        if language not in roles:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=ctx.error(
                'That is not a valid help role, please try again'))
        try:
            guild = self.bot.get_guild(681882711945641997)
            channel = guild.get_channel(814129029236916274)
            mention = guild.get_role(roles[language]).mention
        except AttributeError:
            channel = self.bot.get_channel(814129029236916274)
            mention = '<@&{}>'.format(roles[language])
        if not description:
            message = await ctx.send(embed=ctx.embed((
                'Please give a short description of what you need help with. '
                '(10-100 characters)'),
                                     title='What do you need help with?'))

            def check(m):
                return m.channel == message.channel and m.author == ctx.author
            try:
                msg = await self.bot.wait_for('message', check=check,
                                              timeout=30)
                description = msg.content
                await message.delete()
                await msg.delete()
            except asyncio.TimeoutError:
                ctx.command.reset_cooldown(ctx)
                return await ctx.send(embed=ctx.error('Timed out!'))
        if len(description) < 10 or len(description) > 100:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=ctx.error(
                'Your reason must be 10-100 total characters'))
        if not description.isascii():
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=ctx.error('Invalid description'))
        message = await ctx.send(embed=ctx.embed((
            f'Are you sure that you want to ping for {language} help? By '
            'reacting to this message you confirm that you have read '
            '<#799527165863395338> and <#754712400757784709>, and that you '
            'will follow them. Failure to follow the help rules may result in '
            'a punishment from the moderation team. Failure to follow the "how'
            ' to get help" instructions may result in you not being helped.'),
                                                 title='Please Confirm'))
        await message.add_reaction('\U00002705')
        await message.add_reaction('\U0000274c')

        def check(reaction, user):
            return (str(reaction.emoji) in ['\U00002705', '\U0000274c']
                    and user.id == ctx.author.id)
        try:
            reaction, user = await self.bot.wait_for('reaction_add',
                                                     check=check, timeout=30)
        except asyncio.TimeoutError:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=ctx.error('Timed out!'))
        await message.delete()
        if str(reaction.emoji) == '\U0000274c':
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=ctx.embed(title='Cancelled!'))
        embed = ctx.embed((
            '[Click Here]({0.message.jump_url}) to help {0.author.mention}'
            ).format(ctx), title=f'{language} Help'
        )
        embed.add_field(name='Description', value=description)
        await channel.send(content=mention,
                           embed=embed)
        await ctx.send(embed=ctx.embed((
            'Submitted your request for help. Please keep in mind that our '
            'helpers are human and may not be available immediately.'),
                       title='Success'))

    @commands.command(name='callstaff')
    @commands.is_owner()  # disabled for now
    @callstaff_check
    @commands.cooldown(1, 600, commands.BucketType.user)  # ten minute cooldown
    async def _callstaff(self, ctx, reason=None):
        """
        Request help in chat from staff. For less important issues, please
        @mention a single online staff member, and only use this command for
        larger issues such as raid, NSFW, staff abusing powers, etc.
        """
        message = await ctx.send(embed=ctx.embed((
            'Please give a short reason of why are calling staff. (10-100 '
            'characters)'), title='Reason'))

        def check(m):
            return m.channel == message.channel and m.author == ctx.author
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
            reason = msg.content
            await message.delete()
            await msg.delete()
        except asyncio.TimeoutError:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=ctx.error('Timed out!'))
        if len(reason) < 10 or len(reason) > 100:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=ctx.error(
                'Your reason must be 10-100 total characters'))
        if not reason.isascii():
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=ctx.error('Invalid reason'))
        channel = ctx.guild.get_channel(725747936776159243)  # staff chat rn
        mention = ctx.guild.get_role(681895900070543411).mention

        message = await ctx.send(embed=ctx.embed((
            'Are you sure that you want to request staff help? We always want'
            ' to help keep our server friendly for everyone, so we will be '
            'glad to help. However, using this command without a valid reason '
            'or misusing it can and will result in a punishment. For less '
            'important issues, please @mention a single online staff member, '
            'and only use this command for larger issues such as raid, NSFW, '
            'staff abusing powers, etc.'), title='Please Confirm'))
        await message.add_reaction('\U00002705')
        await message.add_reaction('\U0000274c')

        def check(reaction, user):
            return (str(reaction.emoji) in ['\U00002705', '\U0000274c']
                    and user.id == ctx.author.id)
        try:
            reaction, user = await self.bot.wait_for('reaction_add',
                                                     check=check, timeout=30)
        except asyncio.TimeoutError:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=ctx.error('Timed out!'))
        await message.delete()
        if str(reaction.emoji) == '\U0000274c':
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=ctx.embed(title='Cancelled!'))
        message = await channel.send(
            content=f'`{mention}`',  # Not pinging mods for now until its done
            embed=ctx.embed((
                '{0.author.mention} is requesting assistance in '
                '{0.channel.mention}. [Click Here]({0.message.jump_url}) to '
                'help them, and react with \U00002705 when the situation is **'
                'completely** under control.').format(ctx),
                            title='Report Submitted').add_field(name='Reason',
                                                                value=reason))
        await message.add_reaction('\U00002705')
        await ctx.send(embed=ctx.embed(
            'Submitted your request for a moderator.',
            title='Success'))


def setup(bot):
    bot.add_cog(Help(bot))
