from recognition.lpr_lib_detection import *
import easyocr
import time

class Recognition:
  detect_model = None
  recognize_model = None
  data = []
  license_plate_image = []
  license_plate_type = None
  license_plate_text = ''
  model_path = r'recognition/models/wpod-net/wpod-net_update1.json'
  __tmp__ = None
  char_list =  '0123456789QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm'
  
  def __init__(self, model_path = '') -> None:
    if model_path == '':
      self.detect_model = load_model(self.model_path)
    else:
      self.detect_model = load_model(model_path)
  
  def set_data(self, data):
    self.data = data

  def fine_tune(self, license_plate):
    newString = ""
    for i in range(len(license_plate)):
      if license_plate[i] in self.char_list:
        newString += license_plate[i]
    return newString
  
  # Detect license plate by Warped Plannar Object Detection Network
  def detect_license_plate(self, image=None):
    try:
      if not image.any():
        return None, image, -1, 0

      self.set_data(image)
      Dmax, Dmin = 608, 488
      # Calculate the ratio W/H and identify D-min
      ratio = float(max(self.data.shape[:2])) / min(self.data.shape[:2])
      side = int(ratio * Dmin)
      bound_dim = min(side, Dmax)
      start = time.time()*1000
      _ , lp_img, lp_type = detect_lp(self.detect_model, im2single(self.data), bound_dim, lp_threshold=0.5)
      end = time.time()*1000
      self.__tmp__ = _
      self.license_plate_type = lp_type
      if len(lp_img):
        self.license_plate_image = lp_img[0]
        return _, lp_img[0], lp_type, end - start
      else:
        self.license_plate_image = image
        return _, image, lp_type, end - start
    
    except:
      return None, image, -1, 0

  # recognize by easy ocr
  def recogniting_license_plate(self, image):
    try:
      frame_blur = cv2.GaussianBlur(image, (5, 5), 3)
      frame_blur = cv2.GaussianBlur(frame_blur, (3, 3), 16)
      gray = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2GRAY)
      # gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
      cropped_image = gray[0:, 0:]    # [height1: height2, weight1: weight2]
      reader = easyocr.Reader(['en'])
      start = time.time()*1000
      result = reader.readtext(image=cropped_image, detail=0, paragraph=False)
      end = time.time()*1000
      text = ''
      for res in result:
        # text += f'{res[-2]}+'
        text += res
      run_time = end - start
      return text.strip('+').replace(',', '').replace('.', '').replace('-', '').replace(' ', '').replace('+', '-'), run_time
    except:
      return '--', 0
  
  # Using EASY OCR to recognize license plate
  def recognize_by_easy_ocr(self, image=None):
    if image:
      self.license_plate_image = image
    if not len(self.license_plate_image):
      return
    # Chuyen doi anh bien so
    self.license_plate_image = cv2.convertScaleAbs(self.license_plate_image, alpha=(255.0))
    plate, executing_time = self.recogniting_license_plate(self.license_plate_image)
    self.license_plate_text = plate
    return self.fine_tune(plate), executing_time
