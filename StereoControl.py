import PySpin
import time
import config
import cv2
import threading
import os
import zmq

RECORDING = False

def logError(message):
    print("Error:",message)

class ImageEventHandler(PySpin.ImageEvent):

    def __init__(self, camera):
        super(ImageEventHandler, self).__init__()
        self.device_serial_number = int(camera.DeviceSerialNumber())
        self.count = 0
        self.last_frame_time = time.time()
        self.bayer_data = b""
        self.colour_data = b""
        self.width = 0;
        self.height = 0;
        print("Handler attached to camera: %d" %self.device_serial_number)
        del camera


    def OnImageEvent(self, image):
        try:
            self.count += 1
            self.last_frame_time = time.time()
            if image.IsIncomplete():
                #print('Image incomplete with image status %d...' % image.GetImageStatus())
                pass
            else:
                #print("%d got image %d" %(self.device_serial_number,self.count))
                width = image.GetWidth()
                height = image.GetHeight()

                image_converted = image.Convert(PySpin.PixelFormat_BGR8, PySpin.HQ_LINEAR)
                self.colour_data = image_converted.GetData().reshape((height,width,3))
                self.bayer_data = image.GetData().reshape((height,width))
                self.width = width
                self.height = height

        except PySpin.SpinnakerException as ex:
            print('Spin Error: %s' % ex)
        except BaseException as ex:
            print('Error: %s' % ex)

def initialiseCamera(camera):
    camera.Init()

    image_event_handler = ImageEventHandler(camera)
    camera.RegisterEvent(image_event_handler)

    #camera.AcquisitionFrameRateEnable.SetValue(True)
    #camera.AcquisitionFrameRate.SetValue(5)
    #camera.DeviceLinkThroughputLimit.SetValue(50*1024*1024)

    camera.TriggerMode.SetValue(PySpin.TriggerMode_Off)
    camera.TriggerSource.SetValue(PySpin.TriggerSource_Line2)
    camera.TriggerMode.SetValue(PySpin.TriggerMode_On)

    camera.AcquisitionMode.SetValue(
        camera.AcquisitionMode.GetEntryByName('Continuous').GetValue())
    print('Acquisition mode set to continuous...')


    return image_event_handler


def save_jpgs(left_handler, right_handler, directory):
    next_capture_time = time.time();
    while True:
        timestamp = time.time()
        if left_handler.width != 0 and right_handler.width != 0 and RECORDING:
            imgname = directory+'{}-left.{}'\
                .format(timestamp,'jpg')
            cv2.imwrite(imgname,left_handler.colour_data)

            imgname = directory+'{}-right.{}'\
                .format(timestamp,'jpg')
            cv2.imwrite(imgname,right_handler.colour_data)

            next_capture_time = next_capture_time + 1.0/config.jpg_save_rate
            sleep_time = next_capture_time - time.time()
            if sleep_time > 0:
                time.sleep(next_capture_time - time.time())
        else:
            time.sleep(0.1)
            next_capture_time = time.time()

def save_pgm(left_handler, right_handler, directory):
    next_capture_time = time.time();
    while True:
        timestamp = time.time()
        if left_handler.width != 0 and right_handler.width != 0 and RECORDING:
            imgname = directory+'{}-left.{}'\
                .format(timestamp,'pgm')
            cv2.imwrite(imgname,left_handler.bayer_data)

            imgname = directory+'{}-right.{}'\
                .format(timestamp,'pgm')
            cv2.imwrite(imgname,right_handler.bayer_data)

            next_capture_time = next_capture_time + 1.0/config.pgm_save_rate
            sleep_time = next_capture_time - time.time()
            if sleep_time > 0:
                time.sleep(next_capture_time - time.time())
        else:
            time.sleep(0.1)
            next_capture_time = time.time()

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%d"%config.stereo_port)

def main ():
    system = PySpin.System.GetInstance()

    cams = system.GetCameras()

    if cams.GetSize() != 2:
        logError("Failed to connect to both cameras")
        return 0;

    handlers = dict()
    for camera in cams:
        handler = initialiseCamera(camera)
        handlers[camera.DeviceSerialNumber()] = handler
        print(camera.DeviceSerialNumber())

    print("Begining image acquisition...")
    for camera in cams:
        camera.BeginAcquisition()


    scan_name = time.strftime("%y-%m-%d-%H-%M",time.localtime())
    scan_dir = "/home/stereo/data/"+scan_name+"/"
    jpg_dir = scan_dir+"jpg/"
    pgm_dir = scan_dir+"pgm/"
    try:
        os.mkdir(scan_dir)
        os.mkdir(jpg_dir)
        os.mkdir(pgm_dir)
    except:
        pass



    jpg_thread = threading.Thread(target=save_jpgs,
        args=(handlers[config.left_camera["serial"]],
            handlers[config.right_camera["serial"]],
            jpg_dir))
    jpg_thread.start()

    pgm_thread = threading.Thread(target=save_pgm,
        args=(handlers[config.left_camera["serial"]],
            handlers[config.right_camera["serial"]],
            pgm_dir))
    pgm_thread.start()

    while True:
        if len(handlers[config.left_camera["serial"]].colour_data) > 0:
            r, buff = cv2.imencode(".jpg", handlers[config.left_camera["serial"]].colour_data )
            socket.send(b"l"+buff.tostring())

        if len(handlers[config.right_camera["serial"]].colour_data) > 0:
            r, buff = cv2.imencode(".jpg", handlers[config.right_camera["serial"]].colour_data )
            socket.send(b"r"+buff.tostring())

        socket.send_string("s%d" %(1 if RECORDING else 0))
        time.sleep(0.1)
    jpg_thread.join()
    pgm_thread.join()

    print("Ending image acquisition")
    for camera in cams:
        camera.EndAcquisition()
        camera.UnregisterEvent(handlers[camera.DeviceSerialNumber()])
        camera.DeInit()
        del camera

    cams.Clear()
    system.ReleaseInstance()


main()
