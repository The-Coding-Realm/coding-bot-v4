import discord
import os
import sys
import asyncio
import psutil
import logging
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter

class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='eval')
    async def _eval(self, ctx, *, code: codeblock_converter):
        """Eval some code"""
        cog = self.bot.get_cog("Jishaku")
        await cog.jsk_python(ctx, argument=code)
        
    @commands.command(name='refresh')
    async def _refresh(self, ctx):
        """Refresh the bot by invoking `jsk git pull` and `restart`"""
        cog = self.bot.get_cog("Jishaku")
        await cog.jsk_git(ctx, argument=codeblock_converter('pull'))
        restart = self.bot.get_command('restart')
        await ctx.invoke(restart)

    @commands.command(name='restart')
    async def _restart(self, ctx, flag=None):
        """
        Restart the bot. Will wait for any running commands to stop. Use --force to ignore any running commands and proceed with the restart
        """
        if not (flag == '--force' or flag == '-f'):
            if self.bot.processing_commands > 1:
                embed = discord.Embed(title='Commands in progress...', description=f'Retrying in 30 seconds. Use `{ctx.prefix}restart --force` to force restart.', timestamp=ctx.message.created_at)
                embed.set_footer(text=f'{self.bot.processing_commands - 1} commands currently in progess')
                await ctx.send(embed=embed)
                for i in range(10):
                    await asyncio.sleep(30)
                    if self.bot.processing_commands > 1:
                        embed = discord.Embed(title='Commands in progress...', description=f'Retrying in 30 seconds. Use `{ctx.prefix}restart --force` to force restart.', timestamp=ctx.message.created_at)
                        embed.set_footer(text=f'{self.bot.processing_commands - 1} commands currently in progess')
                        await ctx.send(embed=embed)
                    else:
                        break
                if self.bot.processing_commands > 1:
                    embed = discord.Embed(title='Restart Failed', description=f'{self.bot.processing_commands - 1} commands currently in progess. Use `{ctx.prefix}restart --force` to force restart.', timestamp=ctx.message.created_at)
                    return await ctx.send(embed=embed)
        embed = discord.Embed(title="Be right back!")
        await ctx.send(embed=embed)
        self.bot.helpers.storage(self.bot, 'restart_channel', ctx.channel.id)
        if sys.stdin.isatty(): # if the bot was run from the command line instead of from systemctl
            # os.execv('sudo python', sys.argv) os.path.abspath(__file__)
            try:
                p = psutil.Process(os.getpid())
                for handler in p.open_files() + p.connections():
                    os.close(handler.fd)
            except Exception as e:
                logging.error(e)
            python = sys.executable
            os.execl(python, python, *sys.argv)
        await self.bot.logout()
        embed = ctx.error('Failed to restart')
        await ctx.send(embed=embed)

    @commands.command(name='shutdown',aliases=['off','die','shut','kill'])
    async def _shutdown(self, ctx, flag=None):
        if flag == '--wait' or flag == '-w':
            if self.bot.processing_commands > 1:
                embed = discord.Embed(title='Commands in progress...', description=f'Retrying in 30 seconds.', timestamp=ctx.message.created_at)
                embed.set_footer(text=f'{self.bot.processing_commands - 1} commands currently in progess')
                await ctx.send(embed=embed)
                for i in range(10):
                    await asyncio.sleep(30)
                    if self.bot.processing_commands > 1:
                        embed = discord.Embed(title='Commands in progress...', description=f'Retrying in 30 seconds.', timestamp=ctx.message.created_at)
                        embed.set_footer(text=f'{self.bot.processing_commands - 1} commands currently in progess')
                        await ctx.send(embed=embed)
                    else:
                        break
        await ctx.send(embed=ctx.embed(title='Shutting Down'))
        if sys.stdin.isatty():
            await self.bot.logout()
        else:
            if len(sys.argv) > 1:
                os.system(f"sudo {'stoprewrite' if sys.argv[1] == 'rewrite' else 'stopmain'}")
            await asyncio.sleep(1)
            await ctx.send(embed=ctx.error('Failed to stop systemd service, attempting to shut down both services'))
            os.system(f'sudo stopall')
            await asyncio.sleep(1)
            await ctx.send(embed=ctx.error('Failed to stop systemd service, attempting to logout normally'))
            await self.bot.logout()

    @commands.command()
    async def disable(self, ctx, toggle: bool = None):
        """
        Disable the bot in case of an exploit, major bug, or other emergency. The bot will remain online, but only bot owners will be able to run commands on it
        """
        self.bot.disabled = not self.bot.disabled if toggle is None else toggle
        embed = ctx.embed(title='Bot Status', timestamp=ctx.message.created_at)
        embed.add_field(name='Disabled',value=self.bot.disabled)
        self.bot.helpers.storage(self.bot, key='disabled', value=self.bot.disabled)
        await ctx.send(embed=embed)

    async def cog_check(self, ctx):
        return ctx.author.id in self.bot.owner_ids

def setup(bot):
    bot.add_cog(Owner(bot))
