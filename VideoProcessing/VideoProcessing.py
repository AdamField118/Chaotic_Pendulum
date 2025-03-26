import cv2
import numpy as np
import math
import matplotlib.pyplot as plt

firstLED = []
secondLED = []

# Open the video file (or use 0 for webcam)
cap = cv2.VideoCapture("C:\\Users\\adamf\\OneDrive\\Desktop\\IPL\\Double Pendulum\\Videos\\DSC_0058.AVI")
if not cap.isOpened():
    print("Error opening video.")
    exit()

# Read the first frame
ret, first_frame = cap.read()
if not ret:
    print("Cannot read the first frame.")
    exit()

# Global variable to store the selected pixel value
reference_point = None

# Mouse callback function to capture pixel value on click
def click_and_save(event, x, y, flags, param):
    global reference_point, first_frame
    if event == cv2.EVENT_LBUTTONDOWN:
        reference_point = (x, y)
        print(f"Clicked at {reference_point}")
        cv2.imshow("Select Pivot Point", first_frame)
        cv2.destroyWindow("Select Pivot Point")

# Create a window to display the first frame
cv2.namedWindow("Select Pivot Point")
cv2.imshow("Select Pivot Point", first_frame)
cv2.setMouseCallback("Select Pivot Point", click_and_save)

# Wait until a key is pressed (or until the window is closed by our callback)
cv2.waitKey(0)

# At this point, 'selected_pixel' holds the pixel value clicked on the first frame
if reference_point is None:
    print("No pixel was selected. Exiting.")
    cap.release()
    cv2.destroyAllWindows()
    exit()

# Global variable to store the selected pixel value
middle_point = None

# Mouse callback function to capture pixel value on click
def click_and_save(event, x, y, flags, param):
    global middle_point, first_frame
    if event == cv2.EVENT_LBUTTONDOWN:
        middle_point = (x, y)
        print(f"Clicked at {middle_point}")
        cv2.imshow("Select first LED", first_frame)
        cv2.destroyWindow("Select first LED")

# Create a window to display the first frame
cv2.namedWindow("Select first LED")
cv2.imshow("Select first LED", first_frame)
cv2.setMouseCallback("Select first LED", click_and_save)

# Wait until a key is pressed (or until the window is closed by our callback)
cv2.waitKey(0)

# At this point, 'selected_pixel' holds the pixel value clicked on the first frame
if middle_point is None:
    print("No pixel was selected. Exiting.")
    cap.release()
    cv2.destroyAllWindows()
    exit()

# Global variable to store the selected pixel value
end_point = None

# Mouse callback function to capture pixel value on click
def click_and_save(event, x, y, flags, param):
    global end_point, first_frame
    if event == cv2.EVENT_LBUTTONDOWN:
        end_point = (x, y)
        print(f"Clicked at {end_point}")
        cv2.imshow("Select second LED", first_frame)
        cv2.destroyWindow("Select second LED")

# Create a window to display the first frame
cv2.namedWindow("Select second LED")
cv2.imshow("Select second LED", first_frame)
cv2.setMouseCallback("Select second LED", click_and_save)

# Wait until a key is pressed (or until the window is closed by our callback)
cv2.waitKey(0)

# At this point, 'selected_pixel' holds the pixel value clicked on the first frame
if end_point is None:
    print("No pixel was selected. Exiting.")
    cap.release()
    cv2.destroyAllWindows()
    exit()

previous_first_position = middle_point
previous_second_position = end_point

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Option 1: If LEDs are very bright, use grayscale thresholding
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Adjust threshold value as needed – this should pick out the LEDs
    _, thresh = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY)

    # Option 2: If LEDs have a distinct color, you could convert to HSV and threshold based on hue/saturation/value
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # lower = np.array([H_min, S_min, V_min])
    # upper = np.array([H_max, S_max, V_max])
    # thresh = cv2.inRange(hsv, lower, upper)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    led_coords = []
    # Create an empty mask with the same dimensions as the frame
    led_mask = np.zeros_like(frame)
    
    current_first_position = None
    current_second_position = None

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 5 or area > 500:  # adjust these area thresholds based on your LED size
            continue

        # Compute the bounding box or moments to get the center coordinate
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0

        #print(previous_first_position)
        #print(previous_second_position)
        firstDistanceFromPrevious = math.sqrt((cX - previous_first_position[0])**2 + (cY - previous_first_position[1])**2)
        secondDistanceFromPrevious =  math.sqrt((cX - previous_second_position[0])**2 + (cY - previous_second_position[1])**2)
        if firstDistanceFromPrevious > secondDistanceFromPrevious:
            pixel_number = 2
            current_second_position = (cX,cY)
        else:
            pixel_number = 1
            current_first_position = (cX,cY)

        if current_first_position == None:
            current_first_position = previous_first_position
        if current_second_position == None:
            current_second_position = previous_second_position

        frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        fps = cap.get(cv2.CAP_PROP_FPS)
        time_value = frame_index / fps

        theta = math.atan2(cX - reference_point[0], cY - reference_point[1])

        led_coords.append((time_value, theta, pixel_number))
        
        # Draw the LED region on the mask (copy original LED region)
        x, y, w, h = cv2.boundingRect(cnt)
        led_mask[y:y+h, x:x+w] = frame[y:y+h, x:x+w]
        
        # Optionally, draw a circle on the original frame for visualization
        cv2.putText(frame, f"{round(math.degrees(theta),2)},{pixel_number}", (cX+15, cY-2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 128), 2)

    previous_first_position = current_first_position
    previous_second_position = current_second_position

    # For visualization, create a frame that blacks out everything except LEDs.
    # Here led_mask only has the regions corresponding to LED detected (rest is black).
    cv2.imshow("Original with LED Coordinates", frame)

    # Assuming conversion_factor is defined if needed; here we assume pixel distances equal "meters"
    for led in led_coords:
        if led[2] == 2:
            secondLED.append((led[0],led[1]))
        else:
            firstLED.append((led[0],led[1]))

    key = cv2.waitKey(30) & 0xFF
    if key == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()

#graphing next

def plot_graph(data):
    times = []
    angles = []
    for point in data:
        times.append(point[0])
        angles.append(math.degrees(point[1]))
    
    # Create the plot
    plt.figure(figsize=(8, 6))
    plt.plot(times, angles, linestyle='-')
    
    # Label the axes
    plt.xlabel("Time (seconds)")
    plt.ylabel("Angle (degrees)")
    plt.title("Angle vs Time Plot")
    
    # Show grid
    plt.grid(True)
    
    # Display the plot
    plt.show()

def plot_graphs(data, data2):
    times = []
    angles = []
    times2 = []
    angles2 = []
    for point in data:
        times.append(point[0])
        angles.append(math.degrees(point[1]))
    for point2 in data2:
        times2.append(point2[0])
        angles2.append(math.degrees(point2[1]))

    # Create the plot
    plt.figure(figsize=(8, 6))
    plt.plot(times, angles, linestyle='-')
    plt.plot(times2, angles2, color='red', linestyle='-')
    
    # Label the axes
    plt.xlabel("Time (seconds)")
    plt.ylabel("Angle (degrees)")
    plt.title("Angle vs Time Plot")
    
    # Show grid
    plt.grid(True)
    
    # Display the plot
    plt.show()

plot_graph(firstLED)
plot_graph(secondLED)
plot_graphs(firstLED,secondLED)