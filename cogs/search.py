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
    async def official(self, interaction: Interaction, server_number: int) -> None:
        """
        Searches official server information.

        :param interaction: The application command interaction.
        :param server_number: The server number to be looked up.
        """

        await interaction.response.defer()

        embed = my_embed.MyEmbed()

        await embed.setup_standard()

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

    # @app_commands.command(
    #     name="unofficial",
    #     description="Lookup unofficial server player count.",
    # )
    # async def unofficial(self, interaction: Interaction, server_number: int) -> None:
    #     """
    #     Searches official server information.
    #
    #     :param interaction: The application command interaction.
    #     :param server_number: The server number to be looked up.
    #     """
    #
    #     await interaction.response.defer()
    #
    #     embed = my_embed.MyEmbed()
    #
    #     await embed.setup_standard()
    #
    #     try:
    #         server_info = await eos.EOS().matchmaking(server_number, official=False)
    #     except:
    #
    #         embed.colour = discord.Colour.brand_red()
    #
    #         embed.title = "Error"
    #         embed.description = f"Couldn't reach {server_number}!"
    #
    #         await interaction.edit_original_response(embed=embed)
    #
    #         return
    #
    #     ip = server_info['attributes']['ADDRESS_s']
    #     port = server_info['attributes']['ADDRESSBOUND_s'].split(":")[1]
    #     ip_and_port = f"{ip}:{port}"
    #
    #     embed.title = "Unofficial Server"
    #     embed.colour = discord.Colour.green()
    #
    #     embed.add_field(name="Server Name", value=f"```ansi\n{server_info['attributes']['CUSTOMSERVERNAME_s']}```", inline=False)
    #     embed.add_field(name="In-game Day", value=f"```ansi\n{server_info['attributes']['DAYTIME_s']}```", inline=False)
    #     embed.add_field(name="Player Count", value=f"```ansi\n{server_info['totalPlayers']}```", inline=True)
    #     embed.add_field(name="Ping", value=f"```ansi\n{server_info['attributes']['EOSSERVERPING_l']}```", inline=True)
    #     embed.add_field(name="IP/Port", value=f"```ansi\n{ip_and_port}```", inline=False)
    #
    #     await interaction.edit_original_response(embed=embed)
    #
    #     return


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Search(bot))
