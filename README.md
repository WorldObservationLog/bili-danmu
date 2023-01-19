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
async def on_danmu(danmu: dict):
    print(danmu)

dmc.run(loop)
```
