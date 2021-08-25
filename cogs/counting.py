from discord import Message
from discord.ext import commands


class Counting(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.current = None
        self.active = True
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
        if not self.active or message.channel != self.channel or message.author.bot:
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
        if not self.active or after.channel != self.channel or after.author.bot:
            return
        if before == self.last:
            if (not after.content.isdigit()) or int(after.content) != self.current:
                await after.delete()
        else:
            await after.delete()

    @commands.Cog.listener()
    async def on_message_delete(self, message: Message) -> None:
        if self.active and message == self.last:
            self.last = await message.channel.send(
                f"{self.current} (message from {message.author.name} was deleted)"
            )

    @commands.group(invoke_without_command=True)
    async def counting(self, ctx: commands.Context) -> None:
        """
        Commands related to the counting system
        """
        await ctx.send_help("counting")

    @commands.has_permissions(manage_channels=True)
    @counting.command(name="toggle")
    async def _counting_toggle(self, ctx: commands.Context) -> None:
        """
        Toggle counting state
        """
        if self.active:
            self.active = False
            await ctx.send("Counting has been turned off.")
        else:
            self.active = True
            await ctx.send("Counting has been turned on.")

    @commands.has_permissions(manage_channels=True)
    @counting.command(name="set")
    async def _counting_set(self, ctx: commands.Context, number: int) -> None:
        """
        Set the current number
        """
        self.current = number
        await ctx.send(f"Set current number to {number}")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Counting(bot))
