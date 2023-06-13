'''
Q or q => quit
Z or z => undo
S or s => save
C or c => clear
'''

print('Q or q => quit')
print('Z or z => undo')
print('S or s => save')
print('C or c => clear')

import cv2
import yaml

# Initialize variables
corps = []
# out_path = 'tracking/data/videos/sample5/crop_frames.yml'
out_path = 'tracking/data/videos/sample5/parkinglots.yml'
sample_img_path = 'recognition\data\licenseplates\goa39951.jpg'

# Load the image
image = cv2.imread(sample_img_path)
last_frame = None
allow_undo = True

def render_rectangle(frame, corperates):
  if len(corperates) == 0:
    cv2.imshow("Image", frame)
    return
  for cor in corperates:
    cv2.rectangle(frame,
                  (cor['points'][0][0], cor['points'][0][1]),
                  (cor['points'][2][0], cor['points'][2][1]),
                  (0, 255, 0), 2)
    cv2.imshow("Image", frame)

# Define the callback function for mouse events
def draw_quad(event, x, y, flags, param):
  global points, draw
  try:
    if event == cv2.EVENT_LBUTTONDOWN:
      # Set the first point of the quadrilateral
      points = [(x, y)]
      draw = True
    elif event == cv2.EVENT_LBUTTONUP:
      # Set the second point of the quadrilateral
      points.append((x, y))
    elif event == cv2.EVENT_MOUSEMOVE:
      if draw:
        # Draw the current quadrilateral being defined
        temp = image.copy()
        cv2.rectangle(temp, points[0], (x, y), (0, 255, 0), 2)
        cv2.imshow("Image", temp)
  except:
    pass

# Init variables
points = []
draw = False

# Create a window and set the mouse callback function
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", draw_quad)

index = 0
cv2.imshow("Image", image)
last_frame = image.copy()
sample_frame = image.copy()
while True:
  # Display the image and wait for a key press
  # cv2.imshow("Image", image)
  
  key = cv2.waitKey(1) & 0xFF
  # Undo one step
  if key == ord('z') or key == ord('Z'):
    print('Undo')
    if len(corps) > 0 and allow_undo == True:
      allow_undo = False
      index -= 1
      corps.pop()
      image = last_frame.copy()
      render_rectangle(image, corps)
  # Exit if 'q' is pressed
  if key == ord("q") or key == ord('Q'):
    print('Quit')
    break
  # Save points into yaml file
  if key == ord('s') or key == ord('S'):
    print('Save')
    if len(corps) > 0:
      with open(out_path, 'a') as file:
        documents = yaml.dump(corps, file)
  # Clear state
  if key == ord('c') or key == ord('C'):
    print('Clear')
    corps.clear()
    image = sample_frame.copy()
    last_frame = sample_frame.copy()
    render_rectangle(image, [])
    allow_undo = True
    index = 0

  # If the quadrilateral is complete, draw it on the image
  if len(points) == 2:
    allow_undo = True
    last_frame = image.copy()
    cv2.rectangle(image, points[0], points[1], (0, 255, 0), 2)
    corps.append({
      "id": index,
      "points": [
        [points[0][0], points[0][1]],   # x0, y0
        [points[1][0], points[0][1]],   # x1, y0
        [points[1][0], points[1][1]],   # x1, y1
        [points[0][0], points[1][1]]    # x0, y1
      ]
    })
    index += 1
    points = []

# Close the window and release resources
cv2.destroyAllWindows()