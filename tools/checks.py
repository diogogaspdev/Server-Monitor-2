from discord import Interaction
from discord import app_commands


def is_allowed():
    async def predicate(interaction: Interaction):

        if not interaction.response.is_done():
            await interaction.response.defer()

        pool = interaction.client.pool

        async with pool.acquire() as con:
            data = await con.fetchrow("""
                SELECT guild_id
                    FROM guilds
                WHERE
                    guild_id = $1
                    AND allowed = true
            """, interaction.guild.id)

            await con.close()

        if data:
            return True
        else:
            raise app_commands.CheckFailure("Guild not allowed!")

    return app_commands.check(predicate)


def is_premium():
    async def predicate(interaction: Interaction):

        if not interaction.response.is_done():
            await interaction.response.defer()

        pool = interaction.client.pool

        async with pool.acquire() as con:
            data = await con.fetchrow("""
                SELECT guild_id
                    FROM guilds
                WHERE
                    guild_id = $1
                    AND allowed = true
                    AND premium = true
            """, interaction.guild.id)

            await con.close()

        if data:
            return True
        else:
            raise app_commands.CheckFailure("Guild not premium!")

    return app_commands.check(predicate)
