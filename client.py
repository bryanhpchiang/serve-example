import time
import asyncio
import websockets
import json
import uuid


class WSClient:
    def __init__(self, uri):
        self.uri = uri
        self.pending = {}

    async def connect(self):
        self.connection = await websockets.connect(self.uri)
        self.consumer_task = asyncio.ensure_future(self.consumer_handler())

    async def disconnect(self):
        self.consumer_task.cancel()
        await self.connection.close()

    async def consumer_handler(self):
        async for message in self.connection:
            data = json.loads(message)
            if 'id' in data:
                if data['id'] in self.pending:
                    print("Took {} seconds for request {} to be fulfilled.".format(
                        time.time() - data["start"], data["id"]))
                    self.pending[data['id']].set_result(data)

    async def send_and_receive_websocket(self, message):
        request_id = str(uuid.uuid4())
        self.pending[request_id] = asyncio.Future()
        await self.connection.send(json.dumps({
            'id': request_id,
            'text': message,
            "start": time.time()
        }))
        return await self.pending[request_id]


async def main():
    client = WSClient('ws://localhost:8000')
    await client.connect()
    tasks = [client.send_and_receive_websocket(
        f'Warmup {i}') for i in range(10)]
    results = await asyncio.gather(*tasks)
    print(results)
    await client.disconnect()


asyncio.run(main())
