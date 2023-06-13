def input_process():
  is_tracking = input(">> Do you want to track the parking lots? (y/N): ") or 'N'
  is_send = input(">> Do you want to send data to server? (y/N): ") or 'N'
  data_path = input('Enter your video path: ')

  if not data_path:
    data_path = ''
    # exit('Not found any image or video.')
  
  data_path = data_path.strip()
  data_path = data_path.replace('\\', '/')
  data_path = data_path.strip('/')
  
  return [
    data_path,
    True if is_tracking == 'Y' or is_tracking == 'y' else False,
    True if is_send == 'Y' or is_send == 'y' else False,
  ]
