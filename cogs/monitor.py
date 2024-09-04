from discord.ext import commands, tasks

from tools import *


# from views.monitor_setup import SetupView


class Monitor(commands.Cog, name="Monitor"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.eos = eos.EOS()

    @tasks.loop(minutes=5.0)
    async def player_monitor(self) -> None:
        self.bot.logger.info(f"Running player_monitor")
        await self.eos.players_all()
        self.bot.logger.info(f"Finished player_monitor")

    @player_monitor.before_loop
    async def before_player_monitor(self) -> None:
        await self.bot.wait_until_ready()
        self.bot.logger.info(f"Started player_monitor loop")

    @player_monitor.after_loop
    async def after_player_monitor(self) -> None:
        self.bot.logger.info(f"Ended player_monitor loop")

    @tasks.loop(minutes=1.0)
    async def server_monitor(self) -> None:
        self.bot.logger.info(f"Running server_monitor")
        await self.eos.matchmaking_all()
        self.bot.logger.info(f"Finished server_monitor")

    @server_monitor.before_loop
    async def before_server_monitor(self) -> None:
        await self.bot.wait_until_ready()
        self.bot.logger.info(f"Started server_monitor loop")

    @server_monitor.after_loop
    async def after_server_monitor(self) -> None:
        self.bot.logger.info(f"Ended server_monitor loop")

    async def cog_load(self) -> None:
        self.server_monitor.start()
        self.player_monitor.start()

    async def cog_unload(self) -> None:
        self.server_monitor.stop()
        self.player_monitor.stop()


async def setup(bot) -> None:
    await bot.add_cog(Monitor(bot))
