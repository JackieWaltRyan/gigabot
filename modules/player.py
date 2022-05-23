import sys
from asyncio import sleep
from datetime import timedelta
from os import execl
from traceback import format_exc

from discord import Embed, FFmpegPCMAudio
from discord.ext import commands
from discord.ext.tasks import loop
from discord_components import Button, ButtonStyle
from youtube_dl import YoutubeDL

from bot import DB, SET


class Player(commands.Cog):
    def __init__(self, bot):
        self.BOT = bot
        self.vc = None
        self.entries = None
        self.ctx = None
        self.arg = None
        self.player.start()
        self.playlist.start()

    def cog_unload(self):
        self.player.cancel()
        self.playlist.cancel()

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

    @loop()
    async def playlist(self):
        try:
            if self.entries is not None:
                entries, ctx, arg = None, None, None
                entries, ctx, arg = self.entries, self.ctx, self.arg
                self.entries, self.ctx, self.arg = None, None, None
                for video in entries:
                    download = YoutubeDL({"format": "bestaudio",
                                          "noplaylist": "False",
                                          "default_search": "auto",
                                          "extract_flat": "in_playlist"}).extract_info(video["id"], download=False)
                    queue, i = [], 1
                    for item in DB.server.queue.find():
                        queue.append(item["_id"])
                    if len(queue) != 0:
                        i = int(queue[-1]) + 1
                    post = {"_id": i, "channel": download["channel"], "title": download["title"],
                            "webpage_url": download["webpage_url"], "thumbnail": download["thumbnail"],
                            "url": download["url"], "duration": download["duration"]}
                    DB.server.queue.insert_one(post)
                    if len(entries) == 1:
                        e2 = Embed(title="Плеер:", color=0x008000,
                                   description=f"Следующий трек успешно добавлен в очередь!\n\n"
                                               f"Используйте команду **!play** чтобы добавить новые...\n"
                                               f"Или команду **!skip** чтобы удалить...")
                        e2.add_field(name=f"{i}. {download['webpage_url']}", inline=False,
                                     value=f"Испольнитель: {download['channel']}\n"
                                           f"Название: {download['title']}\n"
                                           f"Длительность: {timedelta(seconds=download['duration'])}")
                        e2.set_thumbnail(url=download["thumbnail"])
                        e2.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
                        await ctx.send(embed=e2)
                        await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name} {arg}\n"
                                                      f"Канал: {ctx.message.channel}")
                else:
                    if len(entries) != 1:
                        e1 = Embed(title="Плеер:", color=0x008000,
                                   description=f"{len(entries)} треков успешно добавлены в очередь!\n\n"
                                               f"Используйте команду **!play** чтобы добавить новые...\n"
                                               f"Или команду **!skip** чтобы удалить...")
                        e1.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
                        await ctx.send(embed=e1)
                        await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name} {arg}\n"
                                                      f"Канал: {ctx.message.channel}")
            else:
                self.playlist.cancel()
        except Exception:
            await self.errors("Загрузка плейлиста:", format_exc())

    @loop()
    async def player(self):
        try:
            i = 1
            while True:
                if int(DB.server.queue.count_documents({})) != 0:
                    if DB.server.queue.find_one({"_id": int(i)}):
                        self.vc = None
                        m = DB.server.queue.find_one({"_id": i})
                        try:
                            for x in self.BOT.voice_clients:
                                await x.disconnect()
                        except Exception:
                            pass
                        try:
                            self.vc = await self.BOT.get_channel(975486290571178045).connect()
                            self.vc.play(FFmpegPCMAudio(f"{m['url']}"))
                        except Exception:
                            pass
                        d = str(timedelta(seconds=m["duration"]))
                        try:
                            post = await self.BOT.get_channel(974755208108310639).fetch_message(
                                int(DB.server.channels.find_one({"_id": 974755208108310639})["Плеер"]))
                            await post.delete()
                        except Exception:
                            pass
                        e1 = Embed(title="Сейчас играет:", color=0x00FFFF)
                        e1.set_thumbnail(url=m["thumbnail"])
                        e1.add_field(name=m["title"], inline=False, value=f"Исполнитель: {m['channel']}\n"
                                                                          f"Длительность: {d}\n"
                                                                          f"Ссылка: {m['webpage_url']}")
                        e1.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
                        mes = await self.BOT.get_channel(974755208108310639).send(embed=e1, components=[[
                            Button(emoji="▶️", style=ButtonStyle.blue, id="play"),
                            Button(emoji="⏸️", style=ButtonStyle.blue, id="pause"),
                            Button(emoji="⏭️", style=ButtonStyle.blue, id="next"),
                            Button(label="Очередь", style=ButtonStyle.green)]])
                        DB.server.channels.update_one({"_id": 974755208108310639}, {"$set": {"Плеер": int(mes.id)}})
                        DB.server.queue.delete_one({"_id": i})
                        await sleep(int(m["duration"]))
                    a = []
                    c = 1
                    for b in DB.server.queue.find():
                        a.append(b["_id"])
                    if len(a) != 0:
                        c = int(a[-1])
                    if i > c:
                        i = 0
                    i += 1
                else:
                    try:
                        for x in self.BOT.voice_clients:
                            await x.disconnect()
                        post = await self.BOT.get_channel(974755208108310639).fetch_message(
                            int(DB.server.channels.find_one({"_id": 974755208108310639})["Плеер"]))
                        await post.delete()
                    except Exception:
                        pass
                    await sleep(3)
        except Exception:
            await self.errors("Плеер:", format_exc())

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if interaction.component.id == "play":
                try:
                    self.vc.resume()
                    await interaction.respond()
                except Exception:
                    pass
        except Exception:
            await self.errors(f"Кнопка {interaction.component.id}:", format_exc())
        try:
            if interaction.component.id == "pause":
                try:
                    self.vc.pause()
                    await interaction.respond()
                except Exception:
                    pass
        except Exception:
            await self.errors(f"Кнопка {interaction.component.id}:", format_exc())
        try:
            if interaction.component.id == "next":
                try:
                    self.player.restart()
                    await interaction.respond()
                except Exception:
                    pass
        except Exception:
            await self.errors(f"Кнопка {interaction.component.id}:", format_exc())
        try:
            if interaction.component.label == "Очередь":
                count, e4, i = int(DB.server.queue.count_documents({})), None, 1
                if count != 0:
                    e4 = Embed(title="Очередь:", color=0x008000,
                               description=f"Сейчас в очереди {count} треков!\n\n"
                                           f"Используйте команду **!play** чтобы добавить новые...\n"
                                           f"Или команду **!skip** чтобы удалить...")
                    for item in DB.server.queue.find():
                        if i <= 24:
                            e4.add_field(name=f"{item['_id']}. {item['title']}", inline=False,
                                         value=f"Исполнитель: {item['channel']}\n"
                                               f"Длительность: {timedelta(seconds=item['duration'])}\n"
                                               f"Ссылка: {item['webpage_url']}")
                        if i == 25:
                            e4.add_field(name="Ошибка!", inline=False,
                                         value="Количество треков превышает допустимый лимит!")
                        i += 1
                else:
                    e4 = Embed(title="Очередь:", color=0x008000,
                               description="Сейчас в очереди нет треков!\n\n"
                                           "Используйте команду **!play** чтобы добавить новые...")
                e4.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
                await interaction.send(embed=e4, components=[[Button(label="Очистить очередь", style=ButtonStyle.red)]])
        except Exception:
            await self.errors(f"Кнопка {interaction.component.label}:", format_exc())
        try:
            if interaction.component.label == "Очистить очередь":
                await interaction.send("Вы действительно хотите полностью очистить очередь?",
                                       components=[Button(label="Да", style=ButtonStyle.red)])
        except Exception:
            await self.errors(f"Кнопка {interaction.component.label}:", format_exc())
        try:
            if interaction.component.label == "Да":
                for x in DB.server.queue.find():
                    DB.server.queue.delete_one(x)
                await interaction.send("Очередь успешно очищена!")
                await self.alerts(interaction.user, "Очистил всю очередь!")
        except Exception:
            await self.errors(f"Кнопка {interaction.component.label}:", format_exc())

    @commands.command(description="3", name="play", help="Добавить трек в очередь плеера",
                      brief="`Ссылка на видео или плейлист` / `Поисковый запрос`",
                      usage="!play https://youtu.be/asNy7WJHqdM")
    async def play(self, ctx, *, arg):
        try:
            if ctx.channel.id == 974755208108310639:
                await ctx.message.delete(delay=1)
                download = YoutubeDL({"format": "bestaudio",
                                      "noplaylist": "False",
                                      "default_search": "auto",
                                      "extract_flat": "in_playlist"}).extract_info(arg, download=False)
                if "entries" in download:
                    self.entries, self.ctx, self.arg = download["entries"], ctx, arg
                    self.playlist.start()
                else:
                    queue, i = [], 1
                    for b in DB.server.queue.find():
                        queue.append(b["_id"])
                    if len(queue) != 0:
                        i = int(queue[-1]) + 1
                    post = {"_id": i, "channel": download["channel"], "title": download["title"],
                            "webpage_url": download["webpage_url"], "thumbnail": download["thumbnail"],
                            "url": download["url"], "duration": download["duration"]}
                    DB.server.queue.insert_one(post)
                    e = Embed(title="Плеер:", color=0x008000,
                              description=f"Следующий трек успешно добавлен в очередь!\n\n"
                                          f"Используйте команду **!play** чтобы добавить новые...\n"
                                          f"Или команду **!skip** чтобы удалить...")
                    e.add_field(name=f"{i}. {download['webpage_url']}", inline=False,
                                value=f"Испольнитель: {download['channel']}\n"
                                      f"Название: {download['title']}\n"
                                      f"Длительность: {timedelta(seconds=download['duration'])}")
                    e.set_thumbnail(url=download["thumbnail"])
                    e.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
                    await ctx.send(embed=e)
                await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name} {arg}\n"
                                              f"Канал: {ctx.message.channel}")
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())

    @commands.command(description="3", name="skip", help="Удалить трек из очереди плеера",
                      brief="`Номер трека в очереди`", usage="!skip 1")
    async def skip(self, ctx, pos: int):
        try:
            if ctx.channel.id == 974755208108310639:
                await ctx.message.delete(delay=1)
                item = DB.server.queue.find_one({"_id": pos})
                if item is not None:
                    DB.server.queue.delete_one({"_id": pos})
                    e = Embed(title="Очередь:", color=0xFF0000,
                              description="Следующий трек успешно удален из очереди!\n\n"
                                          "Используйте команду **!play** чтобы добавить новые...\n"
                                          "Или команду **!skip** чтобы удалить еще...")
                    e.add_field(name=f"{item['_id']}. {item['title']}", inline=False,
                                value=f"Исполнитель: {item['channel']}\n"
                                      f"Длительность: {timedelta(seconds=item['duration'])}\n"
                                      f"Ссылка: {item['webpage_url']}")
                    e.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
                    await ctx.send(embed=e, delete_after=60)
                    await self.alerts(ctx.author, f"Использовал команду: {ctx.command.name} {pos}\n"
                                                  f"Канал: {ctx.message.channel}")
        except Exception:
            await self.errors(f"Команда {ctx.command.name}:", format_exc())


def setup(bot):
    bot.add_cog(Player(bot))
