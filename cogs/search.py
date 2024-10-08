import discord
from discord import app_commands, Interaction
from discord.ext import commands

from tools import *


class Search(commands.Cog, name="Search"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="official",
        description="Lookup official server player count.",
    )
    @checks.is_allowed()
    async def official(self, interaction: Interaction, server_number: int) -> None:
        """
        Searches official server information.

        :param interaction: The application command interaction.
        :param server_number: The server number to be looked up.
        """

        if not interaction.response.is_done():
            await interaction.response.defer()

        embed = self.bot.embed.copy_new()

        try:
            server_info = await eos.EOS().matchmaking(server_number, official=True)
        except:

            embed.colour = discord.Colour.brand_red()

            embed.title = "Error"
            embed.description = f"Couldn't reach {server_number}!"

            await interaction.edit_original_response(embed=embed)

            return

        ip = server_info['attributes']['ADDRESS_s']
        port = server_info['attributes']['ADDRESSBOUND_s'].split(":")[1]
        ip_and_port = f"{ip}:{port}"

        embed.title = "Official Server"
        embed.colour = discord.Colour.green()

        embed.add_field(name="Server Name", value=f"```ansi\n{server_info['attributes']['CUSTOMSERVERNAME_s']}```",
                        inline=False)
        embed.add_field(name="In-game Day", value=f"```ansi\n{server_info['attributes']['DAYTIME_s']}```", inline=False)
        embed.add_field(name="Player Count", value=f"```ansi\n{server_info['totalPlayers']}```", inline=True)
        embed.add_field(name="Ping", value=f"```ansi\n{server_info['attributes']['EOSSERVERPING_l']}```", inline=True)
        embed.add_field(name="IP/Port", value=f"```ansi\n{ip_and_port}```", inline=False)

        await interaction.edit_original_response(embed=embed)

        return

    @official.error
    async def official_error(self, interaction: discord.Interaction, error):

        if not interaction.response.is_done():
            await interaction.response.defer()

        if isinstance(error, discord.app_commands.CheckFailure):
            embed = self.bot.embed.copy_new()

            embed.title = "Error!"
            embed.description = str(error).capitalize()
            embed.color = discord.Colour.red()

            await interaction.edit_original_response(embed=embed)
        else:
            raise error


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Search(bot))
