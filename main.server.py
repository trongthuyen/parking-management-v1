print('\033[92m')

from utils.input import *
from utils.global_config import *
from utils.tools import *
import cv2
import numpy as np
from threading import Thread
from datetime import datetime
from receiving_data import Receiver
import csv

input_data = input_process()
global_configs = Config(input_data=input_data)

summary(global_configs)

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


def recognition_processing(image):
  img = cv2.imread(image)
  RootRecognition.set_data(img)
  # Detect license plate area by WPOD-Net
  _, lp_img, lp_type, detection_time = RootRecognition.detect_license_plate(img)
  # Recognize license plate by OCR
  lp_text, recognition_time = RootRecognition.recognize_by_easy_ocr()
  return lp_text

def classification_processing(image):
  img = cv2.imread(image)
  result, classification_time = RootClassification.classify(img)
  return result

def execute_modules(images=[]):
  # process images
  with open('event_logs.csv', 'a', newline='') as outfile:
    writer = csv.writer(outfile)
    for img in images:
      file_name = img.split('/')[-1]
      sliced_file_name = file_name.split('_')
      if global_configs.is_recognition and sliced_file_name[1] == 'T':
        sliced_file_name[2] = recognition_processing(img)
      if global_configs.is_classification and sliced_file_name[1] == 'T':
        sliced_file_name[3] = classification_processing(img).split(': ')[0]
      timestamp = sliced_file_name[4].split('.')[0]
      sliced_file_name[4] = datetime.fromtimestamp(int(timestamp))
      writer.writerow([
        sliced_file_name[4],
        f'SPACE-{sliced_file_name[0]}',
        "Occupied" if sliced_file_name[1] == "T" else "Unoccupied",
        sliced_file_name[2],
        sliced_file_name[3]
      ])

def run():
  session = Receiver()
  session.start_session()
  try:
    session.listen(1)
    session.receive_data(execute_modules)
  except KeyboardInterrupt:
    exit()
  finally:
    print('[SERVER: DONE]')

run()
