import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from tools import *


class Owner(commands.Cog, name="owner"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(
        name="sync",
        description="Synchonizes the slash commands.",
    )
    @app_commands.describe(scope="The scope of the sync. Can be `global` or `guild`")
    @commands.is_owner()
    async def sync(self, context: Context, scope: str) -> None:
        """
        Synchonizes the slash commands.

        :param context: The command context.
        :param scope: The scope of the sync. Can be `global` or `guild`.
        """

        if scope == "global":
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Slash commands have been globally synchronized.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        elif scope == "guild":
            context.bot.tree.copy_global_to(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Slash commands have been synchronized in this guild.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description="The scope must be `global` or `guild`.", color=0xE02B2B
        )
        await context.send(embed=embed)

    @commands.command(
        name="unsync",
        description="Unsynchonizes the slash commands.",
    )
    @app_commands.describe(
        scope="The scope of the sync. Can be `global`, `current_guild` or `guild`"
    )
    @commands.is_owner()
    async def unsync(self, context: Context, scope: str) -> None:
        """
        Unsynchonizes the slash commands.

        :param context: The command context.
        :param scope: The scope of the sync. Can be `global`, `current_guild` or `guild`.
        """

        if scope == "global":
            context.bot.tree.clear_commands(guild=None)
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Slash commands have been globally unsynchronized.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        elif scope == "guild":
            context.bot.tree.clear_commands(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Slash commands have been unsynchronized in this guild.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description="The scope must be `global` or `guild`.", color=0xE02B2B
        )
        await context.send(embed=embed)

    @commands.command(
        name="load",
        description="Load a cog",
    )
    @app_commands.describe(cog="The name of the cog to load")
    @commands.is_owner()
    async def load(self, context: Context, cog: str) -> None:
        """
        The bot will load the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to load.
        """
        try:
            await self.bot.load_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Could not load the `{cog}` cog.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description=f"Successfully loaded the `{cog}` cog.", color=0xBEBEFE
        )
        await context.send(embed=embed)

    @commands.command(
        name="unload",
        description="Unloads a cog.",
    )
    @app_commands.describe(cog="The name of the cog to unload")
    @commands.is_owner()
    async def unload(self, context: Context, cog: str) -> None:
        """
        The bot will unload the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to unload.
        """
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Could not unload the `{cog}` cog.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description=f"Successfully unloaded the `{cog}` cog.", color=0xBEBEFE
        )
        await context.send(embed=embed)

    @commands.command(
        name="reload",
        description="Reloads a cog.",
    )
    @app_commands.describe(cog="The name of the cog to reload")
    @commands.is_owner()
    async def reload(self, context: Context, cog: str) -> None:
        """
        The bot will reload the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to reload.
        """
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Could not reload the `{cog}` cog.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description=f"Successfully reloaded the `{cog}` cog.", color=0xBEBEFE
        )
        await context.send(embed=embed)

    @commands.command(
        name="shutdown",
        description="Make the bot shutdown.",
    )
    @commands.is_owner()
    async def shutdown(self, context: Context) -> None:
        """
        Shuts down the bot.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(description="Shutting down. Bye! :wave:", color=0xBEBEFE)
        await context.send(embed=embed)
        await self.bot.close()

    @commands.command(
        name="say",
        description="The bot will say anything you want.",
    )
    @app_commands.describe(message="The message that should be repeated by the bot")
    @commands.is_owner()
    async def say(self, context: Context, *, message: str) -> None:
        """
        The bot will say anything you want.

        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        await context.send(message)

    @commands.command(
        name="embed",
        description="The bot will say anything you want, but within embeds.",
    )
    @app_commands.describe(message="The message that should be repeated by the bot")
    @commands.is_owner()
    async def embed(self, context: Context, *, message: str) -> None:
        """
        The bot will say anything you want, but using embeds.

        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        embed = self.bot.embed.copy_new()

        embed.description = message
        await context.send(embed=embed)

    @commands.command(
        name="add_premium",
        description="Adds a server to the premium list.",
    )
    @app_commands.describe(message="Adds a server to the premium list")
    @commands.is_owner()
    async def add_premium(self, context: Context, guild_id: int) -> None:
        """
        Adds a server to the premium list.

        :param context: The command context.
        :param guild_id: Guild ID to be added.
        """

        pool = self.bot.pool

        async with pool.acquire() as con:
            await con.execute("""
                INSERT INTO guilds (guild_id)
                VALUES ($1)
                ON CONFLICT (guild_id) DO UPDATE
                SET premium = True, allowed = True
            """, guild_id)

            await con.close()

        embed = self.bot.embed.copy_new()

        embed.title = "Premium"
        embed.description = f"Premium added for guild {guild_id}"

        await context.send(embed=embed)

    @commands.command(
        name="remove_premium",
        description="Removes a server from the premium list.",
    )
    @app_commands.describe(message="Removes a server from the premium list")
    @commands.is_owner()
    async def remove_premium(self, context: Context, guild_id: int) -> None:
        """
        Removes a server from the premium list.

        :param context: The command context.
        :param guild_id: Guild ID to be removed.
        """

        pool = self.bot.pool

        async with pool.acquire() as con:
            await con.execute("""
                UPDATE guilds
                SET premium=false
                WHERE guild_id=$1
            """, guild_id)

            await con.close()

        embed = self.bot.embed.copy_new()

        embed.title = "Premium"
        embed.description = f"Premium removed for guild {guild_id}"

        await context.send(embed=embed)

    @commands.command(
        name="add_allowed",
        description="Allows a server.",
    )
    @app_commands.describe(message="Allows a server")
    @commands.is_owner()
    async def add_allowed(self, context: Context, guild_id: int) -> None:
        """
        Allows a server.

        :param context: The command context.
        :param guild_id: Guild ID to be added.
        """

        pool = self.bot.pool

        async with pool.acquire() as con:
            await con.execute("""
                INSERT INTO guilds (guild_id)
                VALUES ($1)
                ON CONFLICT (guild_id) DO UPDATE
                SET allowed = True
            """, guild_id)

            await con.close()

        embed = self.bot.embed.copy_new()

        embed.title = "Premium"
        embed.description = f"Premium added for guild {guild_id}"

        await context.send(embed=embed)

    @commands.command(
        name="remove_allowed",
        description="Disallows a server.",
    )
    @app_commands.describe(message="Disallows a server")
    @commands.is_owner()
    async def remove_allowed(self, context: Context, guild_id: int) -> None:
        """
        Disallows a server.

        :param context: The command context.
        :param guild_id: Guild ID to be disallowed.
        """

        pool = self.bot.pool

        async with pool.acquire() as con:
            await con.execute("""
                UPDATE guilds
                SET premium=false, allowed=false
                WHERE guild_id=$1
            """, guild_id)

            await con.close()

        embed = self.bot.embed.copy_new()

        embed.title = "Premium"
        embed.description = f"Guild disallowed {guild_id}"

        await context.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Owner(bot))
