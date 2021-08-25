import discord
from discord.ext import commands


class Archive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    @property
    def default_guild(self):
        return self.bot.get_guild(681882711945641997)
    
    
    @property
    def archive_category(self):
        return discord.utils.get(self.default_guild.categories, id=812881115705901088) # Defaulting to current archive category


    # Setting new archive category    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def archivecategory(self, ctx, category: discord.CategoryChannel=None):
        if category == None:
            await ctx.send("Please send a category id to set as archive category.")
        else:
            self.archive_category = category
            await ctx.send(f"✅ Successfully set `{category.name}` as archive category. ")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def archive(self, ctx, channel: discord.TextChannel=None):
        if self.archive_category == None:
            await ctx.send("Please set an archive category first. (`,archivecategory <category_id>`)")
        else:
            if channel == None:
                channel = ctx.channel
            await ctx.channel.purge(limit=1)
            await ctx.channel.edit(category=self.archive_category, sync_permissions=True)
            embed = discord.Embed(title="✅ Successfully Archived", description=f"`{channel.name}` has been successfully archived", color=discord.Color.green())
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Archive(bot))
