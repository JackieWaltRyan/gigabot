import sys
from os import execl
from traceback import format_exc

from discord import Embed, utils
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord_components import Button, ButtonStyle

from bot import DB, SET


class Posts(Cog):
    def __init__(self, bot):
        self.BOT = bot
        self.posts.start()

    def cog_unload(self):
        self.posts.cancel()

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

    @loop(count=1)
    async def posts(self):
        try:
            channel, rid1, rid2 = 974901059380203570, 974764853707280384, 974920743366320188
            try:
                rules = await self.BOT.get_channel(channel).fetch_message(
                    int(DB.server.channels.find_one({"_id": channel})["Роли"]))
                await rules.delete()
            except Exception:
                pass
            e1 = Embed(title="Возми себе роль:", color=0x008000, description=f"<@&{rid1}> - доступ в игровой чат.\n\n"
                                                                             f"<@&{rid2}> - доступ к 18+ чату.")
            e1.set_footer(text=SET["Футер"]["Текст"], icon_url=SET["Футер"]["Ссылка"])
            rulesid = await self.BOT.get_channel(channel).send(embed=e1, components=[[
                Button(label=DB.server.roles.find_one({"_id": rid1})["Название"], style=ButtonStyle.blue,
                       id=str(rid1)),
                Button(label=DB.server.roles.find_one({"_id": rid2})["Название"], style=ButtonStyle.blue,
                       id=str(rid2))]])
            DB.server.channels.update_one({"_id": channel}, {"$set": {"Роли": rulesid.id}})
        except Exception:
            await self.errors("Пост Роли:", format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if len(interaction.component.id) == 18:
                role = utils.get(interaction.user.guild.roles, id=int(interaction.component.id))
                if role in interaction.user.roles:
                    await interaction.send(f"Поздравляем! Вам убрана роль <@&{interaction.component.id}>")
                    await interaction.user.remove_roles(role)
                    await self.alerts(interaction.user, f"Убрана роль: {role.name}")
                else:
                    await interaction.send(f"Поздравляем! Вам выдана роль <@&{interaction.component.id}>")
                    await interaction.user.add_roles(role)
                    await self.alerts(interaction.user, f"Выдана роль: {role.name}")
        except Exception:
            await self.errors(f"Кнопка {interaction.component.label}:", format_exc())


def setup(bot):
    bot.add_cog(Posts(bot))
