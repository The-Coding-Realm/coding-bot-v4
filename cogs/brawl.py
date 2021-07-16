import discord
from discord.ext import commands
from dislash import ActionRow, Button, ButtonStyle, SelectMenu, SelectOption
import asyncio
import random

data = {
    "BobDotCom": {
        "class": "staff",
        "pfp": "https://cdn.discordapp.com/avatars/690420846774321221/5a2e465e7a4a56aa18b50ee94cde4229.webp",
        "catchphrase": ["Hmm", "Lol.", "LMFAO", "Poggers."],
        "atk_1": {
            "name": "Make a Bot",
            "desc": "Make a Discord bot to harass your opponent.",
            "type": "attack",
            "dmg": 10,
            "dmg_exc": {
                "class": "coder",
                "ext_dmg": -5
            },
        },
        "atk_2": {
            "name": "Mess Around",
            "desc": "Confuse your opponent by messing with them.",
            "type": "attack",
            "dmg": 5
        },
        "ability": {
            "name": "Go Camping",
            "type": "stun",
            "desc": "Make your opponent wait for you to get back from camping.",
            "ext_turns": 2,
        }
    },

    "ShadowX": {
        "class": "staff",
        "pfp": "https://cdn.discordapp.com/avatars/698225613617496094/cf5b4bc8b4a24432a1c4dcb171c701a2.webp",
        "catchphrase": "I bully without discrimination.",
        "atk_1": {
            "name": "Yell",
            "desc": "Yell at someone for some reason.",
            "type": "attack",
            "dmg": 10,
            "dmg_exc": {
                "character": "bob",
                "ext_dmg": 10,
            },
        },
        "atk_2": {
            "name": "Lecture",
            "desc": "Lecture your opponent about something.",
            "type": "attack",
            "dmg": 5,
            "dmg_exc": {
                "class": "staff",
                "ext_dmg": 2
            }
        },
        "ability": {
            "name": "Switch Moods",
            "desc": "Switch between angry and chill in a flash.",
            "type": "options",
            "options": {
                "Chill": {
                    "ext_dmg": 0,
                    "color": ButtonStyle.green,
                    "emoji": "😃"
                },
                "Angry": {
                    "ext_dmg": 5,
                    "color": ButtonStyle.red,
                    "emoji": "😡",
                }
            }
        },
    },

    "Swas.py": {
        "class": "owner",
        "pfp": "https://cdn.discordapp.com/avatars/556119013298667520/a_8f8ca8f13d8db81c818c61c5d7c89ba2.webp",
        "catchphrase": "When the impostor is sus.",
        "atk_1" : {
            "name": "Demote",
            "desc": "Demote someone.",
            "type": "attack",
            "dmg": 10,
            "dmg_exc": {
                "class": "staff",
                "ext_dmg": 5
            },
        },
        "atk_2": {
            "name": "Succeed",
            "desc": "Succeed at being a YouTuber/programmer and piss your opponent off because they can't.",
            "type": "attack",
            "dmg": 5,
            "dmg_exc": {
                "class": "coder",
                "ext_dmg": -4
            }
        },
        "ability": {
            "name": "Make Video",
            "type": "stun",
            "desc": "Make your opponent watch the video you just made.",
            "ext_turns": 2
        }
    },

    "Nerd": {
        "class": "coder",
        "pfp": "https://cdn.discordapp.com/avatars/186202944461471745/7435b73891f328a1c7d097a169f6511e.webp",
        "catchphrase": "It's refractor time.",
        "atk_1": {
            "name": "The Missile",
            "desc": "You see, it knows where it is because it knows where it isn't.",
            "type": "attack",
            "dmg": 10,
        },
        "atk_2": {
            "name": "Use AI",
            "desc": "Use Artificial Intelligence to harm your opponent.",
            "type": "attack",
            "dmg": 5,
            "dmg_exc": {
                "class": "coder",
                "ext_dmg": -3
            },
        },
        "ability": {
            "name": "Help",
            "desc": "Help your opponent with code and get thanked.",
            "type": "heal",
            "health_gain_amt": 2,
            "health": 5
        }
    },

    "Tapu": {
        "class": "member",
        "pfp": "https://cdn.discordapp.com/avatars/673105565689446409/1c51e7f5efdb7ec3a74e5dde7c8123fe.webp",
        "catchphrase": "Test.",
        "atk_1": {
            "name": "Risk Warn",
            "desc": "Send a message that's warn debatable.",
            "type": "attack",
            "dmg": 5,
            "dmg_exc": {
                "class": "staff",
                "ext_dmg": 5
            },
        },
        "atk_2": {
            "name": "Meme",
            "desc": "Send memes in chat.",
            "type": "attack",
            "dmg": 5
        },
        "ability": {
            "name": "Leave",
            "type": "heal",
            "health_gain_amt": 1,
            "desc": "Leave the server.",
            "health": -100
        }
    },

    "Pleb": {
        "class": "member",
        "pfp": "https://cdn.discordapp.com/avatars/797448912419422208/3fede35d3233f33b10540c0836e4b9d8.webp",
        "catchphrase": "Nothing.",
        "atk_1": {
            "name": "Raid",
            "desc": "Raid TCA with spambots or something because you don't like it.",
            "type": "attack",
            "dmg": 5,
            "dmg_exc": {
                "class": "staff",
                "ext_dmg": 10
            }
        },
        "atk_2": {
            "name": "Hate on TCA",
            "type": "attack",
            "desc": "Be angry at TCA for some reason.",
            "dmg": 10,
            "dmg_exc": {
                "class": "staff",
                "ext_dmg": -5
            }
        },
        "ability": {
            "name": "Tryhard",
            "type": "placebo",
            "desc": "Be a tryhard and think you're cool.",
            "temp_xp": 10,
            "turns": 1
        }
    },

    "Average TCA Member": {
        "class": "member",
        "pfp": "https://cdn.discordapp.com/icons/681882711945641997/a_2c2eeae970672cefecdb5b8536f42a47.webp",
        "catchphrase": "Yeah but how do I fix this error?",
        "atk_1": {
            "name": "Ask for \"help\"",
            "desc": "Ask for help on the simplest parts of Python.",
            "type": "attack",
            "dmg": 10,
            "dmg_exc": {
                "class": "coder",
                "ext_dmg": -5
            },
        },
        "atk_2": {
            "name": "Spam",
            "desc": "Spam the chat, causing people to get annoyed.",
            "type": "attack",
            "dmg": 5,
            "dmg_exc": {
                "class": "staff",
                "ext_dmg": 2
            }
        },
        "ability": {
            "name": "Halt Chat",
            "desc": "Stop the chat because of that cringe shit you just said.",
            "type": "stun",
            "ext_turns": 2
        }
    },

    "TheGenocide": {
        "class": "staff",
        "pfp": "https://cdn.discordapp.com/avatars/685082846993317953/68755d84255de78b8b3dd0b78de40991.webp",
        "catchphrase": "I don't know lemme find it one sec.",
        "atk_1": {
            "name": "Moderate",
            "desc": "Moderate your opponent's every move.",
            "dmg": 5,
            "type": "attack",
            "dmg_exc": {
                "class": "member",
                "ext_dmg": 10
            }
        },
        "atk_2": {
            "name": "Be Active",
            "desc": "Your opponent can't break the rules when you're not asleep.",
            "dmg": 5,
            "type": "attack",
            "dmg_exc": {
                "class": "member",
                "ext_dmg": 5
            }
        },
        "ability": {
            "name": "Sweep",
            "desc": "Sweep and regain some health.",
            "type": "heal",
            "health": 10,
            "health_gain_amt": 1
        }
    },

    "UnsoughtConch": {
        "class": "staff",
        "pfp": "https://cdn.discordapp.com/avatars/579041484796461076/a_5cb028f945b0616951cc59e00031b1f2.webp",
        "catchphrase": "I'm too cool for a catchphrase.",
        "atk_1": {
            "name": "Randomly DM Someone",
            "desc": "Give someone an unexpected DM of random origin.",
            "type": "attack",
            "dmg": 10,
            "dmg_exc": {
                "class": "member",
                "ext_dmg": 3
            }
        },
        "atk_2":{
            "name": "Random Lyrics",
            "desc": "Sing random lyrics from some obscure AJR song.",
            "type": "attack",
            "dmg": 5
        },
        "ability": {
            "name": "Have a Stroke",
            "desc": "Trick your opponent into giving you aid because you're having a stroke.",
            "type": "heal",
            "health": 5,
            "health_gain_amt": 1
        }

    }
}

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

    @commands.group(invoke_without_command=True)
    async def brawl(self, ctx):
        embed=discord.Embed(title="TCA ***BRAWL*** Version 1.0.0", description="TCA Brawl is a turn-based fighting game written in Python and playable via a Discord bot. It includes all of your"
        " favorite TCA members and former TCA members.", color=discord.Color.random())
        embed.add_field(name="How to Play:", value="Grab a friend and take a bot channel. Use the `brawl battle` command to get started! The `battle` command has one alias,"
        " `fight`. You will be prompted to pick a character, then the game will begin! If you want info on a character before playing, use `;info`.", inline=False)
        embed.add_field(name="All Commands:", value="`brawl`, `info`, `help`, `faq`.", inline=False)
        embed.add_field(name="Our FAQ", value="You may want to suggest a character, or you don't want your own person in the game. Check the FAQ to see how to deal with stuff.", inline=False)
        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/SydGsxAv1JDLCgm4qALPhcke7fv6TWoyVR2lQhEu-NI/%3Fsize%3D128/https/cdn.discordapp.com/icons/681882711945641997/a_2c2eeae970672cefecdb5b8536f42a47.gif")
        embed.set_image(url="https://media.discordapp.net/attachments/773319739581136916/864310160520249384/tcabrawl.png?width=1025&height=404")
        embed.set_footer(text="TCA Brawl created by UnsoughtConch.")

        faq = discord.Embed(title="Frequently Asked Questions", description="These aren't really frequently asked.", color=discord.Color.random())
        faq.add_field(name="Why am I not a character here?", value="This has a few answers. You either aren't very familiar, we haven't got to you yet, or we can't think of a good moveset for you.")
        faq.add_field(name="I'm in this game and don't want to be. How can I remove myself?", value="If you don't want to be in our game, please contact UnsoughtConch#9225.")
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

    @brawl.command(aliases=['fight'])
    async def battle(self, ctx, user:discord.Member):
        embed = discord.Embed(title=f"Waiting for {user.display_name} to accept...", color=discord.Color.random())
        buttons = ActionRow(
            Button(style=ButtonStyle.green, label="Accept", emoji="✅"),
            Button(style=ButtonStyle.red, label="Deny", emoji="❌")
        )

        msg = await ctx.send(embed=embed, components=[buttons])

        def check(m):
            return m.author == user

        try:
            inter = await msg.wait_for_button_click(check=check, timeout=30)
        except:
            await ctx.send(embed=f"{user.display_name} failed to respond in time!", color=discord.Color.red())

        await inter.reply(type=6)

        embed = discord.Embed(title=f"{ctx.author.display_name}, choose your user!", color=discord.Color.random())

        char_menu_opts = []

        for character in data:
            char = data[character]
            desc = f"Class: {char['class']}\nAttack One: {char['atk_1']['name']}\nAttack Two: {char['atk_2']['name']}\nAbility: {char['ability']['name']}"
            embed.add_field(name=character, value=desc)
            char_menu_opts.append(SelectOption(character, character))

        char_menu = SelectMenu(placeholder="Choose your user!", options=char_menu_opts)

        msg = await ctx.send(embed=embed, components=[char_menu])

        def check(m):
            return m.author == ctx.author

        try:
            inter = await msg.wait_for_dropdown(check=check, timeout=120)
        except:
            await ctx.send(embed=discord.Embed(f"{ctx.author.display_name} failed to respond in time!", color=discord.Color.red()))

        await inter.reply(type=6)

        author_character = [option.label for option in inter.select_menu.selected_options][0]

        embed.title = f"{user.display_name}, choose your user!"

        msg = await ctx.send(embed=embed, components=[char_menu])

        def check(m):
            return m.author == user

        try:
            inter = await msg.wait_for_dropdown(check=check, timeout=120)
        except:
            await ctx.send(embed=discord.Embed(f"{user.display_name} failed to respond in time!", color=discord.Color.red()))

        await inter.reply(type=6)

        user_character = [option.label for option in inter.select_menu.selected_options][0]

        self.battle_hp[ctx.author.id] = 100
        self.battle_hp[user.id] = 100

        # True means author turn, False means user turn

        turne = True

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

            msg = await ctx.send(embed=embed, components=[menu])

            def check(m):
                return m.author == turn

            try:
                inter = await msg.wait_for_dropdown(check=check, timeout=120)
            except:
                await ctx.send(embed=discord.Embed(title=f"{turn.display_name} failed to respond on time, making {enemy.display_name} the winner!", color=discord.Color.red()))
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

                    msg = await ctx.send(embed=discord.Embed(title=f"{turn.display_name}, what option would you like to invoke?"), components=[buttons])

                    def check(m):
                        return m.author == turn
                    try:
                        inter = await msg.wait_for_button_click(check=check, timeout=60)
                    except:
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
                
                elif data[character][move]['type'] == "placebo":
                    self.battle_hp[turn.id] = self.battle_hp[turn.id] + data[character][move]['temp_xp']
                    self.placebo[turn.id] = data[character][move]['turns']

                    phrase = f"{turn.display_name} invokes a placebo with {data[character][move]['name']} that gives them {data[character][move]['temp_xp']} more HP for {data[character][move]['turns']} turns!"
                    
                await ctx.send(phrase)

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

                await ctx.send(f"{character} deals {dmg} damage to {enemy_character} with {data[character][move]['name']}")

                if turne is True:
                    self.battle_hp[user.id] = self.battle_hp[user.id] - dmg
                else:
                    self.battle_hp[ctx.author.id] = self.battle_hp[ctx.author.id] - dmg

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

        if self.battle_hp[ctx.author.id] < 1:
            embed = discord.Embed(title=user_character + ": " + data[user_character]['catchphrase'] if user_character != 'BobDotCom' else random.choice(data[user_character]['catchphrase']), 
            description=f"{user_character} won!")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=author_character + ": " + data[author_character]['catchphrase'] if author_character != 'BobDotCom' else random.choice(data[author_character]['catchphrase']), 
            description=f"{author_character} won!")
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Brawl(client))
