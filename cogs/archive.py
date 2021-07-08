import discord
from discord.ext import commands

class Archive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.archive_category = None

    # Setting new archive category    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def archivecategory(self, ctx, category: discord.CategoryChannel=None):
        if category == None:
            await ctx.send("Please send a category id to set as archive category.")
        else:
            self.bot.archive_category = category
            await ctx.send(f"✅ Successfully set `{category.name}` as archive category. ")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def archive(self, ctx, channel: discord.TextChannel=None):
        if self.bot.archive_category == None:
            await ctx.send("Please set an archive category first. (`,archivecategory <category_id>`)")
        else:
            if channel == None:
                channel = ctx.channel
            await ctx.channel.purge(limit=1)
            embed = discord.Embed(title="✅ Successfully Archived", description=f"`{channel.name}` has been successfully archived", color=discord.Color.green())
            await ctx.send(embed=embed)

            # archive_category = discord.utils.get(ctx.guild.channels, name="archive")
            await ctx.channel.edit(category=self.bot.archive_category)
            
            overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
