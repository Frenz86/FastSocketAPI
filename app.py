import streamlit as st
import cv2
import websockets
import asyncio
import numpy as np

url = 'ws://127.0.0.1:8000/python_client'

st.title("Webcam Live Feed")
run = st.checkbox('Run')
FRAME_WINDOW = st.image([])
cap = cv2.VideoCapture(0)
from PIL import Image
FRAME_WINDOW2 = st.image([])


async def main(url):
    async with websockets.connect(url) as ws:
        while True:
            success, frame = cap.read()
            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if not success:
                break
            else:
                #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ret, buffer = cv2.imencode('.png', frame)
                arr = np.frombuffer(buffer[1], np.uint8)
                img2 = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
                img2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FRAME_WINDOW2.image(img2)
                await ws.send(buffer.tobytes())

# Start the connection
asyncio.run(main(url))

# https://stackoverflow.com/questions/72355067/streamlit-image-not-being-updated
#current_image = Image.open(io.BytesIO(base64.b64decode(json.loads(message)["image"])))  # until here it works fine, sample log is <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=1280x720 at 0x129D81FD0>
