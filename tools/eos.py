import asyncio
import datetime
import json
import random
from datetime import datetime

import aiohttp
import websockets
from pytz import utc, timezone

from tools.db_connector import DbConnector


async def random_user():
    url = "https://cdn2.arkdedicated.com/asa/BanList.txt"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.text()

    data = data.split()

    return data[random.randint(1, len(data))][:-2]


class EOS:
    def __init__(self):
        self.client_secret = "eHl6YTc4OTFtdW9tUm15bklJSGFKQjlDT0JLa3dqNm46UFA1VUd4eXNFaWVOZlNyRWljYUQxTjJCYjNUZFh1RDd4SFljc2RVSFo3cw=="
        self.deployment_id = "ad9a8feffb3b4b2ca315546f038c3ae2"
        self.api_url = "https://api.epicgames.dev"

    async def get_token(self):
        url = self.api_url + "/auth/v1/oauth/token"

        payload = f"grant_type=client_credentials&deployment_id={self.deployment_id}"
        headers = {
            "Authorization": f"Basic {self.client_secret}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as response:
                token = await response.text()

        return json.loads(token)

    async def ticket(self, server, room_id=None):

        if not room_id:
            pool = await DbConnector().setup()

            async with pool.acquire() as con:
                data = await con.fetchrow("""
                    SELECT ROOM_ID
                    FROM ARK_SERVERS
                    WHERE ARK_SERVER = $1
                    AND ROOM_ID <> 0
                """, server)

                await con.close()

            if data:
                room_id = data['room_id']
            else:
                raise Exception()

        url = f"{self.api_url}/rtc/v1/{self.deployment_id}/room/{room_id}"

        puid = await random_user()

        payload = {
            "participants": [
                {
                    "puid": f"{puid}",
                    "hardMuted": False
                }
            ]
        }

        token = await self.get_token()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token['access_token']}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(payload), headers=headers) as response:
                data = await response.text()

        data = json.loads(data)

        return data['clientBaseUrl'], data['participants'][0]['token'], puid

    async def players(self, server, room_id=None):

        try:
            uri, ticket, puid = await self.ticket(server, room_id)
        except IndexError as e:
            return [], server

        first_message = {
            "type": "join",
            "ticket": ticket,
            "user_token": puid,
            "options": [
                "subscribe",
                "dtx",
                "rtcp_rsize",
                "new_audio_only_reasons",
                "v2",
                "unified_plan",
                "speaking",
                "reserved_audio_streams"
            ],
            "version": "1.16.2-32273396",
            "device": {
                "os": "Windows",
                "model": "",
                "manufacturer": "",
                "online_platform_type": "0"
            }
        }

        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(first_message))
            response = await websocket.recv()
            await websocket.close()

            data = json.loads(response)

        users = []

        for user in data['users']:
            json_user = json.loads(user)

            users.append(json_user['user_token'])

        return users, server

    async def info(self, uids):
        url = self.api_url + "/user/v9/product-users/search"

        payload = {"productUserIds": uids}

        token = await self.get_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token['access_token']}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(payload), headers=headers) as response:
                data = await response.text()

        data = json.loads(data)

        pool = await DbConnector().setup()

        players_info = []

        async with pool.acquire() as con:
            for users in data['productUsers'].items():
                puid = users[0]

                for account in users[1]['accounts']:
                    data = await con.fetchrow("""
                        SELECT PUID
                        FROM PLAYERS
                        WHERE PUID = $1
                        AND ACCOUNT_ID = $2
                        AND PROVIDER = $3
                    """, puid, account['accountId'], account['identityProviderId'])

                    if not data:
                        await con.execute("""
                            INSERT INTO
                                PLAYERS (PUID, ACCOUNT_ID, PROVIDER)
                            VALUES
                                ($1, $2, $3);
                        """, puid, account['accountId'], account['identityProviderId'])

                    players_info.append({
                        "puid": puid,
                        "display_name": account['displayName'],
                        "account": account['accountId'],
                        "platform": account['identityProviderId']
                    })

            await con.close()

        return players_info

    async def matchmaking(self, server_number, official: bool = True, token=None):

        url = f"{self.api_url}/matchmaking/v1/{self.deployment_id}/filter"

        payload = {
            "criteria": [
                {
                    "key": "attributes.OFFICIALSERVER_s",
                    "op": "EQUAL",
                    "value": f"{1 if official else 0}"
                },
                {
                    "key": "attributes.CLUSTERID_s",
                    "op": "EQUAL",
                    "value": "PVPCrossplay"
                },
                {
                    "key": "attributes.CUSTOMSERVERNAME_s",
                    "op": "CONTAINS",
                    "value": f"{server_number}"
                }
            ],
            "maxResults": 2
        }

        if not token:
            token = await self.get_token()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token['access_token']}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(payload), headers=headers) as response:
                data = await response.text()

        data = json.loads(data)

        for session in data['sessions']:
            if 'ENABLEDMODSFILEIDS_s' not in session['attributes']:
                return session

        return []

    async def matchmaking_all(self):

        url = f"{self.api_url}/matchmaking/v1/{self.deployment_id}/filter"

        payload = {
            "criteria": [
                {
                    "key": "attributes.OFFICIALSERVER_s",
                    "op": "EQUAL",
                    "value": f"1"
                },
                {
                    "key": "attributes.CLUSTERID_s",
                    "op": "EQUAL",
                    "value": "PVPCrossplay"
                }
            ],
            "maxResults": 99999
        }

        token = await self.get_token()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token['access_token']}"
        }

        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, data=json.dumps(payload), headers=headers) as response:
                data = await response.text()

        data = json.loads(data)
        seen = []

        sessions = data['sessions']

        sessions.sort(key=lambda session: session['totalPlayers'], reverse=True)

        pool = await DbConnector().setup()

        local_dt = datetime.now()

        local_tz = timezone('Brazil/East')

        local_dt_with_tz = local_dt.astimezone(local_tz)

        utc_dt = local_dt_with_tz.astimezone(utc)

        epoch_time = utc_dt.timestamp()

        results = []

        for session in sessions:
            if session['id'] not in seen:
                results.append((
                    session['attributes']['CUSTOMSERVERNAME_s'][-4:],
                    session['totalPlayers'],
                    int(epoch_time)
                ))

            seen.append(session['id'])

        async with pool.acquire() as con:
            await con.executemany("""
                INSERT INTO server_history(
                ARK_SERVER, PLAYER_COUNT, TIME)
                VALUES ($1, $2, $3)
                ON CONFLICT (ARK_SERVER, TIME) DO NOTHING;
            """, results)

            await con.close()

    async def players_all(self):
        pool = await DbConnector().setup()

        async with pool.acquire() as con:
            data = await con.fetch("""
                SELECT ROOM_ID, ARK_SERVER
                    FROM ark_servers 
                WHERE ROOM_ID <> 0
            """)

            if data:
                results = await asyncio.gather(
                    *[self.players(server['ark_server'], server['room_id']) for server in data])
            else:
                return

            local_dt = datetime.now()

            local_tz = timezone('Brazil/East')

            local_dt_with_tz = local_dt.astimezone(local_tz)

            utc_dt = local_dt_with_tz.astimezone(utc)

            epoch_time = utc_dt.timestamp()

            upload = []

            for result in results:
                for player in result[0]:
                    upload.append((
                        player,
                        result[1],
                        epoch_time
                    ))

            await con.executemany("""
                INSERT INTO player_history(
                puid, ark_server, "time")
                VALUES ($1, $2, $3)
            """, upload)

            await con.close()
