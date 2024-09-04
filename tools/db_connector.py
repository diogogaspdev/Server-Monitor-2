import os

import asyncpg

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
schema = os.getenv("DB_SCHEMA")


class DbConnector:

    def __init__(self):
        self.conn = None

    async def setup(self):
        self.conn = await asyncpg.connect(
            user=user,
            password=password,
            database=db_name,
            host=host,
            port=port,
            server_settings={
                "search_path": schema
            }
        )

        return self.conn
