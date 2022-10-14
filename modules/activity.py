from asyncio import run
from datetime import datetime
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord.utils import get
from gigabot import logs, LEVELS, save
from traceback import format_exc


class Activity(Cog):
    def __init__(self, bot):
        try:
            self.BOT, self.voice = bot, {}
            self.update_members.start()
            self.update_channels.start()
            self.update_roles.start()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    def cog_unload(self):
        try:
            self.update_members.cancel()
            self.update_channels.cancel()
            self.update_roles.cancel()
        except Exception:
            run(main=logs(level=LEVELS[4], message=format_exc()))

    @loop(hours=1)
    async def update_members(self):
        try:
            users = {}
            from db.members import members
            for guild in self.BOT.guilds:
                for member in guild.members:
                    if member.id not in members:
                        members.update({member.id: {"Имя аккаунта": f"{member.name}#{member.discriminator}",
                                                    "Статус": True,
                                                    "Время последнего сообщения": datetime.utcnow(),
                                                    "Бот": False,
                                                    "Достижения": [],
                                                    "Дни": (datetime.utcnow() - member.joined_at).days,
                                                    "Сообщения": 0,
                                                    "Упоминания": 0,
                                                    "Лайки": 0,
                                                    "Дизлайки": 0,
                                                    "Время в голосовых каналах": 0,
                                                    "Дата добавления на сервер": member.joined_at,
                                                    "Роли": [],
                                                    "Крестики-нолики": {"Сыграно": 0, "Побед": 0, "Поражений": 0,
                                                                        "Процент": 0},
                                                    "Тетрис": {"Сыграно": 0, "Лучший счет": 0}}})
                        if member.bot:
                            members[member.id]["Бот"] = True
                    else:
                        members[member.id].update({"Имя аккаунта": f"{member.name}#{member.discriminator}",
                                                   "Дата добавления на сервер": member.joined_at})
                        if member.bot:
                            members[member.id]["Бот"] = True
                        voices = members[member.id]["Время в голосовых каналах"]
                        if members[member.id]["Сообщения"] >= 100 or voices >= 300 * 60:
                            if get(iterable=guild.roles, id=989814115214168125) not in member.roles:
                                await member.add_roles(get(iterable=guild.roles, id=989814115214168125))
                                await member.send(embed=Embed(title="Уведомление!", color=0xFFA500).add_field(
                                    name="Выдача роли!", value=f"Поздравляем! Вам выдана роль "
                                                               f"{get(iterable=guild.roles, id=989814115214168125)}"))
                        if members[member.id]["Сообщения"] >= 200 or voices >= 600 * 60:
                            if get(iterable=guild.roles, id=989815195155185704) not in member.roles:
                                await member.add_roles(get(iterable=guild.roles, id=989815195155185704))
                                await member.send(embed=Embed(title="Уведомление!", color=0xFFA500).add_field(
                                    name="Выдача роли!", value=f"Поздравляем! Вам выдана роль "
                                                               f"{get(iterable=guild.roles, id=989815195155185704)}"))
                        if members[member.id]["Сообщения"] < 100 and voices < 300 * 60:
                            if get(iterable=member.guild.roles, id=989814115214168125) in member.roles:
                                await member.remove_roles(get(iterable=member.guild.roles, id=989814115214168125))
                        if members[member.id]["Сообщения"] < 200 and voices < 600 * 60:
                            if get(iterable=member.guild.roles, id=989815195155185704) in member.roles:
                                await member.remove_roles(get(iterable=member.guild.roles, id=989815195155185704))
                for channel in guild.channels:
                    if str(channel.type) == "text":
                        async for message in channel.history(limit=1000000000):
                            if message.author.id in members:
                                if message.author not in users:
                                    users.update({message.author: {"Сообщений": 1, "Упоминаний": 0,
                                                                   "Дата": message.created_at}})
                                else:
                                    users[message.author]["Сообщений"] += 1
                                if message.created_at < users[message.author]["Дата"]:
                                    users[message.author]["Дата"] = message.created_at
                                if len(message.mentions) > 0:
                                    for member in message.mentions:
                                        if message.author.id in members:
                                            if member not in users:
                                                users.update({member: {"Сообщений": 0, "Упоминаний": 1,
                                                                       "Дата": message.created_at}})
                                            else:
                                                users[member]["Упоминаний"] += 1
                                            if message.created_at < users[member]["Дата"]:
                                                users[member]["Дата"] = message.created_at
            for member in users:
                try:
                    try:
                        if member.joined_at < users[member]["Дата"]:
                            users[member]["Дата"] = member.joined_at
                    except Exception:
                        users[member]["Дата"] = member.joined_at
                except Exception:
                    pass
                members[member.id].update({"Дни": (datetime.utcnow() - users[member]["Дата"]).days,
                                           "Сообщения": users[member]["Сообщений"],
                                           "Упоминания": users[member]["Упоминаний"],
                                           "Дата добавления на сервер": users[member]["Дата"]})
                if member.bot:
                    members[member.id]["Бот"] = True
            await save(file="members", content=members)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop(hours=1)
    async def update_channels(self):
        try:
            from db.channels import channels
            for guild in self.BOT.guilds:
                for channel in guild.channels:
                    channels.update({channel.id: {"Название": channel.name, "Тип": str(channel.type),
                                                  "Позиция": channel.position}})
            await save(file="channels", content=channels)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @loop(hours=1)
    async def update_roles(self):
        try:
            from db.roles import roles
            for guild in self.BOT.guilds:
                for role in guild.roles:
                    roles.update({role.id: {"Название": role.name, "Цвет": role.color.value, "Позиция": role.position}})
            await save(file="roles", content=roles)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_message(self, message):
        try:
            from db.members import members
            if message.author.id in members:
                members[message.author.id]["Время последнего сообщения"] = message.created_at
                await save(file="members", content=members)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_reaction_add(self, reaction, user):
        try:
            if str(reaction) == "👍":
                from db.members import members
                members[user.id]["Лайки"] += 1
                await save(file="members", content=members)
            if str(reaction) == "👎":
                from db.members import members
                members[user.id]["Дизлайки"] += 1
                await save(file="members", content=members)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            if member.id != self.BOT.user.id:
                if before.channel is None and after.channel is not None:
                    self.voice.update({member: datetime.now()})
                if after.channel is None and before.channel is not None:
                    if self.voice.get(member) is not None:
                        delta = datetime.now() - self.voice[member]
                        from db.members import members
                        members[member.id]["Время в голосовых каналах"] += int(delta.seconds)
                        await save(file="members", content=members)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Activity(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
