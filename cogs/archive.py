import discord
from discord.ext import commands


class Archive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._archive_category = None

    @property
    def default_guild(self):
        return self.bot.get_guild(681882711945641997)

    @property
    def archive_category(self):
        if self._archive_category is not None:
            return self._archive_category
        return discord.utils.get(self.default_guild.categories, id=812881115705901088) if self.default_guild else None

    @archive_category.setter
    def archive_category(self, category):
        self._archive_category = category

    # Setting new archive category    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def archivecategory(self, ctx, category: discord.CategoryChannel = None):
        if category is None:
            await ctx.send("Please send a category id to set as archive category.")
        else:
            self._archive_category = category
            await ctx.send(f"✅ Successfully set `{category.name}` as archive category. ")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def archive(self, ctx, channel: discord.TextChannel = None):
        if self.archive_category is None:
            await ctx.send("Please set an archive category first. (`,archivecategory <category_id>`)")
        else:
            if channel is None:
                channel = ctx.channel
            await ctx.channel.purge(limit=1)
            await ctx.channel.edit(category=self.archive_category, sync_permissions=True)
            embed = discord.Embed(title="✅ Successfully Archived",
                                  description=f"`{channel.name}` has been successfully archived",
                                  color=discord.Color.green())
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Archive(bot))
