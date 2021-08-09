import discord
from discord.ext import commands
from dislash import ActionRow, Button, ButtonStyle, SelectMenu, SelectOption
import asyncio
import random
import json
from datetime import datetime
import os

with open('./ext/brawl.json', 'r') as f:
    data = json.load(f)

class Brawl(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.battle_hp = dict()
        self.ext_turns = dict()
        self.options = dict()
        self.placebo = dict()
        self.cooldowns = dict()
        self.info_sesh = dict()

    # ext = extra
    # exc = exception
    # atk = attack
    # dmg = damage
    # amt = amount

    async def write_action(self, id, action):
        with open(f'./storage/brawl{id}.txt', 'a') as f:
            f.write(f"{datetime.utcnow()}: {action}\n\n")

    async def endgame(self, ctx, user=None):
        await ctx.send("Game Log:", file=discord.File(f'./storage/brawl{ctx.author.id}.txt'))
        os.remove(f'./storage/brawl{ctx.author.id}.txt')

        if user:     
            del self.battle_hp[ctx.author.id]
            del self.battle_hp[user.id]
            try:
                del self.placebo[ctx.author.id]
            except:
                pass
            try:
                del self.placebo[user.id]
            except:
                pass

    @commands.group(invoke_without_command=True)
    async def brawl(self, ctx):
        embed=discord.Embed(title="TCA ***BRAWL*** Version 1.0.0", description="TCA Brawl is a turn-based fighting game written in Python and playable via a Discord bot. It includes all of your"
        " favorite TCA members and former TCA members.", color=discord.Color.random())
        embed.add_field(name="How to Play:", value="Grab a friend and take a bot channel. Use the `brawl battle` command to get started! The `battle` command has two aliases,"
        " `fight` and `start`. You will be prompted to pick a character, then the game will begin! If you want info on a character before playing, use `brawl info`.", inline=False)
        embed.add_field(name="All Commands:", value="`brawl`, `info`, `help`, `faq`.", inline=False)
        embed.add_field(name="Our FAQ", value="You may want to suggest a character, or you don't want your own person in the game. Check the FAQ to see how to deal with stuff.", inline=False)
        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/SydGsxAv1JDLCgm4qALPhcke7fv6TWoyVR2lQhEu-NI/%3Fsize%3D128/https/cdn.discordapp.com/icons/681882711945641997/a_2c2eeae970672cefecdb5b8536f42a47.gif")
        embed.set_image(url="https://media.discordapp.net/attachments/773319739581136916/864310160520249384/tcabrawl.png?width=1025&height=404")
        embed.set_footer(text="TCA Brawl created by UnsoughtConch.")

        faq = discord.Embed(title="Frequently Asked Questions", description="These aren't really frequently asked.", color=discord.Color.random())
        faq.add_field(name="Why am I not a character here?", value="This has a few answers. You either aren't very familiar, we haven't got to you yet, or we can't think of a good moveset for you.")
        faq.add_field(name="I'm in this game and don't want to be. How can I remove myself?", value="If you don't want to be in our game, please contact UnsoughtConch#9225.")
        faq.add_field(name="I want to make improvements to the game/a character. Can I?", value="Of course! Make a pull request from [the Coding Bot repository](https://github.com/The-Coding-Academy/Coding-Bot-v4) and edit the JSON or code!")
        faq.add_field(name="How can I suggest a character?", value="Contact UnsoughtConch#9225.")

        chars = discord.Embed(title="TCA ***BRAWL*** Characters")
        for character in data:
            char = data[character]
            desc = f"Class: {char['class']}\nAttack One: {char['atk_1']['name']}\nAttack Two: {char['atk_2']['name']}\nAbility: {char['ability']['name']}"
            chars.add_field(name=character, value=desc)
        chars.set_footer(text="You can get a more interactive and overall better info screen with ;info.")


        main_comps = ActionRow(
            Button(style=ButtonStyle.green, label="Information", emoji="❕", disabled=True),
            Button(style=ButtonStyle.blurple, label="FAQ", emoji="❔"),
            Button(style=ButtonStyle.secondary, label="Characters", emoji="🧑")
        )

        faq_comps = ActionRow(
            Button(style=ButtonStyle.green, label="Information", emoji="❕"),
            Button(style=ButtonStyle.blurple, label="FAQ", emoji="❔", disabled=True),
            Button(style=ButtonStyle.secondary, label="Characters", emoji="🧑")
        )

        chars_comps = ActionRow(
            Button(style=ButtonStyle.green, label="Information", emoji="❕"),
            Button(style=ButtonStyle.blurple, label="FAQ", emoji="❔"),
            Button(style=ButtonStyle.secondary, label="Characters", emoji="🧑", disabled=True)
        )

        msg = await ctx.send(embed=embed, components=[main_comps])


        on_click = msg.create_click_listener(timeout=60)


        @on_click.not_from_user(ctx.author)
        async def help_not_from_user(inter):
            await inter.reply("You have to be the command invoker to press these buttons.", ephemeral=True)

        @on_click.from_user(ctx.author)
        async def help_from_user(inter):
            await inter.reply(type=6)
            if str(inter.clicked_button.emoji) == "❔":
                await inter.message.edit(embed=faq, components = [faq_comps])
            
            elif str(inter.clicked_button.emoji) == "❕":
                await inter.message.edit(embed=embed, components = [main_comps])

            elif str(inter.clicked_button.emoji) == "🧑":
                await inter.message.edit(embed=chars, components=[chars_comps])

        @on_click.timeout
        async def help_timeout():
            buttons = ActionRow(
                Button(style=ButtonStyle.green, label="Information", emoji="❕", disabled=True),
                Button(style=ButtonStyle.blurple, label="FAQ", emoji="❔", disabled=True),
                Button(style=ButtonStyle.secondary, label="Characters", emoji="🧑", disabled=True),
            )

            await msg.edit(components=[buttons])

    @brawl.command()
    async def faq(self, ctx):
        faq = discord.Embed(title="Frequently Asked Questions", description="These aren't really frequently asked.", color=discord.Color.random())
        faq.add_field(name="Why am I not a character here?", value="This has a few answers. You either aren't very familiar, we haven't got to you yet, or we can't think of a good moveset for you.")
        faq.add_field(name="I'm in this game and don't want to be. How can I remove myself?", value="If you don't want to be in our game, please contact UnsoughtConch#9225.")
        faq.add_field(name="How can I suggest a character?", value="Contact UnsoughtConch#9225.")
        faq.add_field(name="I want to make improvements to the game/a character. Can I?", value="Of course! Make a pull request from [the Coding Bot repository](https://github.com/The-Coding-Academy/Coding-Bot-v4) and edit the JSON or code!")
        faq.add_field(name="I'm a character in this game and want to suggest changes to myself. Can I do that?", value="Of course you can! Contact UnsoughtConch#9225.")

        await ctx.send(embed=faq)
    
    @brawl.command()
    async def info(self, ctx):
        menu_opts = [] 
        char_embds = dict()
        chars = discord.Embed(title="TCA ***BRAWL*** Characters", description="Select a character from the select menu to get started!")
        for character in data:
            menu_opts.append(SelectOption(character, character))
            embed = discord.Embed(title="TCA ***BRAWL*** | " + character, color=discord.Color.random(), description=f"Character Class: {data[character]['class']}")
            embed.add_field(name="Attack One:", value=f"NAME: {data[character]['atk_1']['name']}\nDAMAGE: {data[character]['atk_1']['dmg']}")
            embed.add_field(name="Attack Two:", value=f"NAME: {data[character]['atk_2']['name']}\nDAMAGE: {data[character]['atk_2']['dmg']}")
            type = data[character]['ability']['type']
            if type == "heal":
                embed.add_field(name="Ability:", value=f"NAME: {data[character]['ability']['name']}\nTYPE: Healing\nPARTIES HEALED: {data[character]['ability']['health_gain_amt']}"
                f"\nHEALTH AMOUNT: {data[character]['ability']['health']}")
            elif type == "stun":
                embed.add_field(name="Ability:", value=f"NAME: {data[character]['ability']['name']}\nTYPE: Stun\nEXTRA TURNS: {data[character]['ability']['ext_turns']}")
            elif type == "options":
                embed.add_field(name="Ability:", value=f"NAME: {data[character]['ability']['name']}\nTYPE: Options\nOPTIONS: {', '.join([name for name in data[character]['ability']['options']])}")
            elif type == "placebo":
                embed.add_field(name="Ability:", value=f"NAME: {data[character]['ability']['name']}\nTYPE: Placebo\nEXTRA HEALTH: {data[character]['ability']['temp_xp']}\nTURNS KEPT: {data[character]['ability']['turns']}")

            stri = '\n'
            exc_list = []
            if 'dmg_exc' in data[character]['atk_1']:
                if 'name' in data[character]['atk_1']['dmg_exc']:
                    exc_list.append(f"CHARACTER: {data[character]['atk_1']['dmg_exc']['name']} | EXTRA DAMAGE: {data[character]['atk_1']['dmg_exc']['ext_dmg']}")
                elif "class" in data[character]['atk_1']['dmg_exc']:
                    exc_list.append(f"CLASS: {data[character]['atk_1']['dmg_exc']['class']} | EXTRA DAMAGE: {data[character]['atk_1']['dmg_exc']['ext_dmg']}")
            if 'dmg_exc' in data[character]['atk_2']:
                if 'name' in data[character]['atk_2']['dmg_exc']:
                    exc_list.append(f"CHARACTER: {data[character]['atk_2']['dmg_exc']['name']} | EXTRA DAMAGE: {data[character]['atk_2']['dmg_exc']['ext_dmg']}")
                elif "class" in data[character]['atk_2']['dmg_exc']:
                    exc_list.append(f"CLASS: {data[character]['atk_2']['dmg_exc']['class']} | EXTRA DAMAGE: {data[character]['atk_2']['dmg_exc']['ext_dmg']}")
            if exc_list is not None:
                stri = '\n'.join(exc_list)
                embed.add_field(name="Damage Exceptions:", value=stri)
            else:
                embed.add_field(name="Damage Exceptions:", value="No exceptions.")

            char_embds[character] = embed
            
        menu = SelectMenu(
            placeholder = "Select a character...",
            custom_id="infoMenu",
            options=menu_opts
        )

        if ctx.author.id in self.info_sesh:
            msg = self.info_sesh[ctx.author.id]
            pass
        else:
            msg = await ctx.send(embed=chars, components=[menu])
            self.info_sesh[ctx.author.id] = msg

        def check(m):
            return m.author == ctx.author

        try:
            inter = await msg.wait_for_dropdown(check=check, timeout=30)
        except:
            del self.info_sesh[ctx.author.id]
            return await msg.edit(components=[])

        await inter.reply(type=6)
        await msg.edit(embed=char_embds[[option.label for option in inter.select_menu.selected_options][0]])

        await self.info(ctx)

    @brawl.command(aliases=['fight', 'start'])
    async def battle(self, ctx, user:discord.Member):
        if user == ctx.author:
            return await ctx.send(embed=discord.Embed(title="You cannot battle yourself.", color=discord.Color.red()))

        embed = discord.Embed(title=f"Waiting for {user.display_name} to accept...", color=discord.Color.random())
        buttons = ActionRow(
            Button(style=ButtonStyle.green, label="Accept", emoji="✅"),
            Button(style=ButtonStyle.red, label="Deny", emoji="❌")
        )

        base = await ctx.send(embed=embed, components=[buttons])

        def check(m):
            return m.author == user

        try:
            inter = await base.wait_for_button_click(check=check, timeout=30)
        except:
            await base.edit(embed=f"{user.display_name} failed to respond in time!", color=discord.Color.red())
            await self.endgame(ctx)

        await inter.reply(type=6)

        embed = discord.Embed(title=f"{ctx.author.display_name}, choose your user!", color=discord.Color.random())

        char_menu_opts = []

        for character in data:
            char = data[character]
            desc = f"Class: {char['class']}\nAttack One: {char['atk_1']['name']}\nAttack Two: {char['atk_2']['name']}\nAbility: {char['ability']['name']}"
            embed.add_field(name=character, value=desc)
            char_menu_opts.append(SelectOption(character, character))

        char_menu = SelectMenu(placeholder="Choose your user!", options=char_menu_opts)

        await base.delete()

        base = await ctx.send(embed=embed, components=[char_menu])

        def check(m):
            return m.author == ctx.author

        try:
            inter = await base.wait_for_dropdown(check=check, timeout=120)
        except:
            await base.edit(embed=discord.Embed(f"{ctx.author.display_name} failed to respond in time!", color=discord.Color.red()))
            await self.endgame(ctx)

        await inter.reply(type=6)

        author_character = [option.label for option in inter.select_menu.selected_options][0]

        embed.title = f"{user.display_name}, choose your user!"

        await base.edit(embed=embed)

        def check(m):
            return m.author == user

        try:
            inter = await base.wait_for_dropdown(check=check, timeout=120)
        except:
            await ctx.send(embed=discord.Embed(f"{user.display_name} failed to respond in time!", color=discord.Color.red()))
            await self.endgame(ctx)

        await inter.reply(type=6)

        await base.delete()

        user_character = [option.label for option in inter.select_menu.selected_options][0]

        self.battle_hp[ctx.author.id] = 100
        self.battle_hp[user.id] = 100

        # True means author turn, False means user turn

        turne = True

        await self.write_action(ctx.author.id, f"{author_character} ({ctx.author.display_name}) picks a fight with {user_character} ({user.display_name})")

        while True:
            if self.battle_hp[ctx.author.id] < 1 or self.battle_hp[user.id] < 1:
                break
            if turne is True:
                turn = ctx.author
                character = author_character
                turn_hp = self.battle_hp[ctx.author.id]
                turn_class = data[character]['class']
                enemy = user
                enemy_character = user_character
                enemy_hp = self.battle_hp[user.id]
                enemy_class = data[enemy_character]['class']
            else:
                turn = user
                character = user_character
                turn_hp = self.battle_hp[user.id]
                turn_class = data[character]['class']
                enemy = ctx.author
                enemy_character = author_character
                enemy_hp = self.battle_hp[user.id]
                enemy_class = data[enemy_character]['class']

            if turn.id in self.placebo:
                if self.placebo[turn.id] == 0:
                    self.battle_hp[turn.id] = self.battle_hp[turn.id] - data[character]['ability']['temp_xp']
                else:
                    self.placebo[turn.id] = self.placebo[turn.id] - 1

            embed = discord.Embed(title=f"{turn.display_name}'s Turn")

            if turn_hp > 75:
                embed.color = discord.Color.green()
            elif turn_hp > 25:
                embed.color = discord.Color.gold()
            elif turn_hp <= 25:
                embed.color = discord.Color.red()

            embed.add_field(name="Character:", value=character)
            embed.add_field(name="HP:", value=turn_hp)
            embed.add_field(name="** **", value="** **")
            embed.add_field(name=data[character]['atk_1']['name'], value="ATTACK: " + data[character]['atk_1']['desc'])
            embed.add_field(name=data[character]['atk_2']['name'], value="ATTACK: " + data[character]['atk_2']['desc'])
            embed.add_field(name=data[character]['ability']['name'], value="ABILITY: " + data[character]['ability']['desc'])
            embed.set_thumbnail(url=data[character]['pfp'])

            options=[
                SelectOption(data[character]['atk_1']['name'], "atk_1"),
                SelectOption(data[character]['atk_2']['name'], "atk_2"),
                SelectOption(data[character]['ability']['name'], "ability")
            ]
            if turn.id in self.cooldowns:
                flag = False
                if 'atk_1' in self.cooldowns[turn.id]['moves']:
                    del self.cooldowns[turn.id]['moves']['atk_1']
                    del options[0]
                    flag = True

                if 'ability' in self.cooldowns[turn.id]['moves']:
                    if turn.id in self.ext_turns:
                        pass
                    else:
                        if self.cooldowns[turn.id]['moves']['ability'] == 1:
                            del self.cooldowns[turn.id]['moves']['ability']
                        else:
                            self.cooldowns[turn.id]['moves']['ability'] = self.cooldowns[turn.id]['moves']['ability'] - 1
                    if flag is True:
                        del options[1]
                    else:
                        del options[2]



            menu = SelectMenu(
                placeholder="Select a move...",
                options=options
            )

            msg1 = await ctx.send(embed=embed, components=[menu])

            def check(m):
                return m.author == turn

            try:
                inter = await msg1.wait_for_dropdown(check=check, timeout=120)
            except:
                await ctx.send(embed=discord.Embed(title=f"{turn.display_name} failed to respond on time, making {enemy.display_name} the winner!", color=discord.Color.red()))
                await self.endgame(ctx, user)
                return

            await inter.reply(type=6)

            move = [option.value for option in inter.select_menu.selected_options][0]

            if move == "ability":
                if turn.id in self.cooldowns:
                    self.cooldowns[turn.id]['moves']['ability'] = 2
                else:
                    self.cooldowns[turn.id] = {'moves': {'ability': 2}}
                if data[character][move]['type'] == 'heal':
                    self.battle_hp[turn.id] = self.battle_hp[turn.id] + data[character][move]['health']

                    if data[character][move]['health_gain_amt'] == 2:
                        self.battle_hp[enemy.id] = self.battle_hp[enemy.id] + data[character][move]['health']
                    
                        phrase = f"{turn.display_name} healths both parties with {data[character][move]['name']} and gains {data[character][move]['health']} health!"

                    else:
                        phrase = f"{turn.display_name} healths themself with {data[character][move]['name']} and gains {data[character][move]['health']} health!"

                elif data[character][move]['type'] == 'stun':
                    self.ext_turns[turn.id] = data[character][move]['ext_turns']

                    phrase = f"{turn.display_name} stuns {enemy.display_name} with {data[character][move]['name']} and gains {self.ext_turns[turn.id]} extra turns!"

                elif data[character][move]['type'] == 'options':
                    buttons = ActionRow(
                        Button(style=ButtonStyle.green, label="Chill", emoji="😃"),
                        Button(style=ButtonStyle.red, label="Angry", emoji="😡")
                    )

                    msg2 = await ctx.send(embed=discord.Embed(title=f"{turn.display_name}, what option would you like to invoke?"), components=[buttons])

                    def check(m):
                        return m.author == turn
                    try:
                        inter = await msg2.wait_for_button_click(check=check, timeout=60)
                    except:
                        await self.endgame(ctx, user)
                        return await ctx.send(embed=discord.Embed(title=f"{turn.display_name} didn't choose in time, making {enemy.display_name} the winner!", color=discord.Color.red()))

                    await inter.reply(type=6)

                    option = inter.clicked_button.label

                    if data[character][move]['options'][option]['ext_dmg'] == 0:
                        try:
                            del self.options[turn.id]
                        except:
                            pass

                    self.options[turn.id] = data[character][move]['options'][option]['ext_dmg']

                    phrase = f"{turn.display_name} chooses {option} with {data[character][move]['name']} and gains {data[character][move]['options'][option]['ext_dmg']} extra power!"

                    await msg2.delete()
                
                elif data[character][move]['type'] == "placebo":
                    self.battle_hp[turn.id] = self.battle_hp[turn.id] + data[character][move]['temp_xp']
                    self.placebo[turn.id] = data[character][move]['turns']

                    phrase = f"{turn.display_name} invokes a placebo with {data[character][move]['name']} that gives them {data[character][move]['temp_xp']} more HP for {data[character][move]['turns']} turns!"

            else:
                try:
                    dmg_class = data[character][move]['dmg_exc']['class']
                    if dmg_class == enemy_class:
                        ext_dmg = data[character][move]['dmg_exc']['ext_dmg']
                        dmg = ext_dmg + data[character][move]['dmg']
                    else:
                        dmg = data["wefrefwfwef"]
                except KeyError:
                    try:
                        dmg_char = data[character][move]['dmg_exc']['name']
                        if dmg_char == enemy_character:
                            dmg = data[character][move]['dmg_exc']['ext_dmg'] + data[character][move]['dmg']
                    except KeyError:
                        dmg = data[character][move]['dmg']

                if move == 'atk_1':
                    if turn.id in self.cooldowns:
                        self.cooldowns[turn.id]['moves']['atk_1'] = 0
                    else:
                        self.cooldowns[turn.id] = {'moves': {'atk_1': 0}}

                if turn.id in self.options:
                    ext_dmg = self.options[turn.id]
                    dmg = ext_dmg + dmg
                    del self.options[turn.id]
                
                phrase = f"{character} deals {dmg} damage to {enemy_character} with {data[character][move]['name']}"

                if turne is True:
                    self.battle_hp[user.id] = self.battle_hp[user.id] - dmg
                else:
                    self.battle_hp[ctx.author.id] = self.battle_hp[ctx.author.id] - dmg
            
            await msg1.delete()

            await self.write_action(ctx.author.id, phrase)
            phrsmsg = await ctx.send(phrase)

            try:
                turns = self.ext_turns[turn.id]
                if turns == 0:
                    del self.ext_turns[turn.id]
                    e = self.battle_hp[2]
                self.ext_turns[turn.id] = self.ext_turns[turn.id] - 1
                turne = True if turn == ctx.author else False
            except:
                turne = True if turn == user else False

            await asyncio.sleep(5)

            await phrsmsg.delete()

        if self.battle_hp[ctx.author.id] < 1:
            embed = discord.Embed(title=user_character + ": " + data[user_character]['catchphrase'] if user_character != 'BobDotCom' else random.choice(data[user_character]['catchphrase']), 
            description=f"{user_character} won!")
            embed.set_footer(text=f"Remaining HP: {turn_hp}")
            await ctx.send(embed=embed)
            await self.endgame(ctx, user)
        else:
            embed = discord.Embed(title=author_character + ": " + data[author_character]['catchphrase'] if author_character != 'BobDotCom' else random.choice(data[author_character]['catchphrase']), 
            description=f"{author_character} won!")
            embed.set_footer(text=f"Remaining HP: {turn_hp}")
            await ctx.send(embed=embed)
            await self.write_action(ctx.author.id, f"{ctx.author.display_name} ({author_character}) wins the battle with {turn_hp} HP remaining.")
            await self.endgame(ctx, user)

def setup(client):
    client.add_cog(Brawl(client))
