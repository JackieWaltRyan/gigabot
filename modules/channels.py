from asyncio import run
from datetime import datetime, timedelta
from discord import Embed, PermissionOverwrite
from discord.ext.commands import command, has_permissions, Cog
from discord.ext.tasks import loop
from discord.utils import get
from gigabot import logs, LEVELS, FOOTER, save
from re import findall
from traceback import format_exc


class Channels(Cog):
    def __init__(self, bot):
        try:
            self.BOT = bot
            self.channels.start()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    def cog_unload(self):
        try:
            self.channels.cancel()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    @loop(hours=1)
    async def channels(self):
        try:
            from db.channels import channels
            for channel_id in channels:
                if channels[channel_id]["Отслеживание"]:
                    delta = None
                    if "Время последнего сообщения" in channels[channel_id]:
                        delta = datetime.utcnow() - channels[channel_id]["Время последнего сообщения"]
                    if "Время последнего подключения" in channels[channel_id]:
                        delta = datetime.utcnow() - channels[channel_id]["Время последнего подключения"]
                    timer = timedelta(hours=channels[channel_id]["Таймер"]) - delta
                    if "-1" in str(timer):
                        try:
                            channel = await self.BOT.get_channel(id=channel_id)
                            await channel.delete()
                        except Exception:
                            await logs(level=LEVELS[1], message=format_exc())
                        channels[channel_id]["Отслеживание"] = False
                        await save(file="channels", content=channels)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_message(self, message):
        try:
            from db.channels import channels
            if "Отслеживание" in channels[message.channel.id]:
                if channels[message.channel.id]["Отслеживание"]:
                    channels[message.channel.id]["Время последнего сообщения"] = message.created_at
                    await save(file="channels", content=channels)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            from db.channels import channels
            try:
                if "Отслеживание" in channels[after.channel.id]:
                    if channels[after.channel.id]["Отслеживание"]:
                        channels[after.channel.id]["Время последнего подключения"] = datetime.utcnow()
                        await save(file="channels", content=channels)
                if "Отслеживание" in channels[before.channel.id]:
                    if channels[before.channel.id]["Отслеживание"]:
                        channels[before.channel.id]["Время последнего подключения"] = datetime.utcnow()
                        await save(file="channels", content=channels)
            except Exception:
                await logs(level=LEVELS[1], message=format_exc())
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    # команды пользователей
    @command(description="Все 2", name="text", help="Создать приватный текстовый канал", brief="Не применимо",
             usage="!text")
    async def command_text(self, ctx):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                overwrites = {ctx.message.guild.default_role: PermissionOverwrite(view_channel=False),
                              ctx.message.guild.get_member(user_id=ctx.author.id):
                                  PermissionOverwrite(add_reactions=True, attach_files=True, create_instant_invite=True,
                                                      embed_links=True, manage_channels=True, manage_messages=True,
                                                      manage_roles=True, manage_webhooks=True, mention_everyone=True,
                                                      read_message_history=True, send_messages=True,
                                                      send_tts_messages=True, use_external_emojis=True,
                                                      use_slash_commands=True, view_channel=True)}
                await ctx.message.guild.create_text_channel(name=f"🦄{ctx.author.name.lower()}", overwrites=overwrites,
                                                            category=get(iterable=ctx.message.guild.categories,
                                                                         id=1007577247894482974))
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @command(description="Все 2", name="voice", help="Создать приватный голосовой канал", brief="Не применимо",
             usage="!voice")
    async def command_voice(self, ctx):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                overwrites = {ctx.message.guild.default_role: PermissionOverwrite(connect=False, view_channel=False),
                              ctx.message.guild.get_member(user_id=ctx.author.id):
                                  PermissionOverwrite(connect=True, create_instant_invite=True, deafen_members=True,
                                                      manage_channels=True, manage_roles=True, move_members=True,
                                                      mute_members=True, priority_speaker=True, speak=True, stream=True,
                                                      use_voice_activation=True, view_channel=True)}
                await ctx.message.guild.create_voice_channel(name=f"🦄{ctx.author.name.lower()}", overwrites=overwrites,
                                                             category=get(iterable=ctx.message.guild.categories,
                                                                          id=1007577247894482974))
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    # команды модераторов
    @command(description="Модераторы 1", name="channels", help="Управление удалением каналов",
             brief="Ничего / `Параметр` `Упоминание канала или ID` `Время в часах`",
             usage="!channel add <#974755169311002636> 24")
    @has_permissions(manage_channels=True)
    async def command_channels(self, ctx, trigger: str = None, name: str = None, time: int = 24):
        try:
            if str(ctx.channel.type) == "text":
                await ctx.message.delete(delay=1)
                embed, i, ii, iii = None, 0, 0, 1
                from db.channels import channels
                if trigger is None and name is None and time == 24:
                    embeds = [[Embed(title="Список отслеживаемых каналов:", color=ctx.author.color)]]
                    embeds[i].add_field(name="Команды управления:", inline=False,
                                        value="Добавить канал: **!channels add `упоминание канала или ID` `время в "
                                              "часах`**\n"
                                              "Удалить канал: **!channels del `упоминание канала или ID` `время в "
                                              "часах`**\n"
                                              "Изменить время: **!channels time `упоминание канала или ID` `время в "
                                              "часах`**")
                    for channel in channels:
                        if "Отслеживание" in channels[channel]:
                            if channels[channel]["Отслеживание"]:
                                if ii < 25:
                                    delta = None
                                    if "Время последнего сообщения" in channels[channel]:
                                        delta = datetime.utcnow() - channels[channel]["Время последнего сообщения"]
                                    if "Время последнего подключения" in channels[channel]:
                                        delta = datetime.utcnow() - channels[channel]["Время последнего подключения"]
                                    timer = timedelta(hours=channels[channel]["Таймер"]) - delta
                                    string = str(timer).split(sep=".")[0].replace("days", "дней").replace("day", "день")
                                    embeds[i].add_field(name=f"Канал {iii}:", inline=False,
                                                        value=f"ID: {channel}\n"
                                                              f"Название: <#{channel}>\n"
                                                              f"Таймер: {channels[channel]['Таймер']} часа\n"
                                                              f"Текущее время до удаления: {string}")
                                    ii += 1
                                    iii += 1
                                else:
                                    embeds.append([Embed(title="Список отслеживаемых каналов:",
                                                         color=ctx.author.color)])
                                    i += 1
                                    ii = 0
                    if iii == 1:
                        embeds[i].add_field(name="Ошибка:", value="Сейчас нет отслеживаемых каналов!", inline=False)
                if trigger is not None:
                    channel_id = int(findall(r"(\d+)", name)[0])
                    if trigger == "add":
                        if name is not None:
                            channel = await self.BOT.get_channel(id=channel_id)
                            if str(channel.type) == "text":
                                channels[channel_id].update({"Отслеживание": True,
                                                             "Время последнего сообщения": datetime.utcnow(),
                                                             "Таймер": int(time)})
                            elif str(channel.type) == "voice":
                                channels[channel_id].update({"Отслеживание": True,
                                                             "Время последнего подключения": datetime.utcnow(),
                                                             "Таймер": int(time)})
                            else:
                                raise Exception("The channel type is not supported.")
                            await save(file="channels", content=channels)
                            embed = Embed(title="Добавление канала:", color=ctx.author.color)
                            embed.add_field(name="Успешно:",
                                            value=f"Если в канале <#{channel_id}> не будет актива {time} часа, канал "
                                                  f"будет удален!")
                    if trigger == "del":
                        if name is not None:
                            channels[channel_id]["Отслеживание"] = False
                            await save(file="channels", content=channels)
                            embed = Embed(title="Удаление канала:", color=ctx.author.color)
                            embed.add_field(name="Успешно:",
                                            value=f"Канал <#{channel_id}> удален из списка проверяемых каналов!")
                    if trigger == "time":
                        if name is not None:
                            channels[channel_id]["Таймер"] = int(time)
                            await save(file="channels", content=channels)
                            embed = Embed(title="Обновление времени:", color=ctx.author.color)
                            embed.add_field(name="Успешно:",
                                            value=f"Для канала <#{channel_id}> установлено значение {time} часа!")
                embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                await ctx.send(embed=embed, delete_after=60)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Channels(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
