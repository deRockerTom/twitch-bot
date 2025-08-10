# ws_server.py
import asyncio
import logging
from typing import Set

import websockets
from config import WEBSOCKETS_SERVER_SETTINGS

from shared import DatabaseClient, Message

LOGGER = logging.getLogger("WebSocketServer")
logging.basicConfig(level=logging.INFO)

# Set of connected clients
connected_clients: Set[websockets.ServerConnection] = set()


# Function to handle each client connection
async def ws_handler(websocket: websockets.ServerConnection):
    connected_clients.add(websocket)
    try:
        async for _ in websocket:
            pass
    finally:
        connected_clients.remove(websocket)


async def start_ws_server():
    LOGGER.info("Starting websocket server...")
    server = await websockets.serve(ws_handler, "0.0.0.0", 8081)
    LOGGER.info("WebSocket server running at ws://localhost:8081/")
    await server.wait_closed()


async def watch_db():
    client = DatabaseClient(
        database_name=WEBSOCKETS_SERVER_SETTINGS.MONGO__DB,
        host=WEBSOCKETS_SERVER_SETTINGS.MONGO__HOST,
        port=WEBSOCKETS_SERVER_SETTINGS.MONGO__PORT,
    )
    coll = client.messages._collection
    async with await coll.watch() as stream:
        async for change in stream:
            if change["operationType"] == "insert":
                doc = change["fullDocument"]
                msg = Message(
                    login=doc["login"],
                    message=doc["message"],
                    user_id=doc["user_id"],
                    timestamp=doc["timestamp"],
                )
                LOGGER.info("Sending message: %s", msg)
                await asyncio.gather(*[ws.send(msg.model_dump_json()) for ws in connected_clients])


# Main function to start the WebSocket server
async def main():
    await asyncio.gather(start_ws_server(), watch_db())


# Run the server
if __name__ == "__main__":
    asyncio.run(main())
