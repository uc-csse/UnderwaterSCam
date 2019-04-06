#!/usr/bin/env python
from flask import Flask, render_template, Response
#from camera import Camera
import time
import zmq
import numpy as np
import cv2

context = zmq.Context()
left_sock = context.socket(zmq.SUB)
left_sock.connect("tcp://localhost:5556")
left_sock.setsockopt_string(zmq.SUBSCRIBE, "l")

right_sock = context.socket(zmq.SUB)
right_sock.connect("tcp://localhost:5556")
right_sock.setsockopt_string(zmq.SUBSCRIBE, "r")


app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

def left_stream_full():
	count =0
	while True:
		print(count)
		data = left_sock.recv()[1:]
		if count%10==0:
			yield (b'--frame\r\n'
					b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
		count += 1

def left_stream_small():
	count =0
	while True:
		data = left_sock.recv()[1:]
		data = np.fromstring(data,np.uint8)
		img = cv2.imdecode(data, 1)
		img = cv2.resize(img, (640,480))
		data = cv2.imencode(".jpg",img )[1].tostring()
		if count%2==0:
			yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
		count += 1

def right_stream_full():
	count =0
	while True:
		data = right_sock.recv()[1:]
		if count%10==0:
			yield (b'--frame\r\n'
					b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
		count += 1

def right_stream_small():
	count =0
	while True:
		data = right_sock.recv()[1:]
		data = np.fromstring(data,np.uint8)
		img = cv2.imdecode(data, 1)
		img = cv2.resize(img, (640,480))
		data = cv2.imencode(".jpg",img )[1].tostring()
		if count%2==0:
			yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
		count += 1

@app.route('/video_left')
def video_left():
	return Response(left_stream_small(),
					mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_right')
def video_right():
	return Response(right_stream_small(),
					mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_left_full')
def video_left_full():
	return Response(left_stream_full(),
					mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_right_full')
def video_right_full():
	return Response(right_stream_full(),
					mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
