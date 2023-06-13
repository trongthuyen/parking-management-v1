print('\033[92m')

from utils.input import *
from utils.global_config import *
from utils.tools import *
import cv2
import numpy as np

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

def run():
  lots = []
  # read image
  image = cv2.imread(global_configs.data_path)
  
  # Track parking lots
  if global_configs.is_tracking:
    RootTracking.set_parking_buffer(is_image=True)
    lots, frame_out = RootTracking.track_parking_lots(image, 99999999999, global_configs.export_path)
    # if frame_out.any():
    #   cv2.imshow('Frame', frame_out)
    #   cv2.waitKey()

  # Recognize license plate
  if global_configs.is_recognition:
    # CASE: Including tracking parking lots
    if global_configs.is_tracking and len(lots):
      lots = np.unique(lots)
      for lot in lots:
        valid_car = lot.split('/')[-1]
        space_id = valid_car.split('_')[0]
        if valid_car.find('_T.') == -1:
          continue
        img = cv2.imread(lot)
        RootRecognition.set_data(img)
        # Detect license plate area by Warped Planar Object Detection Network (WPOD-Net)
        _, lp_img, lp_type, detection_time = RootRecognition.detect_license_plate(img)
        
        # Recognize license plate by EASY OCR
        lp_text, recognition_time = RootRecognition.recognize_by_easy_ocr()
        print(f'Space {space_id}, License plate: {lp_text}')
        # cv2.imshow('License plate', lp_img)
        # cv2.waitKey()

    # CASE: Excluding tracking parking lots
    elif not global_configs.is_tracking:
      RootRecognition.set_data(image)
      # Detect license plate area by WPOD-Net
      _, lp_img, lp_type, detection_time = RootRecognition.detect_license_plate(image)
      
      # Recognize license plate OCR
      lp_text, recognition_time = RootRecognition.recognize_by_easy_ocr()
      upper_case_lp_text = lp_text.upper()
      print('License plate:', upper_case_lp_text)
      cv2.imshow('License plate', lp_img)
      cv2.waitKey()
  
  # Classify model-make-year
  if global_configs.is_classification:
    # CASE: Including tracking parking lots
    if global_configs.is_tracking and len(lots):
      lots = np.unique(lots)
      for lot in lots:
        valid_car = lot.split('/')[-1]
        space_id = valid_car.split('_')[0]
        if valid_car.find('_T.') == -1:
          continue
        img = cv2.imread(lot)
        result, classification_time = RootClassification.classify(img)
        print(f'Space {space_id} - {result}')

    # CASE: Excluding tracking parking lots
    elif not global_configs.is_tracking:
      result, classification_time = RootClassification.classify(image)
      print(result, classification_time)
      put_text(image=image, text=result)
      cv2.imshow('Class', image)
      cv2.waitKey()

  # Show image if it is tracking parking lots
  if global_configs.is_tracking and frame_out.any():
    cv2.imshow('Frame', frame_out)
    cv2.waitKey()

run()
