#!env/bin/python

# The client will run my local machine:
# $ client.py 1.23.45.6:7000
# Attaching to remote...
# Attached!
# >
# The server will run on my remote machine.
# > server.py
# Starting server on ip 1.23.45.6:7000

from typing import Optional, List

from fastapi import Depends, FastAPI, HTTPException, Request, Response, Header, APIRouter
from pydantic import BaseModel, HttpUrl
import json
import requests
from uvicorn import Config, Server
import time
import asyncio
import aiohttp

from requests.api import request

auth_token = "eyJhbGciOiJIUzI1NiIsInRc5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1ZmIzZjljOTU1MWQ2ZjYxYWExZjUzYmUiLCJlbWFpbCI6ImFsZXhAdGVzdC5jb20iLCJpc0FkbWluIjp0cnVlLCJpYXQiOjE2MTU2MTUyMDEsImV4cCI6MTYxODIwNzIwMX0.los-irC1kdNfSb_sVS9PSORKLXzJa8Anqjbkk_lravc"

class Listener:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def baseURL(self):
        return f'http://{self.ip}:{self.port}'


class Node():
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


def get_node(loop, auth_token, port, on_message):
    _n = FastAPI()
    listeners = []

    async def get_server_up():
        print('=========== START =========')
        config = Config(app=_n, port=port, loop=loop, reload=True)
        await Server(config).serve()

    def is_auth(request):
        headers = request.headers
        authorization = headers['authorization'].split(' ')[1] if 'authorization' in headers else ''
        host = headers['host']
        return authorization == auth_token

    def attach_to(ip, port, auth_token):
        print('Attaching to remote...')
        listener = Listener(ip, port)
        listeners.append(listener.baseURL())
        print('listener: {}'.format(listener))	

    async def broadcast_message(message):
        print("=========== Broadcasting ============")
        print(listeners, ' Listner to broadcast')
        async def broadcasting():
            await asyncio.sleep(1)
            for listener in listeners:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f'{listener}/message') as response:
                        print(response, ' broadcast to')
            await asyncio.sleep(0.1)
        await broadcasting()

    @_n.get('/')
    def on_read():
        return 'hello'

    @_n.get('/attach')
    async def on_attach(request: Request):
        address = request.client
        ip, port = address[0], address[1]
        # ip = request.host.ip  # TODO check this
        # port = request.host.port  # and this
        if is_auth(request):
            listener = Listener(ip, port)
            if listener.baseURL() not in listeners:
                listeners.append(listener.baseURL())
            print('listeners: {}'.format(listeners))
            return {"message": "Attached to Remote!"}
        return {"message": "Invalid auth"}

    @_n.post("/message")
    async def on_message(request: Request):
        if is_auth(request):
            r_data = await request.json()
            print('message received: {}'.format(r_data))
            return {"message": "Delivered"}
        return {"message": "Invalid auth"}

    return Node(
        is_auth = is_auth,
        attach_to = attach_to,
        get_server_up = get_server_up,
        broadcast_message = broadcast_message
    )


def main():
    loop = asyncio.get_event_loop()
    def on_message_from_server(message):
        print(f'Client got message from server: {message}')

    def on_message_from_client(message):
        print(f'Server got message from client: {message}')


    server = get_node(loop, auth_token, 8001, on_message_from_client)
    client = get_node(loop, auth_token, 8002, on_message_from_server)

    s = asyncio.gather(*[server.get_server_up()])
    c = asyncio.gather(*[client.get_server_up()])
    m = asyncio.gather(*[client.broadcast_message('message from client')])

    client.attach_to('127.0.0.1', '8001', auth_token)
    server.attach_to('127.0.0.1', '8002', auth_token)

    
    loop.run_until_complete(asyncio.gather(s, c, m))


if __name__ == '__main__':
    try:
        main()
    finally:
        pass
