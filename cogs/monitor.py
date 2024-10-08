from discord import app_commands, Interaction
from discord.ext import commands, tasks
from discord.ext.commands import Context

from monitors import *
from tools import *
from views.aliases import AliasView


class Monitor(commands.Cog, name="Monitor"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.eos = eos.EOS()
        self.player_monitor.add_exception_type()

    @app_commands.command(
        name="hub",
        description="Hub setup wizard"
    )
    @checks.is_premium()
    async def hub(self, interaction: Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer()

        pass

    @app_commands.command(
        name="alias",
        description="Set a alias for a server"
    )
    @checks.is_premium()
    async def alias_setup(self, interaction: Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer()

        view = AliasView(interaction, pool=self.bot.pool)

        await interaction.edit_original_response(view=view)

        await view.wait()


    @commands.command(
        name="monitor_audit",
        description="Shows monitors"
    )
    @commands.is_owner()
    async def audit(self, ctx: Context):
        embed = self.bot.embed.copy_new()

        embed.title = "Monitor Audit"
        embed.set_thumbnail(url=None)

        for task in self.bot.monitor_tasks:
            embed.add_field(
                name=task,
                value=f"{'Running' if task.is_running() else 'Stopped'}",
                inline=False
            )

        await ctx.send(embed=embed)

    @tasks.loop(minutes=15)
    async def player_monitor(self) -> None:
        if self.player_monitor._stop_next_iteration:
            return
        await self.eos.players_all()

    @player_monitor.before_loop
    async def before_player_monitor(self) -> None:
        await self.bot.wait_until_ready()
        self.bot.logger.info(f"Started player_monitor loop")

    @player_monitor.after_loop
    async def after_player_monitor(self) -> None:
        self.bot.logger.info(f"Ended player_monitor loop")

    @tasks.loop(minutes=1)
    async def server_monitor(self) -> None:
        if self.server_monitor._stop_next_iteration:
            return
        await self.eos.matchmaking_all()

    @server_monitor.before_loop
    async def before_server_monitor(self) -> None:
        await self.bot.wait_until_ready()
        self.bot.logger.info(f"Started server_monitor loop")

    @server_monitor.after_loop
    async def after_server_monitor(self) -> None:
        self.bot.logger.info(f"Ended server_monitor loop")

    async def cog_load(self) -> None:
        # general monitors
        self.server_monitor.start()
        self.player_monitor.start()

        pool = self.bot.pool

        async with pool.acquire() as con:
            data = await con.fetch("""
                SELECT channel_id, type
                FROM server_monitor.monitors;
            """)

            for record in data:
                if record['type'] == 1:
                    self.bot.monitor_tasks.append(basic.BasicChannel(self.bot, record['channel_id']).start())
                elif record['type'] == 2:
                    self.bot.monitor_tasks.append(basic.BasicMonitor(self.bot, record['channel_id']).start())
                elif record['type'] == 5:
                    self.bot.monitor_tasks.append(hub.Hub(self.bot, record['channel_id']).start())

            await con.close()

    async def cog_unload(self) -> None:
        self.server_monitor.stop()
        self.player_monitor.stop()

        for task in self.bot.monitor_tasks:
            if task:
                task.stop()


async def setup(bot) -> None:
    await bot.add_cog(Monitor(bot))
