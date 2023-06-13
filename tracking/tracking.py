import yaml
import numpy as np
import cv2
import zipfile
import os
import time
import shutil

class Tracking:
  # <ID>_<status>_<license plate>_<car class>_<timestamp>.jpg
  file_name_sample = ['null']*5
  zip_name = 'lots.zip'
  export_path = 'lots'
  config = None
  cap = None
  crop_frames_data = []
  parking_data = None
  parking_contours = []
  parking_bounding_rects = []
  parking_mask = []
  kernel_erode = None
  parking_status = []
  parking_buffer = []
  export_img_timeout = []
  video_cur_pos = None
  re_export_timeout = 999999999
  
  def __init__(self):
    self.config = {
      'parking_overlay': True,
      'parking_id_overlay': True,
      'parking_detection': True,
      'park_laplacian_th': 3.75,
      'park_sec_to_wait': -1,
      'start_frame': 0
    }

  def load_yaml(self, fn_yaml, crop_fr_yaml=None):
      # Read YAML data (crop frames)
    with open(crop_fr_yaml if crop_fr_yaml != None else fn_yaml, 'r') as stream:
      self.crop_frames_data = yaml.safe_load(stream)
      if not self.crop_frames_data:
        self.crop_frames_data = []

    # Read YAML data (parking space polygons)
    with open(fn_yaml, 'r') as stream:
      self.parking_data = yaml.safe_load(stream)
    for park in self.parking_data:
      points = np.array(park['points'])
      rect = cv2.boundingRect(points)
      points_shifted = points.copy()
      points_shifted[:, 0] = points[:, 0] - rect[0]  # shift contour to roi
      points_shifted[:, 1] = points[:, 1] - rect[1]
      self.parking_contours.append(points)
      self.parking_bounding_rects.append(rect)
      mask = cv2.drawContours(np.zeros((rect[3], rect[2]), dtype=np.uint8), [points_shifted], contourIdx=-1,
                  color=0, thickness=-1, lineType=cv2.LINE_8)
      mask = mask == 0
      self.parking_mask.append(mask)

    self.kernel_erode = cv2.getStructuringElement(
      cv2.MORPH_ELLIPSE, (3, 3))  # morphological kernel
    # self.kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)) # morphological kernel
    self.kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 19))
    self.parking_status = [True]*len(self.parking_data)
    self.parking_buffer = [None]*len(self.parking_data)
    self.export_img_timeout = [0]*len(self.parking_data)
  
  def set_parking_buffer(self, is_image):
    if is_image:
      self.parking_buffer = [0]*len(self.parking_data)
    else:
      self.parking_buffer = [None]*len(self.parking_data)
  
  def track_parking_lots(self, frame, video_cur_pos=9999999999, export_path=None, delay=0):
    print(export_path)
    # No image found
    if not frame.any():
      print('No image found')
      return [], None
    
    if export_path and os.path.isdir(export_path):
      shutil.rmtree(export_path)
    elif not export_path and os.path.isdir(self.export_path):
      shutil.rmtree(self.export_path)
    if export_path:
      os.mkdir(export_path)
    else:
      os.mkdir(self.export_path)
    # Background Subtraction
    frame_blur = cv2.GaussianBlur(frame.copy(), (3, 3), 5)
    frame_gray = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2GRAY)
    frame_out = frame.copy()
    frame_cut = frame.copy()

    # tracking
    lots = []
    if self.config['parking_detection']:
      for ind, park in enumerate(self.parking_data):
        points = np.array(park['points'])
        rect = self.parking_bounding_rects[ind]
        # crop roi for faster calcluation
        roi_gray = frame_gray[rect[1]:(
          rect[1]+rect[3]), rect[0]:(rect[0]+rect[2])]
        laplacian = cv2.Laplacian(roi_gray, cv2.CV_64F)
        points[:, 0] = points[:, 0] - rect[0]  # shift contour to roi
        points[:, 1] = points[:, 1] - rect[1]
        delta = np.mean(np.abs(laplacian * self.parking_mask[ind]))
        status = delta < self.config['park_laplacian_th']
          
        if delay != 0 and status != self.parking_status[ind] and self.parking_buffer[ind] == None:
          self.parking_buffer[ind] = video_cur_pos
        # If status is still different than the one saved and counter is open
        elif delay == 0 or (status != self.parking_status[ind] and self.parking_buffer[ind] != None):
          if delay == 0 or (video_cur_pos - self.parking_buffer[ind] > self.config['park_sec_to_wait']):
            if export_path:
              self.export_img_timeout[ind] = self.re_export_timeout
            self.parking_status[ind] = status
            self.parking_buffer[ind] = None
            
            # TODO Car recognition
            if not status:
              # occupied
              # ...
              pass

            if len(self.crop_frames_data):
              for crop in self.crop_frames_data:
                if crop['id'] == park['id']:
                  p = crop['points']
                  crop_img = frame_cut[p[0][1]:p[2][1], p[0][0]:p[1][0]]
                  self.file_name_sample[0] = f'{crop["id"]}'
                  self.file_name_sample[1] = "T" if not status else "F"
                  self.file_name_sample[4] = f'{round(time.time())}'
                  file_name = '_'.join(self.file_name_sample)
                  cv2.imwrite(f'{export_path if export_path else self.export_path}/{file_name}.jpg', crop_img)
                  lots.append(f'{export_path if export_path else self.export_path}/{file_name}.jpg')
        # If status is still same and counter is open
        elif status == self.parking_status[ind] and self.parking_buffer[ind] != None:
          if video_cur_pos - self.parking_buffer[ind] > self.config['park_sec_to_wait']:
            self.parking_buffer[ind] = None
        
        # If timeout == 0, then transmit image to server
        if self.export_img_timeout[ind] <= 0:
          if export_path:
            self.export_img_timeout[ind] = self.re_export_timeout

          # TODO Car recognition
          if not self.parking_status[ind]:
            # occupied
            # ...
            pass

          if len(self.crop_frames_data):
            for crop in self.crop_frames_data:
              if crop['id'] == park['id']:
                p = crop['points']
                crop_img = frame_cut[p[0][1]:p[2][1], p[0][0]:p[1][0]]
                self.file_name_sample[0] = f'{crop["id"]}'
                self.file_name_sample[1] = "T" if not status else "F"
                self.file_name_sample[4] = f'{round(time.time())}'
                file_name = '_'.join(self.file_name_sample)
                cv2.imwrite(f'{export_path if export_path else self.export_path}/{file_name}.jpg', crop_img)
                lots.append(f'{export_path if export_path else self.export_path}/{file_name}.jpg')
        else:
          self.export_img_timeout[ind] -= 1
        # print("#%d: %.2f" % (ind, delta))

      # # packing zip file for transmiting
      # if export_path and len(lots) > 0:
      #   if os.path.isfile(self.zip_name):
      #     os.remove(self.zip_name)
      #   with zipfile.ZipFile(self.zip_name, 'w') as file:
      #     for lot in lots:
      #       new_path = 'data/'+lot.split('/')[-1]
      #       file.write(lot, new_path)
      #       # os.remove(lot)

        # pp = park['points']
        # cv2.putText(img=frame_out, text=f'{round(delta - self.config["park_laplacian_th"], 3)}', org=(pp[0][0]+5, pp[2][1]-5), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(255,255,0))

    if self.config['parking_overlay']:
      for ind, park in enumerate(self.parking_data):
        points = np.array(park['points'])
        if self.parking_status[ind]:
          # unoccupied, BGR
          color = (0, 255, 0)
        else:
          # occupied, BGR
          color = (0, 0, 255)
        cv2.drawContours(
          frame_out,
          [points],
          contourIdx=-1,
          color=color,
          thickness=1,
          lineType=cv2.LINE_8
        )
        moments = cv2.moments(points, binaryImage=True)
        centroid = (int(moments['m10']/moments['m00'])-3, int(moments['m01']/moments['m00'])+3)
        cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame_out, str(park['id']), centroid, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    return lots, frame_out
