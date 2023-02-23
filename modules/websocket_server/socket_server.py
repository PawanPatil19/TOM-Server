import asyncio
import websockets
from queue import Queue
import traceback
import sys
import threading

SERVER_IP = ""
SERVER_PORT = 8080

CONNECTIONS = set()

tx_queue = Queue()
rx_queue = Queue()

# references: https://websockets.readthedocs.io/en/stable/reference/server.html , https://pypi.org/project/websockets/ 
async def ws_echo(websocket):
    global tx_queue, rx_queue

    CONNECTIONS.add(websocket)
    try:
        async for rx_data in websocket:
            rx_queue.put_nowait(rx_data)
            print(f'Received data: {rx_data}')

            if not tx_queue.empty():
                tx_data = tx_queue.get_nowait()
                await websocket.send(tx_data)
                print(f'Sent data: {tx_data}')
                del tx_data
    except Exception:
        traceback.print_exc(file=sys.stdout)
    finally:
        CONNECTIONS.remove(websocket)


# Broadcast message to all websocket clients. 
def broadcastmsg(msg):
    websockets.broadcast(CONNECTIONS, msg)


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
    
    
def send_data(data):
    global tx_queue

    print(f'tx_size: {tx_queue.qsize()}')
    tx_queue.put_nowait(data)


def receive_data():
    global rx_queue

    if rx_queue.empty():
        return None

    print(f'rx_size: {rx_queue.qsize()}')

    return rx_queue.get_nowait()


server_thread = None

def start_server_threaded():
    global server_thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()


def stop_server_threaded():
    global server_thread
    stop_server()

    server_thread.join(timeout=2)