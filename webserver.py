#!/usr/bin/env python
from flask import Flask, render_template, Response
#from camera import Camera
import time

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

def gen():
	count = 1
	while True:
		#frame = camera.get_frame()
		with open("demo_images/%d.jpg"%count, "rb") as frame:
			count += 1
			if count > 4: count = 1
			time.sleep(1/10)
			yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame.read() + b'\r\n')

@app.route('/video_feed')
def video_feed():
	return Response(gen(),
					mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
