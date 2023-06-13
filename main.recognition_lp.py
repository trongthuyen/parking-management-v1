print('\033[92m')

from utils.input import *
from utils.global_config import *
from utils.tools import *
import cv2
from glob import glob
import csv
import os
import shutil

configs = input_option()

# import recognition model
from recognition.recognition import Recognition
RootRecognition = Recognition()

def run():
  # Single image mode
  if configs[1] == 1:
    image = cv2.imread(configs[0])
    RootRecognition.set_data(image)
    # Detect license plate area by Warped Planar Object Detection Network (WPOD-Net)
    _, lp_img, lp_type, detection_time = RootRecognition.detect_license_plate(image)
    # Recognize license plate by EASY OCR
    lp_text, recognition_time = RootRecognition.recognize_by_easy_ocr()
    print(f'License plate: {lp_text}')
    exported_image = cv2.normalize(lp_img, dst=None, alpha=0, beta=255,norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    cv2.imwrite(f'recognition/data/licenseplates/{lp_text}.jpg', exported_image)
    cv2.imshow('License plate', lp_img)
    cv2.waitKey()
  
  # Multi image mode
  elif configs[1] == 2:
    images = glob(f'{configs[0]}/*')
    export_path = configs[0] + '/license_plates'
    if os.path.isdir(export_path):
      shutil.rmtree(export_path)
    os.mkdir(export_path)
    results = [['No.', 'Expected Result', 'Actual Result', 'Similar Ratio', 'Detection Time (ms)', 'Recognition Time (ms)', 'Response Time (ms)']]
    idx = 1
    for image in images:
      if image.find('.jpg') != -1 or image.find('.png') != -1:
        tmp_path = image.replace('\\', '/')
        x = tmp_path.split('/')
        expected_result = x.pop().split('.')[0]
        tmp = expected_result.split('-')

        # Just check postfix of LP
        # target = expected_result.replace('-', '')
        target = tmp[0]
        if len(tmp) > 1:
          target = tmp[1]

        image = cv2.imread(tmp_path)
        RootRecognition.set_data(image)
        # Detect license plate area by Warped Planar Object Detection Network (WPOD-Net)
        _, lp_img, lp_type, detection_time = RootRecognition.detect_license_plate(image)
        
        # Recognize license plate by EASY OCR
        lp_text, recognition_time = RootRecognition.recognize_by_easy_ocr()
        lp_uppercase = lp_text.upper()
        similar_ratio = similar(lp_uppercase, target.upper())
        similar_ratio = similar_ratio if lp_uppercase.find(target.upper()) == -1 else 1
        similar_ratio = round(similar_ratio, 2)
        output = target if similar_ratio == 1 else lp_uppercase
        
        # Append to csv
        print(f'{idx} - {target} - {lp_uppercase} - {similar_ratio*100}% - {round(recognition_time + detection_time)}ms')
        results.append([idx, target, output, similar_ratio, round(detection_time), round(recognition_time), round(detection_time + recognition_time)])
        put_text(image, lp_uppercase)
        
        # Save output image
        exported_image = cv2.normalize(lp_img, dst=None, alpha=0, beta=255,norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        put_text(exported_image, lp_uppercase)
        cv2.imwrite(f'{export_path}/{target}~{round(similar_ratio*100)}%.jpg', exported_image)
        idx += 1
        
        # cv2.imshow('LP', image)
        # cv2.waitKey()
    
    with open(f'{export_path}/result_statistics.csv', 'w', newline='') as file:
      writer = csv.writer(file)
      writer.writerows(results)

run()