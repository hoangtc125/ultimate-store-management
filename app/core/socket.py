# import socketio


# class Socket:

#     def __init__(self):
#         self.__sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
#         self.__asgi = socketio.ASGIApp(self.__sio)

#     async def send_data(self, channel: str, data: dict):
#         await self.__sio.emit(channel, data)
#         return

#     def __call__(self):
#         return self.__asgi


# socket_connection = Socket()
