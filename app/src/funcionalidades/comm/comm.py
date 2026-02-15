
#websocket + envio de arquivos temp a api para players terem os modelos fichas poderem renderizar o map etc
# (algo entre conectar salas+chat+interaão com mapa(dm tera coisas extras etc))
import asyncio
import websockets

clients = set()
#SE FOR DM/GM GERARA UM SOCKET PARA CRIAR O ID DA SALA E OUTRAS COISA
class server():
    global client
    port = 8765
    async def echo(websocket):
        async for message in websocket:
            await websocket.send(message)
    #toda acao mandada ao ws tera user:uid:act:cont(interação) ou u:uid:a:c
    async def clients_list(websocket):
        async for message in websocket:
            await websocket.send(message)
    #mostrar id
    def mostrar_id(port):
        return port

    #rodar websocket
    async def main(port):
        #func onde port
        server.port(8765)
        async with websockets.serve(server.echo, "localhost", 8765):
            await asyncio.Future() # Run forever

#players
class client():
    #procurar websocket
    async def listen():
        #conecão com
        uri = "ws://localhost:8765"
        #mandar ao server.py
        async with websockets.connect(uri) as websocket:
            await websocket.send("Hello, World!")
            response = await websocket.recv()
            print(f"Received: {response}")

