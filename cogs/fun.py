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

class BaseMenu(menus.ListPageSource):
    def __init__(self, content, ctx):
        total = []
        current = []
        for line in content.splitlines():
            if len('\n'.join(current) + line) <= 2048 and len(('\n'.join(current) + line).splitlines()) <= 25:
                current.append(line)
            else:
                total.append('\n'.join(current))
                current = []
        if current:
            total.append('\n'.join(current))
        super().__init__(total, per_page=1)
        self.embed = ctx.embed()

    async def format_page(self, menu, entry):
        embed = self.embed.copy()
        embed.description = entry
        embed.set_footer(text=f'Page {menu.current_page + 1}/{menu._source.get_max_pages()} | ' + embed.footer.text,
                         icon_url=embed.footer.icon_url)
        return embed


class LyricsMenu(BaseMenu):
    def __init__(self, data, ctx):
        super().__init__(data.lyrics, ctx)
        self.embed.title = data.title
        self.embed.url = data.link
        self.embed.set_author(name=data.author)
        if data.thumbnail:
            self.embed.set_thumbnail(url=data.thumbnail)


class DefinitionMenu(BaseMenu):
    def __init__(self, data, ctx):
        super().__init__(data.definition.strip('\n').strip(' '), ctx)
        self.embed.title = data.word.title()


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
            gif = self.bot.sr_api.amongus(user.name, user.avatar.url, impostor)
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
            gif = self.bot.sr_api.petpet(user.avatar.url)
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

    @commands.command(name='owolyrics')
    async def _owolyrics(self, ctx, *, song):
        """
        get owo song lyrics
        """
        try:
            lyrics = await self.bot.sr_api.get_lyrics(song, owo=True)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        lyrics.title += ' (OwO)'
        pages = menus.MenuPages(source=LyricsMenu(lyrics, ctx), delete_message_after=True)
        await pages.start(ctx)

    @commands.group(invoke_without_command=True)
    async def binary(self, ctx):
        """
        binary commands
        """
        await ctx.send_help('binary')

    @binary.command(name='encode')
    async def _binary_encode(self, ctx, *, text):
        """
        encode binary
        """
        try:
            binary = await self.bot.sr_api.encode_binary(text)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        await ctx.send_embed(title='Binary Output', description=binary)

    @binary.command(name='decode')
    async def _binary_decode(self, ctx, *, binary):
        """
        decode binary
        """
        try:
            text = await self.bot.sr_api.decode_binary(binary)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        await ctx.send_embed(title='Text Output', description=text)

    @commands.group(invoke_without_command=True)
    async def base64(self, ctx):
        """
        base64 commands
        """
        await ctx.send_help('base64')

    @base64.command(name='encode')
    async def _base64_encode(self, ctx, *, text):
        """
        encode base64
        """
        try:
            b64 = await self.bot.sr_api.encode_base64(text)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        await ctx.send_embed(title='Base64 Output', description=b64)

    @base64.command(name='decode')
    async def _base64_decode(self, ctx, *, base64):
        """
        decode base64
        """
        try:
            text = await self.bot.sr_api.decode_base64(base64)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        await ctx.send_embed(title='Text Output', description=text)

    @commands.command(name="meme")
    async def _meme(self, ctx):
        """
        you are a meem
        """
        try:
            meme = await self.bot.sr_api.get_meme()
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title='Meme', description=meme.caption)
        embed.set_image(url=meme.image)
        embed.set_footer(text=f'Meme {meme.id} ({meme.category}) | ' + embed.footer.text,
                         icon_url=embed.footer.icon_url)
        await ctx.send(embed=embed)

    @commands.command(name='animequote')
    async def _anime_quote(self, ctx):
        """
        random anime quote
        """
        try:
            quote = await self.bot.sr_api.anime_quote()
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        embed = ctx.embed(title=quote.character, description=quote.quote)
        embed.set_author(name=quote.anime)
        await ctx.send(embed=embed)

    @commands.command(name='define')
    async def _define(self, ctx, word):
        """
        define a word
        """
        try:
            definition = await self.bot.sr_api.define(word)
        except:  # noqa: E722
            return await ctx.send_error('Error with API, please try again later')
        pages = menus.MenuPages(source=DefinitionMenu(definition, ctx), delete_message_after=True)
        await pages.start(ctx)

    async def cog_before_invoke(self, ctx):
        await ctx.trigger_typing()


def setup(bot):
    bot.add_cog(Fun(bot))
