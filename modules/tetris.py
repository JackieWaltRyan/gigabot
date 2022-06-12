import sys
from asyncio import sleep
from os import execl
from random import choice, randint
from traceback import format_exc

from discord import Embed, Member
from discord.ext.commands import Cog, command
from discord_components import Button, ButtonStyle
from pymongo import DESCENDING

from bot import DB, SET


class Tetris(Cog):
    def __init__(self, bot):
        self.BOT = bot
        self.posts = {}
        self.styles = {}
        self.poss = {}
        self.members = {}

    def cog_unload(self):
        pass

    async def messages(self, name, value):
        try:
            for uid in [x for x in SET["Уведомления"].values()]:
                try:
                    await self.BOT.get_user(uid).send(embed=Embed(
                        title="Сообщение!", color=0x008000).add_field(name=name, value=value))
                except Exception:
                    pass
            await self.BOT.get_channel(975477956673675354).send(embed=Embed(
                title="Сообщение!", color=0x008000).add_field(name=name, value=value))
        except Exception:
            print(format_exc())

    async def alerts(self, name, value):
        try:
            for uid in [x for x in SET["Уведомления"].values()]:
                try:
                    await self.BOT.get_user(uid).send(embed=Embed(
                        title="Уведомление!", color=0xFFA500).add_field(name=name, value=value))
                except Exception:
                    pass
            await self.BOT.get_channel(975477956673675354).send(embed=Embed(
                title="Уведомление!", color=0xFFA500).add_field(name=name, value=value))
        except Exception:
            print(format_exc())

    async def errors(self, name, value, reset=0):
        try:
            for uid in [x for x in SET["Уведомления"].values()]:
                try:
                    await self.BOT.get_user(uid).send(embed=Embed(
                        title="Ошибка!", color=0xFF0000).add_field(name=name, value=value))
                except Exception:
                    pass
            await self.BOT.get_channel(975477956673675354).send(embed=Embed(
                title="Ошибка!", color=0xFF0000).add_field(name=name, value=value))
            if reset == 1:
                execl(sys.executable, "python", "bot.py", *sys.argv[1:])
        except Exception:
            print(format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if interaction.component.id == "left" or interaction.component.id == "right":
                postid = self.posts[interaction.message.id]
                pos = self.poss[postid]
                member = self.members[postid]
                style = self.styles[postid]
                if pos is not None:
                    if interaction.component.id == "left":
                        if member is None:
                            member = interaction.user
                        if interaction.user == member:
                            if pos[1] > 0:
                                if style[pos[0] + 1][pos[1] - 1] == ButtonStyle.gray:
                                    style[pos[0]][pos[1]] = ButtonStyle.gray
                                    pos[1] = pos[1] - 1
                            self.styles.update([(postid, style)])
                            self.members.update([(postid, member)])
                            self.poss.update([(postid, pos)])
                            try:
                                await interaction.respond()
                            except Exception:
                                pass
                    if interaction.component.id == "right":
                        if member is None:
                            member = interaction.user
                        if interaction.user == member:
                            if pos[1] < 4:
                                if style[pos[0] + 1][pos[1] + 1] == ButtonStyle.gray:
                                    style[pos[0]][pos[1]] = ButtonStyle.gray
                                    pos[1] = pos[1] + 1
                            self.styles.update([(postid, style)])
                            self.members.update([(postid, member)])
                            self.poss.update([(postid, pos)])
                            try:
                                await interaction.respond()
                            except Exception:
                                pass
                else:
                    try:
                        await interaction.respond()
                    except Exception:
                        pass
        except Exception:
            await self.errors(f"Кнопка {interaction.component.id}:", format_exc())

    @command(description="4", name="tet", help="Сыграть в Тетрис", brief="Ничего / `Упоминание пользователя`",
             usage="!tet <@918687493577121884>")
    async def tet(self, ctx, member: Member = None):
        try:
            await ctx.message.delete(delay=1)
            if member is not None:
                user, e = DB.server.users.find_one({"_id": member.id}), None
                e = Embed(title="Статистика игры \"Тетрис\":", color=ctx.author.color,
                          description=f"**Пользователь {member.mention}:**\n"
                                      f"Сыграно игр: **{user['Сыграно игр в Тетрис']}**\n"
                                      f"Лучший счет: **{user['Лучший счет в Тетрис']}**")
                users, top, i = DB.server.users.find().sort("Лучший счет в Тетрис", DESCENDING), "", 1
                for user in users:
                    if i <= 10:
                        top += f"<@{user['_id']}>: {user['Лучший счет в Тетрис']}\n"
                    i += 1
                e.add_field(name="Таблица лидеров:", value=top)
                e.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
                await ctx.send(embed=e, delete_after=60)
                await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name} {member}\n"
                                              f"Канал: {ctx.message.channel}")
            else:
                style = [[ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                         [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                         [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                         [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                         [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray]]
                disabled = [[False, False, False, False, False],
                            [False, False, False, False, False],
                            [False, False, False, False, False],
                            [False, False, False, False, False],
                            [False, False, False, False, False]]
                pos = None
                member = None
                score = 0
                time = 1

                def but(st, ds):
                    buttons = [[Button(label="\u200b", style=int(st[0][0]), disabled=ds[0][0]),
                                Button(label="\u200b", style=int(st[0][1]), disabled=ds[0][1]),
                                Button(label="\u200b", style=int(st[0][2]), disabled=ds[0][2]),
                                Button(label="\u200b", style=int(st[0][3]), disabled=ds[0][3]),
                                Button(label="\u200b", style=int(st[0][4]), disabled=ds[0][4])],
                               [Button(label="\u200b", style=int(st[1][0]), disabled=ds[1][0]),
                                Button(label="\u200b", style=int(st[1][1]), disabled=ds[1][1]),
                                Button(label="\u200b", style=int(st[1][2]), disabled=ds[1][2]),
                                Button(label="\u200b", style=int(st[1][3]), disabled=ds[1][3]),
                                Button(label="\u200b", style=int(st[1][4]), disabled=ds[1][4])],
                               [Button(label="\u200b", style=int(st[2][0]), disabled=ds[2][0]),
                                Button(label="\u200b", style=int(st[2][1]), disabled=ds[2][1]),
                                Button(label="\u200b", style=int(st[2][2]), disabled=ds[2][2]),
                                Button(label="\u200b", style=int(st[2][3]), disabled=ds[2][3]),
                                Button(label="\u200b", style=int(st[2][4]), disabled=ds[2][4])],
                               [Button(label="\u200b", style=int(st[3][0]), disabled=ds[3][0]),
                                Button(label="\u200b", style=int(st[3][1]), disabled=ds[3][1]),
                                Button(label="\u200b", style=int(st[3][2]), disabled=ds[3][2]),
                                Button(label="\u200b", style=int(st[3][3]), disabled=ds[3][3]),
                                Button(label="\u200b", style=int(st[3][4]), disabled=ds[3][4])],
                               [Button(label="\u200b", style=int(st[4][0]), disabled=ds[4][0]),
                                Button(label="\u200b", style=int(st[4][1]), disabled=ds[4][1]),
                                Button(label="\u200b", style=int(st[4][2]), disabled=ds[4][2]),
                                Button(label="\u200b", style=int(st[4][3]), disabled=ds[4][3]),
                                Button(label="\u200b", style=int(st[4][4]), disabled=ds[4][4])]]
                    return buttons

                e = Embed(title="Тетрис:", color=ctx.author.color)
                post = await ctx.send(embed=e, components=but(style, disabled))
                control = await ctx.send(components=[[Button(emoji="⬅️", id="left"), Button(emoji="➡️", id="right")]])
                self.posts.update([(control.id, post.id)])
                self.styles.update([(post.id, style)])
                self.members.update([(post.id, member)])
                self.poss.update([(post.id, pos)])
                await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name}\nКанал: {ctx.message.channel}")
                try:
                    while True:
                        style = self.styles[post.id]
                        pos = self.poss[post.id]
                        member = self.members[post.id]
                        if style[4].count(ButtonStyle.gray) == 0:
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
                            score += 10
                            time -= 0.1
                        if member is not None:
                            e = Embed(title="Тетрис:", color=ctx.author.color,
                                      description=f"Сейчас играет: {member.mention}\nCчет: **{score}**")
                        for x in range(5):
                            column = 5
                            for line in style:
                                if line[x] != ButtonStyle.gray:
                                    column -= 1
                            if column == 0:
                                if member is not None:
                                    e = Embed(title="Тетрис:", color=ctx.author.color,
                                              description=f"Играл: {member.mention}\nФинальный счет: **{score}**")
                                else:
                                    e = Embed(title="Тетрис:", color=ctx.author.color,
                                              description=f"Играл: {self.BOT.user.mention}\n"
                                                          f"Финальный счет: **{score}**")
                                    member = self.BOT.user
                                await control.delete()
                                DB.server.users.update_one({"_id": member.id}, {"$inc": {"Сыграно игр в Тетрис": 1}})
                                user = DB.server.users.find_one({"_id": member.id})
                                if score > user["Лучший счет в Тетрис"]:
                                    DB.server.users.update_one({"_id": member.id},
                                                               {"$set": {"Лучший счет в Тетрис": score}})
                                for xx in range(5):
                                    for xxx in range(5):
                                        disabled[xx][xxx] = True
                        if pos is None:
                            button, color = randint(0, 4), choice(
                                [ButtonStyle.green, ButtonStyle.red, ButtonStyle.blue])
                            if style[0][button] == ButtonStyle.gray:
                                style[0][button] = color
                                pos = [0, button, color]
                        else:
                            if style[pos[0] + 1][pos[1]] == ButtonStyle.gray:
                                style[pos[0] + 1][pos[1]] = pos[2]
                                style[pos[0]][pos[1]] = ButtonStyle.gray
                                pos[0] = pos[0] + 1
                                if pos[0] == 4:
                                    pos = None
                            else:
                                pos = None
                        await post.edit(embed=e, components=but(style, disabled))
                        self.styles.update([(post.id, style)])
                        self.members.update([(post.id, member)])
                        self.poss.update([(post.id, pos)])
                        await sleep(time)
                except Exception:
                    pass
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())


def setup(bot):
    bot.add_cog(Tetris(bot))
