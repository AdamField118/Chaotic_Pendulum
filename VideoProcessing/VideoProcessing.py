import cv2
import numpy as np
import math
import matplotlib.pyplot as plt

firstLED = []
secondLED = []

# Open the video file (or use 0 for webcam)
cap = cv2.VideoCapture("C:\\Users\\adamf\\OneDrive\\Desktop\\IPL\\Double Pendulum\\Videos\\DSC_0059.AVI")
if not cap.isOpened():
    print("Error opening video.")
    exit()

# Read the first frame
ret, first_frame = cap.read()
if not ret:
    print("Cannot read the first frame.")
    exit()

# Global variable to store the selected pivot pixel value
reference_point = None

def click_and_save_pivot(event, x, y, flags, param):
    global reference_point, first_frame
    if event == cv2.EVENT_LBUTTONDOWN:
        reference_point = (x, y)
        print(f"Pivot selected at {reference_point}")
        cv2.imshow("Select Pivot Point", first_frame)
        cv2.destroyWindow("Select Pivot Point")

# Select pivot point
cv2.namedWindow("Select Pivot Point")
cv2.imshow("Select Pivot Point", first_frame)
cv2.setMouseCallback("Select Pivot Point", click_and_save_pivot)
cv2.waitKey(0)

if reference_point is None:
    print("No pivot point selected. Exiting.")
    cap.release()
    cv2.destroyAllWindows()
    exit()

# Global variable to store the selected first LED pixel value
middle_point = None

def click_and_save_first_led(event, x, y, flags, param):
    global middle_point, first_frame
    if event == cv2.EVENT_LBUTTONDOWN:
        middle_point = (x, y)
        print(f"First LED selected at {middle_point}")
        cv2.imshow("Select first LED", first_frame)
        cv2.destroyWindow("Select first LED")

# Select first LED point
cv2.namedWindow("Select first LED")
cv2.imshow("Select first LED", first_frame)
cv2.setMouseCallback("Select first LED", click_and_save_first_led)
cv2.waitKey(0)

if middle_point is None:
    print("No first LED selected. Exiting.")
    cap.release()
    cv2.destroyAllWindows()
    exit()

# Global variable to store the selected second LED pixel value
end_point = None

def click_and_save_second_led(event, x, y, flags, param):
    global end_point, first_frame
    if event == cv2.EVENT_LBUTTONDOWN:
        end_point = (x, y)
        print(f"Second LED selected at {end_point}")
        cv2.imshow("Select second LED", first_frame)
        cv2.destroyWindow("Select second LED")

# Select second LED point
cv2.namedWindow("Select second LED")
cv2.imshow("Select second LED", first_frame)
cv2.setMouseCallback("Select second LED", click_and_save_second_led)
cv2.waitKey(0)

if end_point is None:
    print("No second LED selected. Exiting.")
    cap.release()
    cv2.destroyAllWindows()
    exit()

# Initialize previous positions with the initially clicked points
previous_first_position = middle_point
previous_second_position = end_point

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Use grayscale thresholding to detect bright LEDs
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)
    
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    led_coords = []
    led_mask = np.zeros_like(frame)
    
    current_first_position = None
    current_second_position = None

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 5 or area > 500:  # adjust thresholds based on LED size
            continue

        # Compute centroid using moments
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0

        lengthArm1 = math.sqrt((middle_point[0] - reference_point[0])**2 + (middle_point[1] - reference_point[1])**2)
        distanceFromPivot = math.sqrt((cX - reference_point[0])**2 + (cY - reference_point[1])**2)
        firstDistanceFromPrevious = math.sqrt((cX - previous_first_position[0])**2 + (cY - previous_first_position[1])**2)
        secondDistanceFromPrevious = math.sqrt((cX - previous_second_position[0])**2 + (cY - previous_second_position[1])**2)

        # Updated LED identification logic:
        if (int(distanceFromPivot) in range(int(lengthArm1 - 20), int(lengthArm1) + 20)) and (firstDistanceFromPrevious < (20 + secondDistanceFromPrevious)):
            pixel_number = 1
            current_first_position = (cX, cY)
        else:
            pixel_number = 2
            current_second_position = (cX, cY)

        # Fallback in case no LED was detected in this frame
        if current_first_position is None:
            current_first_position = previous_first_position
        if current_second_position is None:
            current_second_position = previous_second_position

        frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        fps = cap.get(cv2.CAP_PROP_FPS)
        time_value = frame_index / fps

        theta = math.atan2(cX - reference_point[0], cY - reference_point[1])
        led_coords.append((time_value, theta, pixel_number))
        
        # Draw bounding rectangle for visualization
        x, y, w, h = cv2.boundingRect(cnt)
        led_mask[y:y+h, x:x+w] = frame[y:y+h, x:x+w]
        cv2.putText(frame, f"{round(math.degrees(theta),2)},{pixel_number}", (cX+15, cY-2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 128), 2)

    previous_first_position = current_first_position
    previous_second_position = current_second_position

    cv2.imshow("Original with LED Coordinates", frame)

    # Save LED data into corresponding lists
    for led in led_coords:
        if led[2] == 2:
            secondLED.append((led[0], led[1]))
        else:
            firstLED.append((led[0], led[1]))

    key = cv2.waitKey(30) & 0xFF
    if key == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()

# Graphing functions
def plot_graph(data):
    times = [point[0] for point in data]
    angles = [math.degrees(point[1]) for point in data]
    
    plt.figure(figsize=(8, 6))
    plt.plot(times, angles, linestyle='-')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Angle (degrees)")
    plt.title("Angle vs Time Plot")
    plt.grid(True)
    plt.show()

def plot_graphs(data1, data2):
    times1 = [point[0] for point in data1]
    angles1 = [math.degrees(point[1]) for point in data1]
    times2 = [point[0] for point in data2]
    angles2 = [math.degrees(point[1]) for point in data2]

    plt.figure(figsize=(8, 6))
    plt.plot(times1, angles1, linestyle='-', label="LED 1")
    plt.plot(times2, angles2, color='red', linestyle='-', label="LED 2")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Angle (degrees)")
    plt.title("Angle vs Time Plot")
    plt.legend()
    plt.grid(True)
    plt.show()

plot_graph(firstLED)
plot_graph(secondLED)
plot_graphs(firstLED, secondLED)
