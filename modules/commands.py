from asyncio import sleep, run
from datetime import timedelta
from discord import Embed, Member
from discord.ext.commands import command, has_permissions, Cog
from discord_components_mirror import Button, ButtonStyle
from gigabot import logs, LEVELS, FOOTER
from random import randint, choice
from traceback import format_exc


class Commands(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    # команды пользователей
    @command(description="Все 1", name="ava", help="Прислать аватарку пользователя",
             brief="Ничего / `Упоминание пользователя`", usage="!ava <@918687493577121884>")
    async def command_ava(self, ctx, member: Member = None):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                if not member:
                    member = ctx.message.author
                await ctx.send(content=member.avatar_url)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @command(description="Все 1", name="info", help="Показать информацию о пользователе",
             brief="Ничего / `Упоминание пользователя`", usage="!info <@918687493577121884>")
    async def command_info(self, ctx, member: Member = None):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                if not member:
                    member = ctx.message.author
                embed = Embed(title="Информация о пользователе:", color=ctx.author.color)
                embed.add_field(name="Имя на сервере:", inline=False, value=member.mention)
                from db.members import members
                join = members[member.id]["Дата добавления на сервер"] + timedelta(hours=3)
                embed.add_field(name="Дата добавления на сервер:", inline=False,
                                value=join.strftime("%d.%m.%Y %H:%M:%S"))
                embed.add_field(name="Роли на сервере:", inline=False,
                                value=" ".join([role.mention for role in list(reversed(member.roles[1:]))]))
                status = {True: "Активный", False: "Неактиыный"}
                embed.add_field(name="Статус на сервере:", inline=False, value=status[members[member.id]["Статус"]])
                embed.add_field(name="Дней на сервере:", inline=False, value=str(members[member.id]["Дни"]))
                last = members[member.id]["Время последнего сообщения"] + timedelta(hours=3)
                embed.add_field(name="Время последнего сообщения:", inline=False,
                                value=last.strftime("%d.%m.%Y %H:%M:%S"))
                embed.add_field(name="Время в голосовых каналах:", inline=False,
                                value=str(timedelta(seconds=members[member.id]["Время в голосовых каналах"])))
                if "achievements" in [cog.lower() for cog in self.BOT.cogs]:
                    embed.add_field(name="Сообщений на сервере:", inline=False,
                                    value=str(members[member.id]["Сообщения"]))
                    embed.add_field(name="Упоминаний на сервере:", inline=False,
                                    value=str(members[member.id]["Упоминания"]))
                    embed.add_field(name="Лайков на сервере:", inline=False, value=str(members[member.id]["Лайки"]))
                    embed.add_field(name="Дизлайков на сервере:", inline=False,
                                    value=str(members[member.id]["Дизлайки"]))
                    embed.add_field(name="Достижений на сервере:", inline=False,
                                    value=str(len(members[member.id]["Достижения"])))
                if "tictactoe" in [cog.lower() for cog in self.BOT.cogs]:
                    embed.add_field(name="Сыграно игр в Крестики-нолики:", inline=False,
                                    value=str(members[member.id]["Крестики-нолики"]["Сыграно"]))
                    embed.add_field(name="Побед в Крестики-нолики:", inline=False,
                                    value=str(members[member.id]["Крестики-нолики"]["Побед"]))
                    embed.add_field(name="Поражений в Крестики-нолики:", inline=False,
                                    value=str(members[member.id]["Крестики-нолики"]["Поражений"]))
                    embed.add_field(name="Процент побед в Крестики-нолики:", inline=False,
                                    value=str(members[member.id]["Крестики-нолики"]["Процент"]))
                if "tetris" in [cog.lower() for cog in self.BOT.cogs]:
                    embed.add_field(name="Сыграно игр в Тетрис:", inline=False,
                                    value=str(members[member.id]["Тетрис"]["Сыграно"]))
                    embed.add_field(name="Лучший счет в Тетрис:", inline=False,
                                    value=str(members[member.id]["Тетрис"]["Лучший счет"]))
                embed.add_field(name="Имя аккаунта:", inline=False, value=f"{member.name}#{member.discriminator}")
                embed.add_field(name="ID аккаунта:", inline=False, value=member.id)
                embed.add_field(name="Дата регистрации:", inline=False,
                                value=(member.created_at + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M:%S"))
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                await ctx.send(embed=embed)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @command(description="Все 3", name="sea", help="Анимация падающие капли", brief="Не применимо", usage="!sea")
    async def command_sea(self, ctx):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                style = [[ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                         [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                         [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                         [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray],
                         [ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray, ButtonStyle.gray]]

                def button(st):
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

                post = await ctx.send(components=button(st=style))
                try:
                    while True:
                        try:
                            await self.BOT.get_channel(id=post.channel.id).fetch_message(id=post.id)
                        except Exception:
                            break
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
                        await post.edit(components=button(st=style))
                        await sleep(delay=1)
                except Exception:
                    await logs(level=LEVELS[1], message=format_exc())
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    # команды модераторов
    @command(description="Модераторы 1", name="del", help="Удалить указанное количество сообщений",
             brief="`Количество сообщений` / `Упоминание пользователя`", usage="!del 10 <@918687493577121884>")
    @has_permissions(manage_messages=True)
    async def command_del(self, ctx, amount: int = 0, member: Member = None):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                if not member:
                    await ctx.channel.purge(limit=amount)
                else:
                    messages = []
                    async for message in ctx.channel.history():
                        if len(messages) == amount:
                            break
                        if message.author == member:
                            messages.append(message)
                    await ctx.channel.delete_messages(messages=messages)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Commands(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
