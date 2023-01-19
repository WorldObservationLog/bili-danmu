import asyncio
from dataclasses import dataclass
from typing import Dict, Callable, Awaitable
import websockets
import json
import brotli
from .pack import Pack, RawDanmu, WSConstants


class DanmuClient:
    roomId: int
    ws: websockets.WebSocketClientProtocol
    _handler: Dict[int, Callable[[dict | RawDanmu], Awaitable[None]]] ={}
    api = "wss://broadcastlv.chat.bilibili.com:443/sub"
    heartbeat = 30.0

    def __init__(self, roomId: int):
        self._handler[WSConstants.WS_OP_MESSAGE] = self.default_handler
        self._handler[WSConstants.WS_OP_HEARTBEAT_REPLY] = self.default_handler
        self._handler[0] = self.default_handler

        self.roomId = roomId
        self.heartbeat_pack = Pack.pack_string("", WSConstants.WS_OP_HEARTBEAT)

    async def send_auth(self):
        auth_params = {"uid": 1, "roomid": self.roomId, 
                       "protover": 3, "platform": "web", "clientver": "1.7.3"}
        return await self.ws.send(Pack.pack_string(json.dumps(auth_params), WSConstants.WS_OP_USER_AUTHENTICATION))
    
    async def send_heartbeat(self):
       return await self.ws.send(self.heartbeat_pack)

    async def handle_packs(self, packs: bytes):
        if not packs:
            return None
        header = Pack.unpack_header(packs)
        body = packs[header.headerLength:]
        if header.protocolVersion == 3 and header.operation == WSConstants.WS_OP_MESSAGE:
           packs = brotli.decompress(body)
           for raw in Pack.unpack_string(packs):
                await self.parse_body(raw)
        else: 
            if len(packs) == header.packLength:
                await self.parse_body(RawDanmu(header=header, body=body))

    async def parse_body(self, rawDanmu: RawDanmu):
        opt = rawDanmu.header.operation
        if opt == WSConstants.WS_OP_MESSAGE:
            await self._handler[WSConstants.WS_OP_MESSAGE](json.loads(rawDanmu.body.decode("utf-8")))
        elif opt == WSConstants.WS_OP_HEARTBEAT_REPLY:
            await self._handler[WSConstants.WS_OP_HEARTBEAT_REPLY](rawDanmu)
        else:
            await self._handler[0](rawDanmu)
    
    async def default_handler(self, danmu: dict | RawDanmu) -> None:
        pass

    def on_danmu(self, fn: Callable[[dict], Awaitable[None]]):
        self._handler[WSConstants.WS_OP_MESSAGE] = fn
        return fn

    def on_unknown(self, fn: Callable[[RawDanmu], Awaitable[None]]):
        self._handler[0] = fn
        return fn

    def on_heartbeat(self, fn: Callable[[RawDanmu], Awaitable[None]]):
        # watching_num = struct.unpack("!I", rawDanmu.body)
        self._handler[WSConstants.WS_OP_HEARTBEAT_REPLY] = fn
        return fn

    async def job_send_heartbeat(self):
        try:
            while True:
                await self.send_heartbeat()
                await asyncio.sleep(self.heartbeat)
        except asyncio.CancelledError:
            return

    def run(self, loop: asyncio.AbstractEventLoop, block: bool = True):
        async def init_client():
            self.ws = await websockets.connect(self.api, ssl=True)
        loop.run_until_complete(init_client())
        loop.run_until_complete(self.send_auth())
        loop.create_task(self.job_send_heartbeat())
        async def receive_packs():
            async for packs in self.ws:
                try:
                    await self.handle_packs(packs)
                except websockets.ConnectionClosed:
                    continue
        if block:
            loop.run_until_complete(receive_packs())
        else:
            loop.create_task(receive_packs())
