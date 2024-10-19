from flask import Flask, send_file
import cv2
from pygrabber.dshow_graph import FilterGraph
import io
import threading
from PIL import Image

app = Flask(__name__)

image_data = None
lock = threading.Lock()

graph = FilterGraph()
devices = graph.get_input_devices()
camera_name = "RICOH THETA UVC"
camera_id = devices.index(camera_name) if camera_name in devices else 0

capture = cv2.VideoCapture(camera_id)
if not capture.isOpened():
    raise IOError("CAM DSCN")

def capture_frames():
    global image_data
    while True:
        ret, frame = capture.read()
        if ret:
            with lock:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img)
                img_io = io.BytesIO()
                pil_img.save(img_io, 'JPEG')
                img_io.seek(0)
                image_data = img_io
        else:
            print("SHT EROR")

@app.route('/capture')
def get_frame():
    global image_data
    with lock:
        if image_data is not None:
            return send_file(image_data, mimetype='image/jpeg')
        else:
            return "No image available", 503

if __name__ == "__main__":
    capture_thread = threading.Thread(target=capture_frames)
    capture_thread.daemon = True
    capture_thread.start()
    app.run(host='0.0.0.0', port=9091)
