class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

class Config:
  data_path = ''
  export_path = ''
  is_tracking = False
  is_send = False
  
  fn_yaml = ''
  crop_fr_yaml = ''
  
  def __init__(self, input_data) -> None:
    self.data_path = input_data[0]
    self.is_tracking = input_data[1]
    self.is_send = input_data[2]
    
    data_dir = input_data[0].split('/')
    data_dir.pop()
    self.export_path = '/'.join(data_dir) + '/lots'
    self.fn_yaml = '/'.join(data_dir) + '/parkinglots.yml'
    self.crop_fr_yaml = '/'.join(data_dir) + '/crop_frames.yml'
  
  def set_yaml_path(self, dir_path):
    self.fn_yaml = dir_path + '/parkinglots.yml'
    self.crop_fr_yaml = dir_path + '/crop_frames.yml'
  
def summary(config):
  try:
    pltColor = bcolors.OKGREEN if config.is_tracking else bcolors.FAIL
    lprColor = bcolors.OKGREEN if config.is_send else bcolors.FAIL
    
    print('\n')
    print(f'{bcolors.HEADER}SUMMARY')
    print('==============================')
    print(f'{pltColor}Parking lot detection')
    print(f'{lprColor}Send data to server')

    print(f'{bcolors.OKGREEN}Data path: {config.data_path}')
    print(f'{bcolors.OKGREEN}Fn path: {config.fn_yaml}')
    print(f'{bcolors.OKGREEN}Crop fn path: {config.crop_fr_yaml}')
    print(f'{bcolors.OKGREEN}Export path: {config.export_path}')
    print(f'{bcolors.HEADER}==============================\n{bcolors.OKGREEN}')
  except:
    print(bcolors.WARNING+'Occured an error in progress!'+bcolors.OKGREEN)
