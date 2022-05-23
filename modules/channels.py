import sys
from datetime import datetime, timedelta
from os import execl
from re import findall
from traceback import format_exc

from discord import Embed, PermissionOverwrite
from discord.ext.commands import command, has_permissions, Cog
from discord.ext.tasks import loop
from discord.utils import get
from pymongo import ASCENDING

from bot import DB, SET


class Channels(Cog):
    def __init__(self, bot):
        self.BOT = bot
        self.checkchannels.start()

    def cog_unload(self):
        self.checkchannels.cancel()

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

    @loop(hours=1)
    async def checkchannels(self):
        try:
            channels = DB.server.channels.find({"Отслеживание": "Да"})
            for channel in channels:
                delta = None
                if "Время последнего сообщения" in channel:
                    delta = datetime.now() - channel["Время последнего сообщения"]
                if "Время последнего подключения" in channel:
                    delta = datetime.now() - channel["Время последнего подключения"]
                timer = timedelta(hours=channel["Таймер"]) - delta
                if "-1" in str(timer):
                    try:
                        await self.BOT.get_channel(int(channel["_id"])).delete()
                    except Exception:
                        pass
                    DB.server.channels.delete_one({"_id": channel["_id"]})
        except Exception:
            await self.errors(f"Проверка каналов:", format_exc())

    @Cog.listener()
    async def on_message(self, message):
        try:
            channels = [item["_id"] for item in DB.server.channels.find({"Отслеживание": "Да"})]
            if message.channel.id in channels:
                DB.server.channels.update_one({"_id": message.channel.id},
                                              {"$set": {"Время последнего сообщения": message.created_at}})
        except Exception:
            await self.errors(f"Обновление текстовых каналов:", format_exc())

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            channels = [item["_id"] for item in DB.server.channels.find({"Отслеживание": "Да"})]
            try:
                if after.channel.id in channels:
                    DB.server.channels.update_one({"_id": after.channel.id},
                                                  {"$set": {"Время последнего подключения": datetime.now()}})
                if before.channel.id in channels:
                    DB.server.channels.update_one({"_id": before.channel.id},
                                                  {"$set": {"Время последнего подключения": datetime.now()}})
            except Exception:
                pass
        except Exception:
            await self.errors(f"Обновление голосовых каналов:", format_exc())

    # команды пользователей
    @command(description="2", name="text", help="Создать приватный текстовый канал", brief="Не применимо",
             usage="!text")
    async def text(self, ctx):
        try:
            await ctx.message.delete(delay=1)
            overwrites = {ctx.message.guild.default_role: PermissionOverwrite(view_channel=False),
                          ctx.message.guild.get_member(ctx.author.id): PermissionOverwrite(add_reactions=True,
                                                                                           attach_files=True,
                                                                                           create_instant_invite=True,
                                                                                           embed_links=True,
                                                                                           manage_channels=True,
                                                                                           manage_messages=True,
                                                                                           manage_roles=True,
                                                                                           manage_webhooks=True,
                                                                                           mention_everyone=True,
                                                                                           read_message_history=True,
                                                                                           send_messages=True,
                                                                                           send_tts_messages=True,
                                                                                           use_external_emojis=True,
                                                                                           use_slash_commands=True,
                                                                                           view_channel=True)}
            channel = await ctx.message.guild.create_text_channel(name=ctx.author.name, overwrites=overwrites,
                                                                  category=get(ctx.message.guild.categories,
                                                                               id=976595862144827462))
            DB.server.channels.insert_one({"_id": int(channel.id), "Название": channel.name, "Отслеживание": "Да",
                                           "Время последнего сообщения": datetime.now(), "Таймер": int(24)})
            await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name}\nКанал: {ctx.message.channel}")
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())

    @command(description="2", name="voice", help="Создать приватный голосовой канал", brief="Не применимо",
             usage="!voice")
    async def voice(self, ctx):
        try:
            await ctx.message.delete(delay=1)
            overwrites = {ctx.message.guild.default_role: PermissionOverwrite(connect=False, view_channel=False),
                          ctx.message.guild.get_member(ctx.author.id): PermissionOverwrite(connect=True,
                                                                                           create_instant_invite=True,
                                                                                           deafen_members=True,
                                                                                           manage_channels=True,
                                                                                           manage_roles=True,
                                                                                           move_members=True,
                                                                                           mute_members=True,
                                                                                           priority_speaker=True,
                                                                                           speak=True,
                                                                                           stream=True,
                                                                                           use_voice_activation=True,
                                                                                           view_channel=True)}
            channel = await ctx.message.guild.create_voice_channel(name=ctx.author.name, overwrites=overwrites,
                                                                   category=get(ctx.message.guild.categories,
                                                                                id=976595862144827462))
            DB.server.channels.insert_one({"_id": int(channel.id), "Название": channel.name, "Отслеживание": "Да",
                                           "Время последнего подключения": datetime.now(), "Таймер": int(24)})
            await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name}\nКанал: {ctx.message.channel}")
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())

    # команды модераторов
    @command(description="7", name="channels", help="Управление удалением каналов",
             brief="Ничего / `Параметр` `Упоминание канала или ID` `Время в часах`",
             usage="!channel add <#974755169311002636> 24")
    @has_permissions(manage_channels=True)
    async def channels(self, ctx, trigger: str = None, name: str = None, time: int = 24):
        try:
            await ctx.message.delete(delay=1)
            e, i = None, 1
            if trigger is None and name is None and time == 24:
                e = Embed(title="Список отслеживаемых каналов:", color=ctx.author.color)
                e.add_field(name="Команды управления:", inline=False,
                            value="Добавить канал: **!channels add `упоминание канала или ID` `время в часах`**\n"
                                  "Удалить канал: **!channels del `упоминание канала или ID` `время в часах`**\n"
                                  "Изменить время: **!channels time `упоминание канала или ID` `время в часах`**")
                if DB.server.channels.count_documents({"Отслеживание": "Да"}) != 0:
                    channels = DB.server.channels.find({"Отслеживание": "Да"}).sort("Название", ASCENDING)
                    for channel in channels:
                        if i <= 24:
                            delta = None
                            if "Время последнего сообщения" in channel:
                                delta = datetime.now() - channel["Время последнего сообщения"]
                            if "Время последнего подключения" in channel:
                                delta = datetime.now() - channel["Время последнего подключения"]
                            timer = timedelta(hours=channel["Таймер"]) - delta
                            string = str(timer).split(".")[0].replace("days", "дней").replace("day", "день")
                            e.add_field(name=f"Канал {i}:", value=f"ID: {channel['_id']}\n"
                                                                  f"Название: <#{channel['_id']}>\n"
                                                                  f"Таймер: {channel['Таймер']} часа\n"
                                                                  f"Текущее время до удаления: {string}", inline=False)
                        if i == 25:
                            e.add_field(name="Ошибка!", value="Количество каналов превышает допустимый лимит!",
                                        inline=False)
                        i += 1
                else:
                    e.add_field(name="Ошибка:", value="Сейчас нет отслеживаемых каналов!", inline=False)
            if trigger is not None:
                for channel in self.BOT.get_all_channels():
                    ch = DB.server.channels.find_one({"_id": channel.id})
                    if ch is None:
                        DB.server.channels.insert_one({"_id": int(channel.id), "Название": channel.name})
                    else:
                        DB.server.channels.update_one({"_id": channel.id}, {"$set": {"Название": channel.name}})
                cid = int(findall(r"(\d+)", name)[0])
                if trigger == "add":
                    if name is not None:
                        DB.server.channels.update_one({"_id": cid},
                                                      {"$set": {"Отслеживание": "Да",
                                                                "Время последнего подключения": datetime.now(),
                                                                "Таймер": int(time)}})
                        e = Embed(title="Добавление канала:", color=ctx.author.color)
                        e.add_field(name="Успешно:", value=f"Если в канале <#{cid}> не будет актива {time}"
                                                           f" часа, канал будет удален!")
                if trigger == "del":
                    if name is not None:
                        DB.server.channels.update_one({"_id": cid}, {"$set": {"Отслеживание": "Нет"}})
                        e = Embed(title="Удаление канала:", color=ctx.author.color)
                        e.add_field(name="Успешно:",
                                    value=f"Канал <#{cid}> удален из списка проверяемых каналов!")
                if trigger == "time":
                    if name is not None:
                        DB.server.channels.update_one({"_id": cid}, {"$set": {"Таймер": int(time)}})
                        e = Embed(title="Обновление времени:", color=ctx.author.color)
                        e.add_field(name="Успешно:",
                                    value=f"Для канала <#{cid}> установлено значение {time} часа!")
            e.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
            await ctx.send(embed=e, delete_after=60)
            await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name} {trigger} {name}\n"
                                          f"Канал: {ctx.message.channel}")
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())


def setup(bot):
    bot.add_cog(Channels(bot))
