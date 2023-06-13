print('\033[92m')

from utils.input import *
from utils.global_config import *
from utils.tools import *
from utils.constants import *
import cv2
import numpy as np
from threading import Thread

input_data = input_process()
if input_data[0] == '':
  exit('Not found any image or video.')
global_configs = Config(input_data=input_data)

summary(global_configs)

# import tracking model
RootTracking = None
if global_configs.is_tracking:
  from tracking.tracking import Tracking
  RootTracking = Tracking()
  RootTracking.load_yaml(
    fn_yaml=global_configs.fn_yaml,
    crop_fr_yaml=global_configs.crop_fr_yaml
  )

# import recognition model
RootRecognition = None
if global_configs.is_recognition:
  from recognition.recognition import Recognition
  RootRecognition = Recognition()

# import classification model
RootClassification = None
if global_configs.is_classification:
  from classification.classification import Classification
  RootClassification = Classification()
  RootClassification.load_model_resnet152()

def recognition_thread(images=[]):
  for lot in images:
    valid_car, space_id = '', ''
    if global_configs.is_tracking:
      valid_car = lot.split('/')[-1]
      space_id = valid_car.split('_')[0]
    if global_configs.is_tracking and valid_car.find('_T.') == -1:
      continue
    img = cv2.imread(lot) if global_configs.is_tracking else lot
    RootRecognition.set_data(img)
    # Detect license plate area by WPOD-Net
    _, lp_img, lp_type, detection_time = RootRecognition.detect_license_plate(img)
    # Recognize license plate by OCR
    lp_text, recognition_time = RootRecognition.recognize_by_easy_ocr()
    print(f'Space {space_id}, License plate: {lp_text}')
    # cv2.imshow('License plate', lp_img)
    # cv2.waitKey()

def classification_thread(images=[]):
  for lot in images:
    valid_car, space_id = '', ''
    if global_configs.is_tracking:
      valid_car = lot.split('/')[-1]
      space_id = valid_car.split('_')[0]
    if global_configs.is_tracking and valid_car.find('_T.') == -1:
      continue
    img = cv2.imread(lot) if global_configs.is_tracking else lot
    result, classification_time = RootClassification.classify(img)
    print(f'Space {space_id} - {result}')

def run():
  if global_configs.is_tracking:
    RootTracking.set_parking_buffer(is_image=False)
  cap, video_info = setup_capture(fn=global_configs.data_path)
  pause = False
  cap_timeout_var = CAP_TIMEOUT
  while cap.isOpened():
    # update capture timeout
    cap_timeout_var -= 1
    
    lots = []
    ret, frame = cap.read()
    # Read frame-by-frame
    # Current position of the video file in seconds
    video_cur_pos = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
    # Index of the frame to be decoded/captured next
    video_cur_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    if ret == False:
      print("Capture Error")
      break
    
    if global_configs.is_tracking:
      lots, frame_out = RootTracking.track_parking_lots(frame=frame, video_cur_pos=video_cur_pos, export_path=global_configs.export_path)
      # Display video
      put_text(frame_out, f'fps: {round(video_info["fps"])}', (10,30),(0,0,255))
      # cv2.imshow('Frame', frame_out)

    if global_configs.is_recognition:
      if global_configs.is_tracking and len(lots):
        lots = np.unique(lots)
        Thread(target=recognition_thread, args=(lots,)).start()
        # for lot in lots:
        #   valid_car = lot.split('/')[-1]
        #   space_id = valid_car.split('_')[0]
        #   if valid_car.find('_T.') == -1:
        #     continue
        #   img = cv2.imread(lot)
        #   RootRecognition.set_data(img)
        #   # Detect license plate area by WPOD-Net
        #   _, lp_img, lp_type, detection_time = RootRecognition.detect_license_plate(img)
        #   # Recognize license plate by OCR
        #   lp_text, recognition_time = RootRecognition.recognize_by_easy_ocr()
        #   print(f'Space {space_id}, License plate: {lp_text}')
        #   # cv2.imshow('License plate', lp_img)
        #   # cv2.waitKey()
      elif not global_configs.is_tracking and cap_timeout_var <= 0:
        cap_timeout_var = CAP_TIMEOUT
        Thread(target=recognition_thread, args=([frame],)).start()
        cv2.imshow('Frame', frame)
        # RootRecognition.set_data(frame)
        # # Detect license plate area by WPOD-Net
        # _, lp_img, lp_type, detection_time = RootRecognition.detect_license_plate(frame)
        # # Recognize license plate OCR
        # lp_text, recognition_time = RootRecognition.recognize_by_easy_ocr()
        # print('License plate:', lp_text)
        # cv2.imshow('License plate', lp_img)
        # cv2.waitKey()
    
    if global_configs.is_classification and cap_timeout_var <= 0:
      cap_timeout_var = CAP_TIMEOUT
      if global_configs.is_tracking and len(lots):
        lots = np.unique(lots)
        Thread(target=classification_thread, args=(lots,)).start()
        # for lot in lots:
        #   valid_car = lot.split('/')[-1]
        #   space_id = valid_car.split('_')[0]
        #   if valid_car.find('_T.') == -1:
        #     continue
        #   img = cv2.imread(lot)
        #   result, classification_time = RootClassification.classify(img)
        #   print(f'Space {space_id} - {result}')
      elif not global_configs.is_tracking:
        result, classification_time = RootClassification.classify(frame)
        print(result, classification_time)
        put_text(image=frame, text=result)
        cv2.imshow('Class', frame)
        cv2.waitKey()

    if not global_configs.is_tracking and not global_configs.is_recognition and not global_configs.is_classification:
      frame_out = frame
    cv2.imshow('Frame', frame_out)
    # Control displaying video
    k = cv2.waitKey(1)
    if k == ord('q'):
      break
    elif k == ord('c'):
      cv2.imwrite('tracking/data/captures/frame%d.jpg' % video_cur_frame, frame_out)
    elif k == ord('j'):
      cap.set(cv2.CAP_PROP_POS_FRAMES, video_cur_frame-100)  # jump to frame
    elif k == ord('l'):
      cap.set(cv2.CAP_PROP_POS_FRAMES, video_cur_frame+100)  # jump to frame
    elif k == ord('k') or k == ord(' '):
      pause = not pause

    while pause:
      k = cv2.waitKey(1)
      if k == ord('q'):
        exit()
      elif k == ord('c'):
        cv2.imwrite('tracking/data/captures/frame%d.jpg' % video_cur_frame, frame_out)
      elif k == ord('k') or k == ord(' '):
        pause = not pause
  cap.release()
  cv2.destroyAllWindows()

run()
