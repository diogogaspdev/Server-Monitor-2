import time
from datetime import datetime

from discord import Embed


class MyEmbed(Embed):
    def __init__(self):
        super().__init__()

    async def setup_standard(self, pool):
        async with pool.acquire() as con:
            data = await con.fetchrow("""
                SELECT SETTINGS ->> 'footer' footer,
                    SETTINGS ->> 'thumbnail' thumbnail,
                    SETTINGS ->> 'icon' icon
                FROM CONFIG
                WHERE KEY = 'embed'
            """)

            await con.close()

        self.set_footer(text=data['footer'], icon_url=data['icon'])
        self.set_thumbnail(url=data['thumbnail'])

    def copy_new(self) -> Embed:
        self.timestamp = datetime.fromtimestamp(time.time())
        return self.copy()
