import base64
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
import cv2
import numpy as np
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")


facecascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def drawboundingbox(img, boxes, rect_th=2):
   # img = fromat cv2
    for i in range(len(boxes)):
        img = cv2.rectangle(img,  (int(boxes[i][0]), int(boxes[i][1])),
                            (int(boxes[i][2]), int(boxes[i][3])),
                            color=(0,255,0), thickness=rect_th)
    return img

def detect_face_streamlit_api(image):
    # IMAGE MUST TO BE grayscale!!!!!!!!!!!!!!!
    imagegray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # load the face cascade detector,
    #facecascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # detect faces in the image
    facedetects = facecascade.detectMultiScale(imagegray, scaleFactor=1.1, minNeighbors=5,
        minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

    # construct a list of bounding boxes from the detection
    facerect = [(int(fx), int(fy), int(fx + fw), int(fy + fh)) for (fx, fy, fw, fh) in facedetects]
    # update the data dictionary with the faces detected
    data={}
    data.update({"num_faces": len(facerect), "faces": facerect, "success": True})
    # return the data dictionary as a JSON response
    return data

#########################################################################

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/python_client")
async def websocket_endpoint(websocket: WebSocket):
    # listen for connections
    await websocket.accept()
    #count = 1
    try:
        while True:
            contents = await websocket.receive_bytes()
            arr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)

            ##### modification
            frame = cv2.flip(frame, 1)
            ### HAAR CASCADE
            data_dict = detect_face_streamlit_api(frame)
            bb = drawboundingbox(frame, data_dict['faces'])
            frame = bb
            ###############################################
            
            cv2.imshow('frame', frame)
            cv2.waitKey(1)
            #cv2.imwrite("frame%d.png" % count, frame)
            #count += 1
    except WebSocketDisconnect:
        cv2.destroyWindow("frame")
        print("Client disconnected") 


## this will receive the camera from complete.html and send back in the same page but another frame the B&W result
@app.websocket("/complete")
async def get_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            frame = np.fromstring(base64.b64decode(data), dtype=np.uint8)
            frame = cv2.imdecode(frame, flags=cv2.IMREAD_COLOR)
            frame = cv2.flip(frame, 1)

            ### HAAR CASCADE
            data_dict = detect_face_streamlit_api(frame)
            bb = drawboundingbox(frame, data_dict['faces'])
            frame = bb
            ret, buffer = cv2.imencode('.jpg', frame)
            #await websocket.send_text("some text")
            await websocket.send_bytes(buffer.tobytes())
    except WebSocketDisconnect:
        await websocket.close()
        print("stop")

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
