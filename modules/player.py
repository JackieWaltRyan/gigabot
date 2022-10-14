from asyncio import sleep, run
from datetime import timedelta
from discord import Embed, FFmpegPCMAudio
from discord.ext.commands import Cog, command
from discord.ext.tasks import loop
from discord_components_mirror import Button, ButtonStyle, Select, SelectOption
from gigabot import logs, LEVELS, FOOTER, save
from re import findall
from threading import Thread
from traceback import format_exc
from youtube_dl import YoutubeDL


class Player(Cog):
    def __init__(self, bot):
        try:
            self.BOT, self.vc, self.entries, self.ctx, self.arg = bot, None, None, None, None
            self.playlist.start()
            self.player.start()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    def cog_unload(self):
        try:
            self.playlist.cancel()
            self.player.cancel()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    @loop(count=1)
    async def playlist(self):
        try:
            if self.entries is not None:
                entries, ctx, arg = self.entries, self.ctx, self.arg
                self.entries, self.ctx, self.arg = None, None, None
                from db.queue import queue
                queue_1, position = [], 1
                for track in queue:
                    queue_1.append(track)
                if len(queue_1) > 0:
                    position = queue_1[-1] + 1

                def download(en, ps, lp):
                    for video_1 in en:
                        from db.queue import queue
                        download_1 = YoutubeDL(
                            params={"nocheckcertificate": "True", "format": "bestaudio", "noplaylist": "False",
                                    "default_search": "auto", "extract_flat": "in_playlist"}).extract_info(
                            url=video_1["id"], download=False)
                        queue.update({ps: {"channel": download_1["channel"], "title": download_1["title"],
                                           "webpage_url": download_1["webpage_url"],
                                           "thumbnail": download_1["thumbnail"],
                                           "url": download_1["url"], "duration": download_1["duration"]}})
                        run(main=save(file="queue", content=queue))
                        ps += 1

                if len(entries) == 1:
                    download = YoutubeDL(
                        params={"nocheckcertificate": "True", "format": "bestaudio", "noplaylist": "False",
                                "default_search": "auto", "extract_flat": "in_playlist"}).extract_info(
                        url=entries[0]["id"], download=False)
                    queue.update({position: {"channel": download["channel"], "title": download["title"],
                                             "webpage_url": download["webpage_url"], "thumbnail": download["thumbnail"],
                                             "url": download["url"], "duration": download["duration"]}})
                    await save(file="queue", content=queue)
                    embed = Embed(title="Плеер:", color=0x008000,
                                  description=f"Следующий трек успешно добавлен в очередь!\n\n"
                                              f"Используйте команду **!play** чтобы добавить новые...")
                    embed.add_field(name=f"{position}. {download['webpage_url']}", inline=False,
                                    value=f"Испольнитель: {download['channel']}\n"
                                          f"Название: {download['title']}\n"
                                          f"Длительность: {timedelta(seconds=download['duration'])}")
                    embed.set_thumbnail(url=download["thumbnail"])
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed)
                else:
                    videos, i = [[]], 0
                    for video in entries:
                        if len(videos[i]) < 25:
                            videos[i].append(video)
                        else:
                            i += 1
                            videos.append([video])
                    loop_1 = 1
                    for video in videos:
                        thread = Thread(target=download, args=(video, position, loop_1))
                        thread.start()
                        position += len(video)
                        loop_1 += 1
                    embed = Embed(title="Плеер:", color=0x008000,
                                  description=f"{len(entries)} треков успешно добавлены в очередь!\n\n"
                                              f"Используйте команду **!play** чтобы добавить новые...")
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed)
            else:
                self.playlist.cancel()
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop(count=1)
    async def player(self):
        try:
            while True:
                from db.queue import queue
                if len(queue) > 0:
                    for key in queue:
                        self.vc = None
                        try:
                            for vc in self.BOT.voice_clients:
                                await vc.disconnect()
                        except Exception:
                            await logs(level=LEVELS[1], message=format_exc())
                        try:
                            self.vc = await self.BOT.get_channel(id=1007577295877320765).connect()
                            try:
                                self.vc.play(FFmpegPCMAudio(source=f"{queue[key]['url']}",
                                                            executable="ffmpeg/bin/ffmpeg.exe"))
                            except Exception:
                                self.vc.play(FFmpegPCMAudio(source=f"{queue[key]['url']}"))
                                await logs(level=LEVELS[1], message=format_exc())
                        except Exception:
                            await logs(level=LEVELS[1], message=format_exc())
                        from db.settings import settings
                        try:
                            post = await self.BOT.get_channel(id=1007585194863251468).fetch_message(
                                id=settings["Плеер"])
                            await post.delete()
                        except Exception:
                            await logs(level=LEVELS[1], message=format_exc())
                        embed = Embed(title="Сейчас играет:", color=0x00FFFF)
                        embed.set_thumbnail(url=queue[key]["thumbnail"])
                        embed.add_field(name=queue[key]["title"], inline=False,
                                        value=f"Исполнитель: {queue[key]['channel']}\n"
                                              f"Длительность: {timedelta(seconds=queue[key]['duration'])}\n"
                                              f"Ссылка: {queue[key]['webpage_url']}")
                        embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                        post = await self.BOT.get_channel(id=1007585194863251468).send(embed=embed, components=[[
                            Button(emoji="▶️", style=ButtonStyle.blue, id="play"),
                            Button(emoji="⏸️", style=ButtonStyle.blue, id="pause"),
                            Button(emoji="⏭️", style=ButtonStyle.blue, id="next"),
                            Button(label="Очередь", style=ButtonStyle.green)]])
                        settings["Плеер"] = post.id
                        await save(file="settings", content=settings)
                        duration = queue[key]["duration"]
                        queue.pop(key)
                        await save(file="queue", content=queue)
                        await sleep(delay=duration)
                        break
                else:
                    try:
                        for vc in self.BOT.voice_clients:
                            await vc.disconnect()
                        from db.settings import settings
                        post = await self.BOT.get_channel(id=974755208108310639).fetch_message(id=settings["Плеер"])
                        await post.delete()
                    except Exception:
                        pass
                    await sleep(5)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if interaction.component.id == "play":
                try:
                    self.vc.resume()
                    await interaction.respond()
                except Exception:
                    pass
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.id == "pause":
                try:
                    self.vc.pause()
                    await interaction.respond()
                except Exception:
                    pass
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.id == "next":
                try:
                    self.player.restart()
                    await interaction.respond()
                except Exception:
                    pass
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.label == "Очередь":
                from db.queue import queue
                embeds, i = [], 0
                pages = int(len(queue) / 24)
                if pages == 0:
                    pages = 1
                embed = Embed(title="Очередь:", color=0x008000,
                              description=f"Сейчас в очереди {len(queue)} треков!\n\n"
                                          f"⬅️ Переключение страницы (1 из {pages}) ➡️\n\n"
                                          f"Используйте команду **!play** чтобы добавить новые...\n\n")
                embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                embeds.append(embed)
                selector = [[SelectOption(label="Все треки!", value="Все треки")]]
                if len(queue) > 0:
                    for item in queue:
                        if len(selector[i]) < 25:
                            embeds[i].add_field(name=f"{item}. {queue[item]['title']}", inline=False,
                                                value=f"Исполнитель: {queue[item]['channel']}\n"
                                                      f"Длительность: {timedelta(seconds=queue[item]['duration'])}\n"
                                                      f"Ссылка: {queue[item]['webpage_url']}")
                            selector[i].append(SelectOption(label=f"{item}. {queue[item]['title']}", value=f"{item}"))
                        else:
                            i += 1
                            embed = Embed(title="Очередь:", color=0x008000,
                                          description=f"Сейчас в очереди {len(queue)} треков!\n\n"
                                                      f"⬅️ Переключение страницы ({i + 1} из {pages}) ➡️\n\n"
                                                      f"Используйте команду **!play** чтобы добавить новые..."
                                                      f"\n\n")
                            embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                            embeds.append(embed)
                            selector.append([SelectOption(label="Все треки!", value="Все треки")])
                else:
                    embed = Embed(title="Очередь:", color=0x008000,
                                  description="Сейчас в очереди нет треков!\n\n"
                                              "Используйте команду **!play** чтобы добавить новые...")
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                if len(queue) > 0:
                    page = 0
                    post = await self.BOT.get_channel(id=interaction.channel.id).send(
                        embed=embeds[page], delete_after=60, components=[[
                            Button(emoji="⬅️", style=ButtonStyle.blue, id="previous_page"),
                            Button(emoji="➡️", style=ButtonStyle.blue, id="next_page")], [
                            Select(placeholder="Удалить из очереди:", options=selector[page])]])
                    try:
                        await interaction.respond()
                    except Exception:
                        pass
                    while True:
                        interaction = await self.BOT.wait_for(event="button_click")
                        try:
                            await self.BOT.get_channel(id=post.channel.id).fetch_message(id=post.id)
                        except Exception:
                            break
                        if interaction.message.id == post.id:
                            if interaction.component.id == "previous_page":
                                if page > 0:
                                    page -= 1
                                    await post.edit(embed=embeds[page], delete_after=60, components=[[
                                        Button(emoji="⬅️", style=ButtonStyle.blue, id="previous_page"),
                                        Button(emoji="➡️", style=ButtonStyle.blue, id="next_page")], [
                                        Select(placeholder="Удалить из очереди:", options=selector[page])]])
                                else:
                                    page = pages - 1
                                    await post.edit(embed=embeds[page], delete_after=60, components=[[
                                        Button(emoji="⬅️", style=ButtonStyle.blue, id="previous_page"),
                                        Button(emoji="➡️", style=ButtonStyle.blue, id="next_page")], [
                                        Select(placeholder="Удалить из очереди:", options=selector[page])]])
                            if interaction.component.id == "next_page":
                                if page + 1 < pages:
                                    page += 1
                                    await post.edit(embed=embeds[page], delete_after=60, components=[[
                                        Button(emoji="⬅️", style=ButtonStyle.blue, id="previous_page"),
                                        Button(emoji="➡️", style=ButtonStyle.blue, id="next_page")], [
                                        Select(placeholder="Удалить из очереди:", options=selector[page])]])
                                else:
                                    page = 0
                                    await post.edit(embed=embeds[page], delete_after=60, components=[[
                                        Button(emoji="⬅️", style=ButtonStyle.blue, id="previous_page"),
                                        Button(emoji="➡️", style=ButtonStyle.blue, id="next_page")], [
                                        Select(placeholder="Удалить из очереди:", options=selector[page])]])
                            try:
                                await interaction.respond()
                            except Exception:
                                pass
                else:
                    await interaction.send(embed=embed)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if interaction.component.label == "Да":
                from db.queue import queue
                queue = {}
                await save(file="queue", content=queue)
                await interaction.send(content="Очередь успешно очищена!")
                await self.BOT.get_channel(id=interaction.channel.id).send(
                    content=f"{interaction.user} Очистил **всю** очередь!")
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_select_option(self, interaction):
        try:
            if interaction.values[0] == "Все треки":
                await interaction.send(content="Вы действительно хотите полностью очистить очередь?",
                                       components=[Button(label="Да", style=ButtonStyle.red)])
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())
        try:
            if findall(pattern=r"^\d+", string=interaction.values[0]):
                from db.queue import queue
                if int(interaction.values[0]) in queue:
                    embed = Embed(title="Очередь:", color=0xFF0000,
                                  description="Следующий трек успешно удален из очереди!\n\n"
                                              "Используйте команду **!play** чтобы добавить новые...")
                    duration = timedelta(seconds=queue[int(interaction.values[0])]["duration"])
                    embed.add_field(name=f"{interaction.values[0]}. {queue[int(interaction.values[0])]['title']}",
                                    value=f"Исполнитель: {queue[int(interaction.values[0])]['channel']}\n"
                                          f"Длительность: {duration}\n"
                                          f"Ссылка: {queue[int(interaction.values[0])]['webpage_url']}", inline=False)
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    queue.pop(int(interaction.values[0]))
                    await save(file="queue", content=queue)
                    await interaction.send(embed=embed)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @command(description="Все 2", name="play", help="Добавить трек в очередь плеера",
             brief="`Ссылка на видео или плейлист` / `Поисковый запрос`", usage="!play https://youtu.be/asNy7WJHqdM")
    async def command_play(self, ctx, *, arg):
        try:
            if ctx.channel.id == 1007585194863251468:
                await ctx.message.delete(delay=1)
                download = YoutubeDL(
                    params={"nocheckcertificate": "True", "format": "bestaudio", "noplaylist": "False",
                            "default_search": "auto", "extract_flat": "in_playlist"}).extract_info(
                    url=arg, download=False)
                if "entries" in download:
                    self.entries, self.ctx, self.arg = download["entries"], ctx, arg
                    self.playlist.start()
                else:
                    from db.queue import queue
                    queue_1, pos = [], 1
                    for track in queue:
                        queue_1.append(track)
                    if len(queue_1) > 0:
                        pos = queue_1[-1] + 1
                    queue.update({pos: {"channel": download["channel"], "title": download["title"],
                                        "webpage_url": download["webpage_url"], "thumbnail": download["thumbnail"],
                                        "url": download["url"], "duration": download["duration"]}})
                    await save(file="queue", content=queue)
                    embed = Embed(title="Плеер:", color=0x008000,
                                  description=f"Следующий трек успешно добавлен в очередь!\n\n"
                                              f"Используйте команду **!play** чтобы добавить новые...")
                    embed.add_field(name=f"{pos}. {download['webpage_url']}", inline=False,
                                    value=f"Испольнитель: {download['channel']}\n"
                                          f"Название: {download['title']}\n"
                                          f"Длительность: {timedelta(seconds=download['duration'])}")
                    embed.set_thumbnail(url=download["thumbnail"])
                    embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
                    await ctx.send(embed=embed)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Player(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
