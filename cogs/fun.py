import discord
import random
from discord.ext import commands


def percentage_bool(x: int) -> bool:
    if x > 100:
        raise ValueError('Number must be ≤ 100')
    return bool(int(random.choice(list("1" * x) + list("0" * (100 - x)))))

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sr_api_premium = False

    @commands.check
    async def is_premium(self, ctx):
        return self.sr_api_premium

    @commands.command(name='eject', aliases=['amongus'])
    @is_premium()
    async def _eject(self, user: discord.Member = None, impostor: bool = None):
        """
        Eject someone. Among us is cringe tho
        """
        user = user or ctx.author
        impostor = percentage_bool(10) if impostor is None else impostor
        try:
            gif = self.bot.sr_api.amongus(user.name, user.avatar_url, impostor)
        except:
            return await ctx.send_error('Error with API, please try again later')
        buf = BytesIO(await gif.read())
        await ctx.send(file=discord.File(buf, filename=f"{member.name}.gif"))

    @commands.command(name='pet', aliases=['petpet'])
    @is_premium()
    async def _pet(self, user: discord.member):
        try:
            gif = self.bot.sr_api.petpet(user.avatar_url)
        except:
            return await ctx.send_error('Error with API, please try again later')
        buf = BytesIO(await gif.read())
        await ctx.send(file=discord.File(buf, filename=f"{member.name}.gif"))

    @commands.command(name='animal')
    async def _animal(self, animal=None):
        options = ("dog", "cat", "panda", "fox", "red_panda", "koala", "birb",
                   "bird", "racoon", "raccoon", "kangaroo")
        if not animal:
            animal = random.choice(options)
        if animal not in options:
            return await ctx.send_error('Invalid animal')
        try:
            response = await self.bot.sr_api.get_animal(animal)
            image = response['image']
            fact = response['fact']
        except:
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title=animal.title(), description=fact)
        embed.set_image(url=image)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
