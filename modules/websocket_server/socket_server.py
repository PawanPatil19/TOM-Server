import asyncio
import websockets
from queue import Queue
import traceback
import sys
import threading

SERVER_IP = ""
SERVER_PORT = 8090

_CONNECTIONS = set()
_rx_queue = Queue()

# references: https://websockets.readthedocs.io/en/stable/reference/server.html , https://pypi.org/project/websockets/ 
async def ws_echo(websocket):
    global _rx_queue

    _CONNECTIONS.add(websocket)
    try:
        async for rx_data in websocket:
            _rx_queue.put_nowait(rx_data)
            print(f'Received data: {rx_data}')

    except Exception:
        traceback.print_exc(file=sys.stdout)
    finally:
        _CONNECTIONS.remove(websocket)


# Broadcast message to all websocket clients. 
def broadcastmsg(msg):
    websockets.broadcast(_CONNECTIONS, msg)


async def ws_main():
    async with websockets.serve(ws_echo, SERVER_IP, SERVER_PORT):
        await asyncio.Future()  # run forever


async def main():
    websocket_task = asyncio.create_task(ws_main())
    await asyncio.gather(
        websocket_task
    )


def start_server():
    asyncio.run(main())

def stop_server():
    pass
    

async def send_data_to_websockets(data):
    for _websocket in _CONNECTIONS:
        await _websocket.send(data)
    print(f'Sent data: {data}')


def send_data(data):
    asyncio.run(send_data_to_websockets(data))


def receive_data():
    global _rx_queue

    if _rx_queue.empty():
        return None

    print(f'rx_size: {_rx_queue.qsize()}')

    return _rx_queue.get_nowait()


server_thread = None

def start_server_threaded():
    global server_thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()


def stop_server_threaded():
    global server_thread
    stop_server()

    server_thread.join(timeout=2)