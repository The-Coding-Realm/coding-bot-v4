import discord
import time
from discord.ext import commands


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content: # invoke the command again if it is edited
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)

    @commands.command()
    async def ping(self, ctx):
        embed = ctx.embed(title='PONG!  :ping_pong:',description=f'<a:DiscordSpin:795546311319355393> Websocket Latency: {(self.bot.latency * 1000):.2f}ms\n:repeat: Round-Trip: Calculating...\n**:elephant: Database:** Calculating...')
        start = time.perf_counter()
        message = await ctx.send(embed=embed)
        end = time.perf_counter()
        trip = end - start
        embed.description = f'**<a:DiscordSpin:795546311319355393> Websocket Latency:** {(self.bot.latency * 1000):.2f}ms\n**:repeat: Round-Trip:** {(trip * 1000):.2f}ms\n**:elephant: Database:** Calcuating...'
        await message.edit(embed=embed)
        start = time.perf_counter()
        async with self.bot.pools.config.acquire() as connection:
            await connection.fetchval('SELECT prefixes FROM serverconf WHERE id = 0')
        end = time.perf_counter()
        database = end - start
        embed.description = f'**<a:DiscordSpin:795546311319355393> Websocket:** {(self.bot.latency * 1000):.2f}ms\n**:repeat: Round-Trip:** {(trip * 1000):.2f}ms\n**:elephant: Database:** {(database * 1000):.2f}ms'
        await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))