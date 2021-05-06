from mtcnn import MTCNN
from PIL import Image
import cv2
import math
import model_prediction
import frame_face_grab
import pafy

ds_factor=0.6

class Camera360(object):
    def __init__(self):
        #url = "https://youtu.be/ktp6N3krvk0"
        #video = pafy.new(url)
        #best = video.getbest(preftype="mp4")
        #self.video = cv2.VideoCapture(best.url) 
        self.video = cv2.VideoCapture(0)

    def update_cam(self):
        #url = "https://youtu.be/ktp6N3krvk0"
        #video = pafy.new(url)
        #best = video.getbest(preftype="mp4")
        #self.video = cv2.VideoCapture(best.url)
        self.video.release()
        self.video = cv2.VideoCapture(0)

    def get_frame(self):
        ret, frame = self.video.read() #프레임 가져오고

        #frame=cv2.resize(frame,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        #cv2.imshow("a",frame)
        #key=cv2.waitKey(1)    
        names = frame_face_grab.face_catcher(frame)
        
        #ret, jpeg = cv2.imencode('.jpg', frame)
        return names