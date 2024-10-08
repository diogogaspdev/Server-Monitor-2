import discord
from discord.ext import tasks

from tools.eos import EOS


class BasicChannel:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id
        self.task_name = f"Basic Channel {channel_id} loop"

        self.eos = EOS()

        self.basic_channel = tasks.loop(minutes=6, name=self.task_name)(self._basic_channel_loop)
        self.basic_channel.after_loop(self.after)
        self.basic_channel.before_loop(self.before)

    async def _basic_channel_loop(self):
        channel = self.bot.get_channel(self.channel_id)

        if not channel:
            self.bot.logger.warning(f"Basic Channel couldn't find channel {self.task_name}")
            return

        pool = self.bot.pool

        async with pool.acquire() as con:
            data = await con.fetchrow("""
                SELECT settings ->> 'ark_server' ark_server
                    FROM monitors
                WHERE channel_id = $1
                AND type = 1
            """, channel.id)

            await con.close()

        result = await self.eos.matchmaking(data['ark_server'])

        if result:
            await channel.edit(name=f"{channel.name.split('-')[0]}-{result['totalPlayers']}")
        else:
            await channel.edit(name=f"{channel.name.split('-')[0]}-OFF")

    async def before(self):
        await self.bot.wait_until_ready()
        self.bot.logger.info(f"Started {self.task_name}")

    async def after(self):
        self.bot.logger.info(f"Ended {self.task_name}")

    def start(self):
        self.basic_channel.start()
        return self

    def stop(self):
        self.basic_channel.cancel()

    def is_running(self):
        return self.basic_channel.is_running()

    def __str__(self):
        return self.task_name


class BasicMonitor:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id
        self.task_name = f"Basic Monitor {channel_id} loop"
        self.last_count = None

        self.eos = EOS()

        self.basic_monitor = tasks.loop(minutes=1, name=self.task_name)(self._basic_monitor_loop)
        self.basic_monitor.after_loop(self.after)
        self.basic_monitor.before_loop(self.before)

    async def _basic_monitor_loop(self):
        channel = self.bot.get_channel(self.channel_id)

        if not channel:
            self.bot.logger.warning(f"Basic Monitor couldn't find channel {self.task_name}")
            return

        pool = self.bot.pool

        async with pool.acquire() as con:
            data = await con.fetchrow("""
                SELECT settings ->> 'ark_server' ark_server
                    FROM monitors
                WHERE channel_id = $1
                AND type = 2
            """, channel.id)

            await con.close()

        if not data:
            return

        result = await self.eos.matchmaking(data['ark_server'])

        embed = self.bot.embed.copy_new()

        embed.set_thumbnail(url=None)

        if not result:
            embed.colour = discord.Colour.red()

            embed.title = "Error"
            embed.description = f"Couldn't reach {data['ark_server']}!"

            await channel.send(embed=embed)

            return

        if self.last_count is None:
            balance = result['totalPlayers']
        else:
            balance = result['totalPlayers'] - self.last_count

        self.last_count = result['totalPlayers']

        if balance > 0:
            embed.colour = discord.Colour.blue()
        elif balance < 0:
            embed.colour = discord.Colour.dark_purple()
        else:
            return

        embed.clear_fields()

        embed.title = result['attributes']['CUSTOMSERVERNAME_s']

        embed.add_field(
            name="In-game Day",
            value=result['attributes']['DAYTIME_s'],
            inline=False
        )
        embed.add_field(
            name="Player Count",
            value=result['totalPlayers'],
            inline=False
        )
        embed.add_field(
            name="Last 60s Balance",
            value=f"{abs(balance)} {'players' if abs(balance) > 1 else 'player'} {'joined' if balance > 0 else 'left'}!",
            inline=False
        )
        embed.add_field(
            name="Ping",
            value=result['attributes']['EOSSERVERPING_l'],
            inline=False
        )

        await channel.send(embed=embed)

    async def before(self):
        await self.bot.wait_until_ready()
        self.bot.logger.info(f"Started {self.task_name}")

    async def after(self):
        self.bot.logger.info(f"Ended {self.task_name}")

    def start(self):
        self.basic_monitor.start()
        return self

    def stop(self):
        self.basic_monitor.cancel()

    def is_running(self):
        return self.basic_monitor.is_running()

    def __str__(self):
        return self.task_name
