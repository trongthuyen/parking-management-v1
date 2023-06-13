def input_process():
  is_tracking = input(">> Do you want to track the parking lots? (y/N): ") or 'N'
  is_recognition = input(">> Do you want to recognize the license plates? (y/N): ") or 'N'
  is_classification = input(">> Do you want to classify the cars? (y/N): ") or 'N'
  data_path = input('Enter your data path: ')

  if not data_path:
    data_path = ''
    # exit('Not found any image or video.')
  
  data_path = data_path.strip()
  data_path = data_path.replace('\\', '/')
  data_path = data_path.strip('/')
  
  return [
    data_path,
    True if is_tracking == 'Y' or is_tracking == 'y' else False,
    True if is_recognition == 'Y' or is_recognition == 'y' else False,
    True if is_classification == 'Y' or is_classification == 'y' else False,
  ]


def input_option(is_tracking=False):
  mode = input("[?] Single image/Multi images (1/2): ") or '1'
  
  image_path = ''
  folder_path = ''
  fn_yaml = ''
  crop_fr_yaml = ''
  
  if mode == '1':
    image_path = input("[!] Enter image path: ")
    if not image_path:
      exit('[X] Got no image path.')
    else:
      image_path = image_path.replace('\\', '/')
      image_path = image_path.strip('/')
      splited_path = image_path.split('/')
      splited_path.pop()
      fn_yaml = '/'.join(splited_path) + '/parkinglots.yml'
      crop_fr_yaml = '/'.join(splited_path) + '/crop_frames.yml'
  elif mode == '2':
    folder_path = input("[!] Enter folder path: ")
    if not folder_path:
      exit('[X] Got no folder path.')
    else:
      folder_path = folder_path.replace('\\', '/')
      folder_path = folder_path.strip('/')
      fn_yaml = folder_path + '/parkinglots.yml'
      crop_fr_yaml = folder_path + '/crop_frames.yml'
  else:
    exit('[X] Mode is invalid')
  
  return [
    image_path if len(image_path) else folder_path,
    int(mode),
    fn_yaml if is_tracking else '',
    crop_fr_yaml if is_tracking else ''
  ]
