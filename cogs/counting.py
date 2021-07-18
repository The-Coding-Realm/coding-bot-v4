from discord import Message
from discord.ext import commands


class Counting(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.current = None
        self.bot.loop.create_task(self.init())

    async def init(self) -> None:
        await self.bot.wait_until_ready()
        self.channel = self.bot.get_channel(
            757193068431671327  # The counting channel in TCA
        )
        self.last = self.channel.last_message or await self.channel.fetch_message(
            self.channel.last_message_id
        )
        self.current = int(self.last.content)

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.channel != self.channel or message.author.bot:
            return
        if (
            not message.content.isdigit()
            or int(message.content) != self.current + 1
            or message.author == self.last.author
        ):
            return await message.delete()
        self.last = message
        self.current += 1

    @commands.Cog.listener()
    async def on_message_edit(self, before: Message, after: Message) -> None:
        if before == self.last:
            if (not after.content.isdigit()) or int(after.content) != self.current:
                await after.delete()
        else:
            await after.delete()

    @commands.Cog.listener()
    async def on_message_delete(self, message: Message) -> None:
        if message == self.last:
            self.last = await message.channel.send(
                f"{self.current} (message from {message.author.name} was deleted)"
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Counting(bot))
