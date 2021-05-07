from mtcnn import MTCNN
from keras.models import Model, load_model
from PIL import Image
import cv2
import math
import numpy as np
import model_prediction
from collections import deque

'''여기서는 임의의 이미지를 사용하지만
실제로 사용될 이미지는 실시간이든 비디오든, 어떤 프레임임'''

detector = MTCNN()
targetX, targetY = 100, 100
categories = model_prediction.categories # 학생 명단 // model_prediction.py에 정의된 것 이용

# 입 모양 및 발화 상태 파악을 위한 모델과 빈 딕셔너리
IMG_SIZE = (34, 26)  # 입 이미지의 가로, 세로 사이즈
mouth_model = load_model('mouth_models/2021_04_02_01_57_41.h5')
class_participants = {}
check_list = {categories[0]:deque('x'*10, maxlen=10), categories[1]: deque('x'*10, maxlen=10), categories[2]: deque('x'*10, maxlen=10), categories[3]:deque('x'*10, maxlen=10), categories[4]:deque('x'*10, maxlen=10)}

# # 입 개폐 여부 파악 함수
# def check_mouth(face, face_info, name):
#     box = face_info['box']
#     keypoints = face_info['keypoints']
#     nose_x, nose_y = keypoints['nose'][0], keypoints['nose'][1]
#     lm_x, lm_y = keypoints['mouth_left'][0], keypoints['mouth_left'][1]
#     rm_x, rm_y = keypoints['mouth_right'][0], keypoints['mouth_right'][1]

#     mouth = face[nose_y + 3: box[1] + box[3], lm_x: rm_x]

#     mouth_rect = [(lm_x, nose_y + 6), (rm_x, box[1] + box[3])]

#     try:
#         mouth = cv2.resize(mouth, dsize=(34, 26))

#         face = cv2.rectangle(
#             face, mouth_rect[0], mouth_rect[1], (255, 0, 0), 1)  # 입주변 박스 그리기

#         mouth = cv2.cvtColor(mouth, cv2.COLOR_BGR2GRAY)  # 입 사진 gray로 변경
#         mouth_input = mouth.copy().reshape(
#             (1, IMG_SIZE[1], IMG_SIZE[0], 1)).astype(np.float32) / 255
#         pred = mouth_model.predict(mouth_input)

#         pred = pred[0][0]

#         if name is not 'UNKNOWN':
#             if pred > 0.5:
#                 class_participants[name].append('o')
#             else:
#                 class_participants[name].append('x')

#             state = 'O %.1f' if pred > 0.5 else '- %.1f'
#             state = state % pred

#             if class_participants[name].count('o') > class_participants[name].count('x'):
#                 cv2.putText(face, 'speaker', (mouth_rect[0][0] + int((mouth_rect[1][0] - mouth_rect[0][0]) / 4),
#                                              mouth_rect[0][1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

#             else:
#                 cv2.putText(face, state, (mouth_rect[0][0] + int((mouth_rect[1][0] - mouth_rect[0][0]) / 4),
#                                          mouth_rect[0][1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
  
#         return face

#     except Exception as e:
#         print(e)
#         print('cannot detect ' + name + '\'s mouth')
#         return None

def square_face(img, box_x, box_y, box_width, box_height):
    try:
        face_center_x = box_x + int(1/2 * box_width)
        face_center_y = box_y + int(1/2 * box_height)
        a = int(1/2 * box_width) if box_width > box_height else int(1/2 * box_height)
        # 최대한 얼굴 형태 유지하며 정방형으로 잘라냄
        face = img[face_center_y - a : face_center_y + a, face_center_x - a : face_center_x + a]
        # 얼굴 (100, 100)로 만듦
        face = cv2.resize(face, dsize=(targetX, targetY))

        return face

    except:
        return None

def face_catcher(img): # 한 img에서 얼굴과 그 얼굴의 신원을 파악하는 코드
    name_list = {categories[0]:'x', categories[1]: 'x', categories[2]: 'x', categories[3]:'x', categories[4]:'x'}
    face_infos = detector.detect_faces(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    #print(len(face_infos)) # 발견된 얼굴의 수
    
    for face_info in face_infos:
        box = face_info['box']
        box_x, box_y = box[0], box[1]
        box_width, box_heigth = box[2], box[3]
        
        # 얼굴 중심을 기준으로 정방형으로 얼굴 추출
        face = square_face(img, box_x, box_y, box_width, box_heigth)

        if face is None:
            continue # 얼굴이 아닌 경우에는 그냥 지나침

        # 모델을 이용한 신원 파악 및 정확도
        # MTCNN이나 Keras에서는 이미지를 PILLOW로 처리하는데, 현재 코드는
        # OpenCV 즉, ndarray 이용하므로 채널과 자료형 변환
        name, acc = model_prediction.predict_by_model(Image.fromarray(
            cv2.cvtColor(face, cv2.COLOR_BGR2RGB)), categories)

        # 처음 등장한 신원에 대해서 입 상태 배열(뎈) 초기화
        if class_participants.get(name, None) == None:
                        class_participants[name] = deque(
                            'x' * 15, maxlen=15)

        # # 얼굴에 바운더리 박스 그리기
        # img = cv2.rectangle(img, (box_x, box_y), (box_x + box_width, box_y + box_heigth), (255, 0, 0), 1)
        # # 박스 위에 이름과 정확도 출력하기
        # img = cv2.putText(
        #                 img, name + ' '+str(acc), (box_x, box_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        #name_list[name]='o' # 발화자가 아니라, {'jinho':'x', 'jahyeon' :'o'}
        #정확도 60이상시에 이사람이 맞다라고 체크
        if acc>60:
            name_list[name]='o'

       
                                    
        
        print(name, acc) # 이미지에서 현재 파악하고 있는 얼굴의 신원과 정확도 반환

        # if check_mouth(img, face_info, name) is None: # 입 개폐 상태를 파악하지 못한 경우
        #     continue
    #실제 출석여부를 반환할 list를 수정
    #현재 프레임에서 몇명이 인식됐는지 리스트가 수정됨.
    #덱에 현재 인식여부를 추가함
    #그 추가된 후에 개수를 파악해서 조건을 만족하면 출석과 비출석을 정해서 최종 리턴
    for name in name_list.keys():
        # if name_list[name]=='o':
        #     check_list[name].append(name_list[name])
        # else:
        #     check_list[name].appendleft(name_list[name])
        check_list[name].append(name_list[name])
        if check_list[name].count('o')>=6:
            name_list[name]='o'
        else:
            name_list[name]='x'
    

    return name_list



if __name__ == '__main__':
    img = cv2.imread('3men.jpg')
    detector = MTCNN()
    face_catcher(img)