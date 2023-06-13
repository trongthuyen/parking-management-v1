import __init__

from utils_copy.input import *
from utils_copy.global_config import *
from utils_copy.tools import *
from utils_copy.constants import *
from threading import Thread

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

# client = None
if global_configs.is_send:
  from transmit_data import Transmitter
  # client = Transmitter()
  # client.start_session()

def handle_send(host, port, file_name, src_path=''):
  client = Transmitter(host=HOST, port=PORT)
  client.start_session()
  client.send_data(file_name, src_path if len(src_path) else file_name)
  client.end_session()

def run():
  if global_configs.is_tracking:
    RootTracking.set_parking_buffer(is_image=False)
  cap, video_info = setup_capture(fn=global_configs.data_path)
  pause = False
  cap_timeout_var = CAP_TIMEOUT
  while cap.isOpened():
    # update capture timeout
    cap_timeout_var -= 1
    
    lots = []
    ret, frame = cap.read()
    # Read frame-by-frame
    # Current position of the video file in seconds
    video_cur_pos = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
    # Index of the frame to be decoded/captured next
    video_cur_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    if ret == False:
      Thread(target=handle_send, args=(HOST, PORT, '##')).start()
      print("Capture Error")
      break
    
    if global_configs.is_tracking:
      lots, frame_out = RootTracking.track_parking_lots(frame=frame, video_cur_pos=video_cur_pos, export_path=global_configs.export_path)
      # Send data to server
      if len(lots) and global_configs.is_send:
        thread = Thread(target=handle_send, args=(HOST, PORT, 'frame%d.zip'%video_cur_pos, 'lots.zip'))
        thread.start()
        thread.join()
      # Display video
      put_text(frame_out, f'fps: {round(video_info["fps"])}', (10,30),(0,0,255))
      cv2.imshow('Frame', frame_out)

    # Control displaying video
    k = cv2.waitKey(1)
    if k == ord('q'):
      break
    elif k == ord('c'):
      cv2.imwrite('../tracking/data/captures/frame%d.jpg' % video_cur_frame, frame_out)
    elif k == ord('j'):
      cap.set(cv2.CAP_PROP_POS_FRAMES, video_cur_frame-100)  # jump to frame
    elif k == ord('l'):
      cap.set(cv2.CAP_PROP_POS_FRAMES, video_cur_frame+100)  # jump to frame
    elif k == ord('k') or k == ord(' '):
      pause = not pause

    while pause:
      k = cv2.waitKey(1)
      if k == ord('q'):
        exit()
      elif k == ord('c'):
        cv2.imwrite('../tracking/data/captures/frame%d.jpg' % video_cur_frame, frame_out)
      elif k == ord('k') or k == ord(' '):
        pause = not pause
  cap.release()
  cv2.destroyAllWindows()
  print('CLIENT: DONE')

run()