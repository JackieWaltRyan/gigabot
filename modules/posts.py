from asyncio import run
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord.utils import get
from discord_components_mirror import Button, ButtonStyle
from gigabot import LEVELS, FOOTER, logs
from random import choice
from traceback import format_exc


class Posts(Cog):
    def __init__(self, bot):
        self.BOT = bot
        self.post_roles.start()

    @loop(count=1)
    async def post_roles(self):
        try:
            await self.BOT.get_channel(id=974901059380203570).purge()
            role1, role2, role3, role4 = 974764853707280384, 974920743366320188, 979770070735675432, 998575031451922522
            embed = Embed(title="Возми себе роль:", color=0x008000,
                          description=f"<@&{role1}> - доступ в <#975369937210195978>.\n\n"
                                      f"<@&{role2}> - доступ в <#974767244670296105>.\n\n"
                                      f"<@&{role3}> - доступ в <#979769343036502026>.\n\n"
                                      f"<@&{role4}> - доступ в <#998574750177697842>.")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/915008263253266472/986216006944952420/"
                                    "roles.png")
            embed.set_footer(text=FOOTER["Текст"], icon_url=FOOTER["Ссылка"])
            styles = [ButtonStyle.green, ButtonStyle.blue, ButtonStyle.red, ButtonStyle.gray]
            from db.roles import roles
            post = await self.BOT.get_channel(id=974901059380203570).send(embed=embed, components=[[
                Button(label=roles[role1]["Название"], style=choice(styles), id=str(role1)),
                Button(label=roles[role2]["Название"], style=choice(styles), id=str(role2)),
                Button(label=roles[role3]["Название"], style=choice(styles), id=str(role3)),
                Button(label=roles[role4]["Название"], style=choice(styles), id=str(role4))]])
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())

    @Cog.listener()
    async def on_button_click(self, interaction):
        try:
            if len(interaction.component.id) == 18:
                role = get(iterable=interaction.user.guild.roles, id=int(interaction.component.id))
                if role in interaction.user.roles:
                    await interaction.send(f"Поздравляем! Вам убрана роль <@&{interaction.component.id}>")
                    await interaction.user.remove_roles(role)
                else:
                    await interaction.send(f"Поздравляем! Вам выдана роль <@&{interaction.component.id}>")
                    await interaction.user.add_roles(role)
        except Exception:
            await logs(level=LEVELS[4], message=format_exc())


def setup(bot):
    try:
        bot.add_cog(cog=Posts(bot=bot))
    except Exception:
        run(main=logs(level=LEVELS[4], message=format_exc()))
