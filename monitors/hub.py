import asyncio
import json
import time

from discord.ext import tasks

from tools.eos import EOS


class Hub:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id
        self.task_name = f"Hub {channel_id} loop"

        self.eos = EOS()

        self.hub = tasks.loop(seconds=15, name=self.task_name)(self._hub_loop)
        self.hub.after_loop(self.after_hub)
        self.hub.before_loop(self.before_hub)

    async def _hub_loop(self):
        channel = self.bot.get_channel(self.channel_id)

        if not channel:
            self.bot.logger.warning(f"Hub couldn't find channel {self.task_name}")
            return

        if self.hub.current_loop == 0:
            await channel.send(content="Loading...")
            await asyncio.sleep(1)

        message = [message async for message in channel.history(limit=1)]

        pool = self.bot.pool

        async with pool.acquire() as con:
            data = await con.fetchrow("""
                SELECT settings -> 'ark_servers' ark_servers
                    FROM monitors
                WHERE channel_id = $1
                AND type = 5
            """, channel.id)

            embed = self.bot.embed.copy_new()

            embed.set_thumbnail(url=None)

            token = await self.eos.get_token()

            server_infos = await asyncio.gather(
                *[self.eos.matchmaking(server, token=token) for server in json.loads(data['ark_servers'])])

            combined_results = [
                {
                    "matchmaking": matchmaking_result['totalPlayers'] if matchmaking_result else "OFF",
                    "server": server
                }
                for matchmaking_result, server in zip(server_infos, json.loads(data['ark_servers']))
            ]

            for session in combined_results:
                data = await con.fetchrow("""
                    SELECT
                        COALESCE((SETTINGS -> 'ark_servers' -> $1 ->> 'alias'), '') as alias,
                        COALESCE((SETTINGS -> 'ark_servers' -> $1 ->> 'friendly'), 'false') as friendly
                    FROM
                        GUILDS
                    WHERE
                        GUILD_ID = $2
                """, session['server'], channel.guild.id)

                if not data:
                    data = {'alias': '', 'friendly': 'false'}

                name = f"{session['server']} {data['alias']}"

                embed.add_field(
                    name=name,
                    value=str(
                        f"""```ansi\n\u001b[1;{"36" if json.loads(data['friendly']) else "31"}m{session['matchmaking']}```"""),
                    inline=True
                )

            if message and message[0].author.id == self.bot.user.id:
                await message[0].edit(content=f"Last Updated <t:{int(time.time())}:R>", embed=embed)
            else:
                await channel.send(content=f"Last Updated <t:{int(time.time())}:R>", embed=embed)

            await con.close()

    async def before_hub(self):
        await self.bot.wait_until_ready()
        self.bot.logger.info(f"Started {self.task_name}")

    async def after_hub(self):
        self.bot.logger.info(f"Ended {self.task_name}")

    def start(self):
        self.hub.start()
        return self

    def stop(self):
        self.hub.cancel()

    def is_running(self):
        return self.hub.is_running()

    def __str__(self):
        return self.task_name
