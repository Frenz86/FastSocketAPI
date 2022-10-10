from importlib.resources import contents
import websockets
import asyncio
import cv2
import numpy as np
import base64

url = 'ws://127.0.0.1:8000/python_client'
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

async def main(url):
    async with websockets.connect(url) as ws:
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.png', frame)
                await ws.send(buffer.tobytes())

# Start the connection
asyncio.run(main(url))




        