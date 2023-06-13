import cv2
import numpy as np
from classification.cc_resnet_152 import resnet152_model
import scipy.io
import time

class Classification:
  data = []
  model = None
  img_width, img_height = 0, 0
  num_channels = 0
  batch_size = 0
  cars_meta = None
  class_names = None
  num_classes = 0
  meta_data_path = r'classification/data/devkit/cars_meta'
  
  def __init__(self, meta_data_path='') -> None:
    self.img_width, self.img_height = 224, 224
    self.num_channels = 3
    self.batch_size = 32
    if meta_data_path == '':
      self.cars_meta = scipy.io.loadmat(self.meta_data_path)
    else:
      self.cars_meta = scipy.io.loadmat(meta_data_path)
    self.class_names = self.cars_meta['class_names']  # shape=(1, 196)
    self.class_names = np.transpose(self.class_names)
    self.num_classes = len(self.class_names)
  
  def load_model_resnet152(self, model_path=None):
    if model_path != None:
      model_weights_path = model_path
    else:
      model_weights_path = 'classification/models/resnet152/model.96-0.89.hdf5'
    model = resnet152_model(
      img_rows=self.img_height,
      img_cols=self.img_width,
      color_type=self.num_channels,
      num_classes=self.num_classes
    )
    model.load_weights(model_weights_path, by_name=True)
    self.model = model

  def set_data(self, data):
    self.data = data

  def classify(self, image=None):
    if not image.any():
      return 'Not found a car: 0.0'
    
    self.set_data(image)
    Dmax, Dmin = 800, 800
    frame = cv2.resize(self.data, (Dmax, Dmin), cv2.INTER_CUBIC)
    bgr_img = cv2.resize(frame, (self.img_width, self.img_height), cv2.INTER_CUBIC)
    rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    rgb_img = np.expand_dims(rgb_img, 0)
    start = time.time()*1000
    preds = self.model.predict(rgb_img)
    end = time.time()*1000
    prob = np.max(preds)
    class_index = np.argmax(preds)
    text = 'Not found a car: 0.0'
    if class_index >= 0 and class_index < self.num_classes:
      text = '{}: {}'.format(
        self.class_names[class_index][0][0], round(float(prob), 4))
    return text, round(end - start)
