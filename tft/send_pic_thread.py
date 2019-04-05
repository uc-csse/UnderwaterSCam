# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import serial,time
import ctypes,cv2
import threading

import signal
import sys

import zmq


keep_running = True
def signal_handler(sig, frame):
    global keep_running
    keep_running=False
    print('You pressed Ctrl+C!')
    time.sleep(1)
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

W=320
H=240
img_to_send=None

class Sender(threading.Thread):
    def run(self):
        global img_to_send
        S=24
        C=H//S #chunk to send
        lib = ctypes.CDLL('./rgb888_to_rgb565.so')
        lib.RGB888_to_RGB565.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int]
        oimg_buf=bytes(W*H*S*2)
        ser = serial.Serial('/dev/ttyUSB-LCD',3000000)  # open serial port
        while keep_running:
            if img_to_send is None:
                time.sleep(0.001)
                continue
            img=img_to_send
            img_to_send=None
            img_buf=img.tobytes()
            lib.RGB888_to_RGB565(img_buf,oimg_buf,W*H)
            for i in range(S):
                ser.write(bytes([0xa5,0xa5,i]))
                ser.write(oimg_buf[W*C*2*i:W*C*2*(i+1)])     # write a string
                time.sleep(0.015)

def init():
    Sender().start()

def write(img):
    global keep_running
    if img.shape[0]==H and img.shape[1]==W:
        global img_to_send
        img_to_send=img
    else:
        print('Error in send_pic_thread: imgae size has to be: (',W,H,') given:',img.shape)
        keep_running = False
        sys.exit(-1)


context = zmq.Context()
stereo_sock = context.socket(zmq.SUB)
stereo_sock.connect("tcp://localhost:5556")
stereo_sock.setsockopt_string(zmq.SUBSCRIBE, "status")
stereo_sock.setsockopt(zmq.CONFLATE, 1)
recording = False

def update_status():
    global recording
    global keep_running
    while keep_running:
        try:
            status = stereo_sock.recv_string()
            recording = True if int(status.split(":")[1]) == 1 else False
        except zmq.ZMQError as e:
            print(e)
            break


if __name__=='__main__':
    import shutil

    img1=cv2.resize(cv2.imread('./left.png'),(W,H))
    img2=cv2.resize(cv2.imread('./right.png'),(W,H))
    init()

    threading.Thread(target=update_status).start()

    while 1:


        fb = img1.copy()
        cv2.putText(fb,"192.168.X.X",(5,20),1,1,(0,0,255));
        col = (0,0,255) if recording else (255,255,255)

        total, used, free = shutil.disk_usage(".")
        cv2.putText(fb,"%0.1f GB"% (free / (2**30)),(5,220),1,2,(0,0,0),5);
        cv2.putText(fb,"%0.1f GB"% (free / (2**30)),(5,220),1,2,col,2);

        write(fb)
        img1,img2=img2,img1
        time.sleep(2)
        print('----',time.time())
