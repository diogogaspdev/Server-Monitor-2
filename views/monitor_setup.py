import discord
from discord import Interaction

from tools import *


def get_options():
    conn = db_connector.DbConnector()

    cur = conn.cur

    cur.execute("""
        SELECT 
            type,
            label,
            description,
            emoji
        FROM monitor_type
        ORDER BY type ASC
    """)

    data = cur.fetchall()

    conn.close()

    options = []
    for option in data:
        options.append(
            discord.SelectOption(
                value=option[0],
                label=option[1],
                description=option[2],
                # emoji=option[3]
            )
        )

    return options


class SelectChannel(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Choose a channel to place the monitor...",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.select_channel(interaction, self.values)


class SetupView(discord.ui.View):
    channel = None
    monitor_type = None
    alias = None
    options = get_options()

    @discord.ui.select(
        placeholder="Choose a type of monitor...",
        options=options
    )
    async def select_type(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        self.monitor_type = select_item.values
        self.children[0].disabled = True
        select_channel = SelectChannel()
        self.add_item(select_channel)
        await interaction.message.edit(view=self)
        await interaction.response.defer()

    async def select_channel(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        self.channel = select_item
        self.children[1].disabled = True
        await interaction.message.edit(view=self)
        self.stop()
