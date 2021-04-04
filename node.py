from fastapi import FastAPI, Request, Response, Header
import requests

class Node():
    app = FastAPI()
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])
            self.listeners = []

    async def get_server_up(self):
        print('=========== START =========')
        config = Config(app=self.app, port=port, loop=loop, reload=True)
        await Server(config).serve()
    
    @app.get('/')
    def root():
        return 'Hello Root'

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

    async def broadcast_message(self, message):
        print("=========== Broadcasting ============")
        print(listeners, ' Listner to broadcast')
        async def broadcasting():
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

