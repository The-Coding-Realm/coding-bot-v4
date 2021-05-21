import discord
import random
import io
from discord.ext import commands, menus


def percentage_bool(x: int) -> bool:
    if x > 100:
        raise ValueError('Number must be ≤ 100')
    return bool(int(random.choice(list("1" * x) + list("0" * (100 - x)))))


def is_premium():
    def predicate(ctx):
        return ctx.bot.sr_api_premium
    return commands.check(predicate)


class LyricsMenu(menus.ListPageSource):
    def __init__(self, data, ctx):
        total = []
        current = ''
        for line in data.lyrics.splitlines():
            if len(current + line) <= 2048 and len((current + line).splitlines()) <= 25:
                current += line
            else:
                total.append(current)
                current = ''
        if current:
            total.append(current)
        super().__init__(total, per_page=1)
        self.ctx = ctx
        self.data = data

    async def format_page(self, menu, entry):
        embed = self.ctx.embed(title=self.data.title, description=entry, url=self.data.link)
        embed.set_footer(text=f'Page {menu.current_page + 1}/{menu._source.get_max_pages()} | ' + embed.footer.text,
                         icon_url=embed.footer.icon_url)
        embed.set_author(name=self.data.author)
        if self.data.thumbnail:
            embed.set_thumbnail(url=self.data.thumbnail)
        return embed


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
        """
        Pet a user
        """
        try:
            gif = self.bot.sr_api.petpet(user.avatar_url)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        buf = io.BytesIO(await gif.read())
        await ctx.send(file=discord.File(buf, filename=f"{user.name}.gif"))

    @commands.command(name='animal')
    async def _animal(self, ctx, animal=None):
        """
        Options are "dog", "cat", "panda", "fox", "red_panda", "koala", "birb", "bird", "racoon", "raccoon", "kangaroo"
        """
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
        """
        Get a discord bot token lol
        """
        try:
            token = await self.bot.sr_api.bot_token()
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        await ctx.send(token)

    @commands.group(invoke_without_command=True)
    async def anime(self, ctx):
        """
        Anime gif commands
        """
        await ctx.send_help('anime')

    @anime.command(name='wink')
    async def _anime_wink(self, ctx):
        """
        anime wink gif
        """
        try:
            image = await self.bot.sr_api.get_gif('wink')
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title='Wink')
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    @anime.command(name='pat')
    async def _anime_pat(self, ctx):
        """
        anime pat gif
        """
        try:
            image = await self.bot.sr_api.get_gif('pat')
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title='Pat')
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    @anime.command(name='hug')
    async def _anime_hug(self, ctx):
        """
        anime hug gif
        """
        try:
            image = await self.bot.sr_api.get_gif('hug')
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title='Hug')
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    @anime.command(name='facepalm', aliases=['fp'])
    async def _anime_facepalm(self, ctx):
        """
        anime facepalm gif
        """
        try:
            image = await self.bot.sr_api.get_gif('face-palm')
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title='Face Palm')
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    @commands.command(name='chatbot', aliases=['chat'])
    @is_premium()
    async def _chatbot(self, ctx, *, message):
        """
        ai chatbot
        """
        try:
            reply = await self.bot.sr_api.chatbot(message)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        await ctx.send_embed(title='Chatbot Says', description=reply)

    @commands.command(name='minecraft', aliases=['mc', 'mcuser'])
    async def _minecraft(self, ctx, *, username):
        """
        minecraft user lookup
        """
        try:
            user = await self.bot.sr_api.mc_user(username)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title=user.name, description=user.formatted_history)
        embed.set_author(name=f'UUID: {user.uuid}')
        await ctx.send(embed=embed)

    @commands.command(name='lyrics')
    async def _lyrics(self, ctx, *, song):
        """
        get song lyrics
        """
        try:
            lyrics = await self.bot.sr_api.get_lyrics(song)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        pages = menus.MenuPages(source=LyricsMenu(lyrics, ctx), delete_message_after=True)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(Fun(bot))
