print('\033[92m')

from utils.input import *
from utils.global_config import *
from utils.tools import *
import cv2
import numpy as np
from glob import glob
from tracking.tracking import Tracking
import time

configs = input_option(is_tracking=True)

# import tracking model
RootTracking = Tracking()
RootTracking.load_yaml(
  fn_yaml=configs[2],
  crop_fr_yaml=configs[3]
)
RootTracking.set_parking_buffer(is_image=True)

def run():
  if configs[1] == 1:
    image = cv2.imread(configs[0])
    lots, frame_out = RootTracking.track_parking_lots(image, 99999999999)
    cv2.imshow('Tracking parking lots', frame_out)
    cv2.waitKey()
    
  elif configs[1] == 2:
    images = glob(f'{configs[0]}/*/**')
    for image in images:
      if (image.find('.jpg') != -1 or image.find('.png') != -1) and image.find('result.jpg') == -1:
        tmp_path = image.replace('\\', '/')
        x = tmp_path.split('/')
        x.pop()
        export_path = '/'.join(x)
        image = cv2.imread(tmp_path)
        lots, frame_out = RootTracking.track_parking_lots(image, 99999999999, f'{export_path}/lots')
        cv2.imwrite(f'{export_path}/result.jpg', frame_out)
      time.sleep(0.1)

run()