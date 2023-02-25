# bili-danmu

A modern library for receiving danmu from bilibili livestream, with full asynchronous support.

NOTICE: It's a simple implement, so IT DOES NOT INCLUDE PARSEING DANMU FEATURES. You need to parse the danmu dict mannually.

# Installation

Just execute `pip install bili-danmu`

# Example

```python
import asyncio
from danmu import DanmuClient

loop = asyncio.new_event_loop()
dmc = DanmuClient(25512465)

@dmc.on_danmu
async def on_danmu(room_id: int, danmu: dict):
    print(danmu)

dmc.run(loop)
loop.run_forever()
```

# Special Thanks

This project refers to some other projects. Sincerely appreciate their developers.

- [Code4Epoch/Bolaris](https://github.com/Code4Epoch/Bolaris) Give me the infomation of v3 protocol

- [qydysky/bili_danmu](https://github.com/qydysky/bili_danmu) A full list of CMD in danmu pack's body

- [littlecodersh/danmu](https://github.com/littlecodersh/danmu) A very old danmu library. Inspire me to use callback design

- [yjqiang/danmu](https://github.com/yjqiang/danmu) Main reference 

- [yangjunlong/barrager.js](https://github.com/yangjunlong/barrager.js) A protocol document and code implement
