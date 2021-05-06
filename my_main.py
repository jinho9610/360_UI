from flask import Flask, render_template, Response
from camera import VideoCamera
from camera_360 import Camera360
import time
import json
import frame_face_grab

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/virtualSpatial')
def virtual():
    return render_template('webGL.html')

@app.route('/realSpatial')
def real():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feeding():
    return Response(gen(Camera360()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_info_streaming')
def video_feed():
    new_cam = Camera360()
    attendance_status = {}
    def generate_info():
        i = 0
        while True:
            i += 1
            #time.sleep(1)
            names = new_cam.get_frame()
            print(i % 20, names)
            if i%20==0:
                time.sleep(5)
                new_cam.update_cam() 
            json_data = json.dumps(names)
            yield f"data:{json_data}\n\n"
    return Response(generate_info(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True)


# from flask import Flask, render_template, Response
# from camera import VideoCamera
# from camera_360 import Camera360
# from collections import deque
# import time
# import json

# app = Flask(__name__)

# @app.route('/')
# def main():
#     return render_template('index.html')

# @app.route('/virtualSpatial')
# def virtual():
#     return render_template('webGL.html')

# @app.route('/realSpatial')
# def real():
#     return render_template('index.html')

# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# @app.route('/video_feed')
# def video_feeding():
#     return Response(gen(Camera360()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/video_info_streaming')
# def video_feed():
#     attendance_checker = {}
#     attendance_cur_stat = {}
#     new_cam = Camera360()
#     def generate_info():
#         i = 0
#         while True:
#             i += 1
#             time.sleep(1)
#             names = new_cam.get_frame()

#             #가장 첫 프레임의 경우
#             if i == 1:
#                 for name in names.keys():
#                     if attendance_cur_stat.get(name, None) == None:
#                         attendance_cur_stat[name] = deque(
#                             'x' * 20, maxlen=20)
#                     if attendance_checker.get(name, None) == None:
#                         attendance_checker[name]='x'
            
#             for name in names.keys():
#                 attendance_cur_stat[name].append(names[name])
#                 if attendance_cur_stat[name].count('o') > 10:
#                     attendance_checker[name] = 'oo'
#                 else:
#                     attendance_checker[name] = 'xx'

#             print(i % 20)
#             print(attendance_cur_stat)
#             print(attendance_checker)
#             print()
            
#             if i % 20 == 0:
#                 json_data = json.dumps(attendance_checker)
#                 yield f"data:{json_data}\n\n"

#     return Response(generate_info(), mimetype="text/event-stream")

# if __name__ == '__main__':
#     app.run()