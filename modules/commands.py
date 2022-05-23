import sys
from asyncio import sleep
from os import execl
from random import randint, choice
from traceback import format_exc

from discord import Embed, Member
from discord.ext.commands import command, has_permissions, Cog
from discord_components import Button, ButtonStyle
from pymongo import DESCENDING

from bot import DB, SET


class Commands(Cog):
    def __init__(self, bot):
        self.BOT = bot

    async def messages(self, name, value):
        try:
            for uid in [x for x in SET["Уведомления"].values()]:
                await self.BOT.get_user(uid).send(embed=Embed(
                    title="Сообщение!", color=0x008000).add_field(name=name, value=value))
            await self.BOT.get_channel(975477956673675354).send(embed=Embed(
                title="Сообщение!", color=0x008000).add_field(name=name, value=value))
        except Exception:
            print(format_exc())

    async def alerts(self, name, value):
        try:
            for uid in [x for x in SET["Уведомления"].values()]:
                await self.BOT.get_user(uid).send(embed=Embed(
                    title="Уведомление!", color=0xFFA500).add_field(name=name, value=value))
            await self.BOT.get_channel(975477956673675354).send(embed=Embed(
                title="Уведомление!", color=0xFFA500).add_field(name=name, value=value))
        except Exception:
            print(format_exc())

    async def errors(self, name, value, reset=0):
        try:
            for uid in [x for x in SET["Уведомления"].values()]:
                await self.BOT.get_user(uid).send(embed=Embed(
                    title="Ошибка!", color=0xFF0000).add_field(name=name, value=value))
            await self.BOT.get_channel(975477956673675354).send(embed=Embed(
                title="Ошибка!", color=0xFF0000).add_field(name=name, value=value))
            if reset == 1:
                execl(sys.executable, "python", "bot.py", *sys.argv[1:])
        except Exception:
            print(format_exc())

    # команды пользователей
    @command(description="1", name="ava", help="Прислать аватарку пользователя",
             brief="Ничего / `Упоминание пользователя`", usage="!ava <@918687493577121884>")
    async def ava(self, ctx, member: Member = None):
        try:
            await ctx.message.delete(delay=1)
            if not member:
                member = ctx.message.author
            await ctx.send(member.avatar_url)
            await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name} {member}\n"
                                          f"Канал: {ctx.message.channel}")
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())

    @command(description="1", name="info", help="Показать информацию о пользователе",
             brief="Ничего / `Упоминание пользователя`", usage="!info <@918687493577121884>")
    async def info(self, ctx, member: Member = None):
        try:
            await ctx.message.delete(delay=1)
            if not member:
                member = ctx.message.author
            e = Embed(title="Информация о пользователе:", color=ctx.author.color)
            e.set_thumbnail(url=member.avatar_url)
            e.add_field(name="Имя на сервере:", value=member.mention, inline=False)
            e.add_field(name="Дата добавления на сервер:", value=member.joined_at.strftime("%d.%m.%Y %H:%M:%S"),
                        inline=False)
            e.add_field(name="Роли на сервере:",
                        value=" ".join([role.mention for role in list(reversed(member.roles[1:]))]), inline=False)
            e.add_field(name="Имя аккаунта:", value=f"{member.name}#{member.discriminator}", inline=False)
            e.add_field(name="ID аккаунта:", value=member.id, inline=False)
            e.add_field(name="Дата регистрации:", value=member.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=False)
            e.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
            await ctx.send(embed=e)
            await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name} {member}\n"
                                          f"Канал: {ctx.message.channel}")
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())

    @command(description="4", name="tic", help="Сыграть в Крестики-нолики", brief="Ничего / `Упоминание пользователя`",
             usage="!tic <@918687493577121884>")
    async def tic(self, ctx, member: Member = None):
        try:
            await ctx.message.delete(delay=1)
            if member is not None:
                users = DB.server.users.find()
                for user in users:
                    a = int(user['Побед в Крестики-нолики'] - user['Поражений в Крестики-нолики'])
                    try:
                        b = int((a / user['Сыграно игр в Крестики-нолики']) * 100)
                        DB.server.users.update_one({"_id": user['_id']},
                                                   {"$set": {"Процент побед в Крестики-нолики": b}})
                    except Exception:
                        pass
                user, e = DB.server.users.find_one({"_id": member.id}), None
                e = Embed(title="Статистика игры \"Крестики-нолики\":", color=ctx.author.color,
                          description=f"**Пользователь {member.mention}:**\n"
                                      f"Сыграно игр: **{user['Сыграно игр в Крестики-нолики']}**\n"
                                      f"Побед: **{user['Побед в Крестики-нолики']}**\n"
                                      f"Поражений: **{user['Поражений в Крестики-нолики']}**\n"
                                      f"Коэфициент побед: {user['Процент побед в Крестики-нолики']}%")
                users, top, i = DB.server.users.find().sort("Процент побед в Крестики-нолики", DESCENDING), "", 1
                for user in users:
                    if i <= 10:
                        top += f"<@{user['_id']}>: {user['Процент побед в Крестики-нолики']}%\n"
                    i += 1
                e.add_field(name="Таблица лидеров:", value=top)
                e.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
                await ctx.send(embed=e, delete_after=60)
                await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name} {member}\n"
                                              f"Канал: {ctx.message.channel}")
            else:
                label = [["\u200b", "\u200b", "\u200b"],
                         ["\u200b", "\u200b", "\u200b"],
                         ["\u200b", "\u200b", "\u200b"]]
                style = [[ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                         [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                         [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray]]
                disabled = [[False, False, False],
                            [False, False, False],
                            [False, False, False]]
                tick, gamer1, gamer2 = "Крестики", None, None

                def but(lb, st, ds):
                    buttons = [[Button(label=lb[0][0], style=st[0][0], id="0 0", disabled=ds[0][0]),
                                Button(label=lb[0][1], style=st[0][1], id="0 1", disabled=ds[0][1]),
                                Button(label=lb[0][2], style=st[0][2], id="0 2", disabled=ds[0][2])],
                               [Button(label=lb[1][0], style=st[1][0], id="1 0", disabled=ds[1][0]),
                                Button(label=lb[1][1], style=st[1][1], id="1 1", disabled=ds[1][1]),
                                Button(label=lb[1][2], style=st[1][2], id="1 2", disabled=ds[1][2])],
                               [Button(label=lb[2][0], style=st[2][0], id="2 0", disabled=ds[2][0]),
                                Button(label=lb[2][1], style=st[2][1], id="2 1", disabled=ds[2][1]),
                                Button(label=lb[2][2], style=st[2][2], id="2 2", disabled=ds[2][2])]]
                    return buttons

                e = Embed(title="Крестики-нолики:", color=ctx.author.color, description="Первые ходят **крестики**:")
                post = await ctx.send(embed=e, components=but(label, style, disabled))
                await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name}\nКанал: {ctx.message.channel}")
                try:
                    while True:
                        interaction = await self.BOT.wait_for("button_click")
                        if interaction.message.id == post.id:
                            buttonid = interaction.component.id
                            pos = buttonid.split(" ")
                            if tick == "Крестики":
                                if gamer1 is None:
                                    gamer1 = interaction.user
                                if gamer1 is not None and interaction.user != gamer1:
                                    continue
                                label[int(pos[0])][int(pos[1])] = "X"
                                style[int(pos[0])][int(pos[1])] = ButtonStyle.red
                                disabled[int(pos[0])][int(pos[1])] = True
                                tick = "Нолики"
                            else:
                                if gamer2 is None and interaction.user != gamer1:
                                    gamer2 = interaction.user
                                if gamer2 is None and interaction.user == gamer1:
                                    continue
                                if gamer2 is not None and interaction.user != gamer2:
                                    continue
                                label[int(pos[0])][int(pos[1])] = "O"
                                style[int(pos[0])][int(pos[1])] = ButtonStyle.green
                                disabled[int(pos[0])][int(pos[1])] = True
                                tick = "Крестики"
                            e = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                      description=f"Сейчас ходят **{tick}**:")
                            if gamer1 is not None:
                                e = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                          description=f"За крестиков играет: {gamer1.mention}\n\n"
                                                      f"Сейчас ходят **{tick}**:")
                                if gamer2 is not None:
                                    e = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                              description=f"За крестиков играет: {gamer1.mention}\n"
                                                          f"За ноликов играет: {gamer2.mention}\n\n"
                                                          f"Сейчас ходят **{tick}**:")

                            def winners(win):
                                ee = None
                                if win == "X":
                                    ee = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                               description=f"За крестиков играл: {gamer1.mention}\n"
                                                           f"За ноликов играл: {gamer2.mention}\n\n"
                                                           f"Победили **крестики**!")
                                    DB.server.users.update_one({"_id": int(gamer1.id)},
                                                               {"$inc": {"Сыграно игр в Крестики-нолики": int(1),
                                                                         "Побед в Крестики-нолики": int(1)}})
                                    DB.server.users.update_one({"_id": int(gamer2.id)},
                                                               {"$inc": {"Сыграно игр в Крестики-нолики": int(1),
                                                                         "Поражений в Крестики-нолики": int(1)}})
                                if win == "O":
                                    ee = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                               description=f"За крестиков играл: {gamer1.mention}\n"
                                                           f"За ноликов играл: {gamer2.mention}\n\n"
                                                           f"Победили **нолики**!")
                                    DB.server.users.update_one({"_id": int(gamer1.id)},
                                                               {"$inc": {"Сыграно игр в Крестики-нолики": int(1),
                                                                         "Поражений в Крестики-нолики": int(1)}})
                                    DB.server.users.update_one({"_id": int(gamer2.id)},
                                                               {"$inc": {"Сыграно игр в Крестики-нолики": int(1),
                                                                         "Побед в Крестики-нолики": int(1)}})
                                if win == "XO":
                                    ee = Embed(title="Крестики-нолики:", color=ctx.author.color,
                                               description=f"За крестиков играл: {gamer1.mention}\n"
                                                           f"За ноликов играл: {gamer2.mention}\n\nУ нас **ничья**!")
                                    DB.server.users.update_one({"_id": int(gamer1.id)},
                                                               {"$inc": {"Сыграно игр в Крестики-нолики": int(1)}})
                                    DB.server.users.update_one({"_id": int(gamer2.id)},
                                                               {"$inc": {"Сыграно игр в Крестики-нолики": int(1)}})
                                for x in range(3):
                                    for xx in range(3):
                                        disabled[x][xx] = True
                                return ee

                            count = 0
                            for lbl in label:
                                count += lbl.count("\u200b")
                            if count == 0:
                                e = winners("XO")
                            for line in label:
                                if line.count("X") == 3:
                                    e = winners("X")
                                if line.count("O") == 3:
                                    e = winners("O")
                            for line in range(3):
                                value = label[0][line] + label[1][line] + label[2][line]
                                if value == "XXX":
                                    e = winners("X")
                                if value == "OOO":
                                    e = winners("O")
                            diag1 = label[0][2] + label[1][1] + label[2][0]
                            diag2 = label[0][0] + label[1][1] + label[2][2]
                            if diag1 == "XXX" or diag2 == "XXX":
                                e = winners("X")
                            if diag1 == "OOO" or diag2 == "OOO":
                                e = winners("O")
                            await post.edit(embed=e, components=but(label, style, disabled))
                            if count != 0:
                                try:
                                    await interaction.respond()
                                except Exception:
                                    pass
                            else:
                                await interaction.respond()
                except Exception:
                    pass
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())

    @command(description="4", name="sea", help="Анимация падающие капли", brief="Не применимо", usage="!sea")
    async def sea(self, ctx):
        try:
            await ctx.message.delete(delay=1)
            style = [[ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                     [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                     [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                     [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                     [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray]]

            def but(st):
                buttons = [[Button(label="\u200b", style=st[0][0]),
                            Button(label="\u200b", style=st[0][1]),
                            Button(label="\u200b", style=st[0][2]),
                            Button(label="\u200b", style=st[0][3]),
                            Button(label="\u200b", style=st[0][4])],
                           [Button(label="\u200b", style=st[1][0]),
                            Button(label="\u200b", style=st[1][1]),
                            Button(label="\u200b", style=st[1][2]),
                            Button(label="\u200b", style=st[1][3]),
                            Button(label="\u200b", style=st[1][4])],
                           [Button(label="\u200b", style=st[2][0]),
                            Button(label="\u200b", style=st[2][1]),
                            Button(label="\u200b", style=st[2][2]),
                            Button(label="\u200b", style=st[2][3]),
                            Button(label="\u200b", style=st[2][4])],
                           [Button(label="\u200b", style=st[3][0]),
                            Button(label="\u200b", style=st[3][1]),
                            Button(label="\u200b", style=st[3][2]),
                            Button(label="\u200b", style=st[3][3]),
                            Button(label="\u200b", style=st[3][4])],
                           [Button(label="\u200b", style=st[4][0]),
                            Button(label="\u200b", style=st[4][1]),
                            Button(label="\u200b", style=st[4][2]),
                            Button(label="\u200b", style=st[4][3]),
                            Button(label="\u200b", style=st[4][4])]]
                return buttons

            post = await ctx.send(components=but(style))
            await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name}\nКанал: {ctx.message.channel}")
            try:
                while True:
                    style[4].clear()
                    style[4].extend(style[3])
                    style[3].clear()
                    style[3].extend(style[2])
                    style[2].clear()
                    style[2].extend(style[1])
                    style[1].clear()
                    style[1].extend(style[0])
                    style[0].clear()
                    style[0].extend([ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray,
                                     ButtonStyle.gray])
                    style[0][randint(0, 4)] = choice([ButtonStyle.green, ButtonStyle.red, ButtonStyle.blue])
                    await post.edit(components=but(style))
                    await sleep(1)
            except Exception:
                pass
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())

    # команды модераторов
    @command(description="7", name="del", help="Удалить указанное количество сообщений",
             brief="`Количество сообщений` / `Упоминание пользователя`", usage="!del 10 <@918687493577121884>")
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 0, member: Member = None):
        try:
            await ctx.message.delete(delay=1)
            msg = []
            if not member:
                await ctx.channel.purge(limit=amount)
            else:
                async for m in ctx.channel.history():
                    if len(msg) == amount:
                        break
                    if m.author == member:
                        msg.append(m)
                await ctx.channel.delete_messages(msg)
            await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name} {amount} {member}\n"
                                          f"Канал: {ctx.message.channel}")
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())


def setup(bot):
    bot.add_cog(Commands(bot))
