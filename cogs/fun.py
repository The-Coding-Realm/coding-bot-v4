import discord
import random
import io
from discord.ext import commands


def percentage_bool(x: int) -> bool:
    if x > 100:
        raise ValueError('Number must be ≤ 100')
    return bool(int(random.choice(list("1" * x) + list("0" * (100 - x)))))


def is_premium():
    def predicate(ctx):
        return ctx.bot.sr_api_premium
    return commands.check(predicate)


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='eject', aliases=['amongus'])
    @is_premium()
    async def _eject(self, ctx, user: discord.Member = None, impostor: bool = None):
        """
        Eject someone. Among us is cringe tho
        """
        user = user or ctx.author
        impostor = percentage_bool(10) if impostor is None else impostor
        try:
            gif = self.bot.sr_api.amongus(user.name, user.avatar_url, impostor)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        buf = io.BytesIO(await gif.read())
        await ctx.send(file=discord.File(buf, filename=f"{user.name}.gif"))

    @commands.command(name='pet', aliases=['petpet'])
    @is_premium()
    async def _pet(self, ctx, user: discord.member):
        try:
            gif = self.bot.sr_api.petpet(user.avatar_url)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        buf = io.BytesIO(await gif.read())
        await ctx.send(file=discord.File(buf, filename=f"{user.name}.gif"))

    @commands.command(name='animal')
    async def _animal(self, ctx, animal=None):
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
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title=animal.title(), description=fact)
        embed.set_image(url=image)
        await ctx.send(embed=embed)

    @commands.command(name="token", aliases=['bottoken', 'faketoken'])
    async def _token(self, ctx):
        try:
            token = await self.bot.sr_api.bot_token()
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        await ctx.send(token)

    @commands.group(invoke_without_command=True)
    async def anime(self, ctx):
        await ctx.send_help('anime')

    @anime.command(name='wink')
    async def _anime_wink(self, ctx):
        try:
            image = await self.bot.sr_api.get_gif('wink')
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title='Wink')
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    @anime.command(name='pat')
    async def _anime_pat(self, ctx):
        try:
            image = await self.bot.sr_api.get_gif('pat')
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title='Pat')
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    @anime.command(name='hug')
    async def _anime_hug(self, ctx):
        try:
            image = await self.bot.sr_api.get_gif('hug')
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title='Hug')
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    @anime.command(name='facepalm', aliases=['fp'])
    async def _anime_facepalm(self, ctx):
        try:
            image = await self.bot.sr_api.get_gif('face-palm')
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title='Face Palm')
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
