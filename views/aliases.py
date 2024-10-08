import json
import discord
from discord import ui

class AliasView(ui.View):
    def __init__(self, interaction: discord.Interaction, pool):
        super().__init__(timeout=300)
        self.interaction = interaction
        self.pool = pool

    @ui.button(label="Server Alias", style=discord.ButtonStyle.primary)
    async def server_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ServerAliasModal(view=self)
        await interaction.response.send_modal(modal)

    @ui.button(label="User Alias", style=discord.ButtonStyle.primary)
    async def user_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = UserAliasModal(view=self)
        await interaction.response.send_modal(modal)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.interaction.user


class ServerAliasModal(ui.Modal):
    def __init__(self, view: AliasView):
        super().__init__(title='Server Alias', timeout=60)
        self.view = view
        self.server = ui.TextInput(label='Server number', required=True)
        self.add_item(self.server)
        self.alias = ui.TextInput(label='Server Alias', style=discord.TextStyle.short, required=False, max_length=5)
        self.add_item(self.alias)
        self.friendly = ui.TextInput(label='Mark as friendly', style=discord.TextStyle.short, required=False, max_length=3, default='No')
        self.add_item(self.friendly)

    async def on_submit(self, interaction: discord.Interaction):
        server = self.server.value
        alias = self.alias.value
        friendly = self.friendly.value

        if self.alias.value:
            await interaction.response.send_message(f'Set {server} alias to {alias}!', ephemeral=True)
        else:
            await interaction.response.send_message(f'Cleared {server} alias!', ephemeral=True)

        async with self.view.pool.acquire() as con:
            data = await con.fetchrow("""
                SELECT guild_id, settings
                FROM guilds
                WHERE guild_id = $1
            """, interaction.guild.id)

            if not data:
                return

            settings = data['settings']

            if not settings:
                settings = {}
            else:
                settings = json.loads(settings)

            if 'ark_servers' not in settings:
                settings['ark_servers'] = {}

            if server not in settings['ark_servers']:
                settings['ark_servers'][server] = {}

            settings['ark_servers'][server]['alias'] = alias
            settings['ark_servers'][server]['friendly'] = True if friendly.upper() in ('YES', 'YE', 'Y') else False

            await con.execute("""
                UPDATE guilds
                SET settings = $2
                WHERE guild_id = $1
            """, interaction.guild.id, json.dumps(settings))

            await con.close()


class UserAliasModal(ui.Modal):
    def __init__(self, view: AliasView):
        super().__init__(title='User Alias', timeout=60)
        self.view = view
        self.user = ui.TextInput(label='User PUID', required=True)
        self.add_item(self.user)
        self.alias = ui.TextInput(label='User Alias', style=discord.TextStyle.short, required=False, max_length=10)
        self.add_item(self.alias)

    async def on_submit(self, interaction: discord.Interaction):
        user = self.user.value
        alias = self.alias.value

        if self.alias.value:
            await interaction.response.send_message(f'Set {user} alias to {alias}!', ephemeral=True)
        else:
            await interaction.response.send_message(f'Cleared {user} alias!', ephemeral=True)

        async with self.view.pool.acquire() as con:
            data = await con.fetchrow("""
                SELECT guild_id, settings
                FROM guilds
                WHERE guild_id = $1
            """, interaction.guild.id)

            if not data:
                return

            settings = data['settings']

            if not settings:
                settings = {}
            else:
                settings = json.loads(settings)

            if 'users' not in settings:
                settings['users'] = {}

            if user not in settings['users']:
                settings['users'][user] = {}

            settings['users'][user]['alias'] = alias

            await con.execute("""
                UPDATE guilds
                SET settings = $2
                WHERE guild_id = $1
            """, interaction.guild.id, json.dumps(settings))

            await con.close()