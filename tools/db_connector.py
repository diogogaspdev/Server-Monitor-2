import os

import asyncpg


class DbConnector:

    def __init__(self):
        self.pool = None
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.schema = os.getenv("DB_SCHEMA")

    async def setup(self):
        self.pool = await asyncpg.create_pool(
            user=self.user,
            password=self.password,
            database=self.db_name,
            host=self.host,
            port=self.port,
            server_settings={
                "search_path": self.schema
            },
            min_size=1,
            max_size=25
        )

        return self.pool
