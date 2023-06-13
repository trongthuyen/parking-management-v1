from difflib import SequenceMatcher
import cv2

def similar(a, b):
  return SequenceMatcher(None, a, b).ratio()

def put_text(image, text, position=(10, 50), color=(255, 255, 255), thickness=1):
  x, y = position
  cv2.putText(
    image,
    text,
    (x, y),
    cv2.FONT_HERSHEY_PLAIN,
    1.5,
    color=color,
    lineType=cv2.LINE_AA,
    thickness=thickness
  )

def setup_capture(fn, start_frame=0):
  cap = cv2.VideoCapture(fn)
  video_info = {
    'fps':  cap.get(cv2.CAP_PROP_FPS),
    'width':  int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
    'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    'fourcc': cap.get(cv2.CAP_PROP_FOURCC),
    'num_of_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  }
  cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)  # jump to frame
  return cap, video_info