from discord.ext import commands

from .objects import Track, Playlist
from .websocket import WebSocket


class Node:
    def __init__(
        self,
        host: str,
        port: int,
        user_id: int,
        *,
        client,
        session,
        rest_uri: str,
        password,
        identifier,
    ):
        self.rest_uri = rest_uri
        self.host = host
        self.port = port
        self.user_id = user_id
        self.identifier = identifier
        self.password = password

        self._client = client
        self.session = session

        self.players = {}

        self._websocket = None

        self.available = True

    def __repr__(self):
        p_count = len(self.players.keys())
        return f"<GraniteNode player_count={p_count} available={self.available}>"

    def __str__(self):
        return self.identifier

    async def connect(self, bot: commands.Bot):
        self._websocket = WebSocket(
            bot, self.host, self.port, self.password, self
        ) # git please help me
        await self._websocket._connect()

    async def get_tracks(self, query: str):
        password = "null" if not self.password else self.password

        async with self.session.get(
            f"{self.rest_uri}/loadtracks", params = dict(identifier = query),
            headers={"Authorization": password},
        ) as response:
            data = await response.json()

        if not data['tracks']:
            return None

        if data['loadType'] == 'PLAYLIST_LOADED':
            return Playlist(data = data)

        tracks = []
        for track in data["tracks"]:
            tracks.append(Track(_id=track["track"], data=track["info"]))

        return tracks
