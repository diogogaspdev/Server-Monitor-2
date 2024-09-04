import time
from datetime import datetime

from discord import Embed

from tools.db_connector import DbConnector


class MyEmbed(Embed):
    def __init__(self):
        super().__init__()

    async def setup_standard(self):
        self.timestamp = datetime.fromtimestamp(time.time())

        conn = await DbConnector().setup()

        data = await conn.fetchrow("""
            SELECT SETTINGS ->> 'footer' footer,
                SETTINGS ->> 'thumbnail' thumbnail,
                SETTINGS ->> 'icon' icon
            FROM CONFIG
            WHERE KEY = 'embed'
        """)

        self.set_footer(text=data['footer'], icon_url=data['icon'])
        self.set_thumbnail(url=data['thumbnail'])
