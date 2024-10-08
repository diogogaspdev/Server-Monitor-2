import discord

class MonitorSetupView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.monitor_type = None
        self.channel = None
        self.server_numbers = []