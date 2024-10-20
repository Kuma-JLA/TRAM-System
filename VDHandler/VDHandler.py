import io
import time
import threading
from flask import Flask, send_file, jsonify
import mss
import mss.tools
from PIL import Image

app = Flask(__name__)

image_data = None

def get_second_display_area():
    with mss.mss() as sct:
        monitor_number = 2
        mon = sct.monitors[monitor_number]
        monitor = {
            "top": int(mon["top"] + (mon["height"] * 0.095)),
            "left": int(mon["left"] + (mon["width"] * 0.05)),
            "width": int(mon["width"] * 0.44),
            "height": int(mon["height"] * 0.7),
            "mon": monitor_number
        }
        return monitor

def capture_screenshot():
    global image_data
    capture_area = get_second_display_area()
    with mss.mss() as sct:
        while True:
            screenshot = sct.grab(capture_area)
            img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            image_data = img_io.getvalue()
            time.sleep(0.5)

@app.route('/capture')
def get_image():
    if image_data:
        return send_file(io.BytesIO(image_data), mimetype='image/png')
    return jsonify({"error": "No image available"}), 500
capture_thread = threading.Thread(target=capture_screenshot)
capture_thread.daemon = True
capture_thread.start()

if __name__ == '__main__':
    port = 9092
    app.run(debug=True, port=port)
