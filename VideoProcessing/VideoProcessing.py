import cv2
import math
import matplotlib.pyplot as plt
import os
import json
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

video_name = 'DSC_0059' # name of the video you want to graph *dont include .AVI (see line 57 if it's not an AVI file)*
brightness_value = 140 # Use 140 for low aperture videos like DSC_0059, 245 for any other videos
graph_title = 'Chaotic Double Pendulum'

path_to_videos = 'C:\\Users\\adamf\\OneDrive\\Desktop\\IPL\\Double Pendulum\\Videos\\' # wherever you have videos on your local device
path_to_data = 'C:\\Users\\adamf\\Downloads\\' # wherever you want to save the already processed video data

firstLED = []
secondLED = []

if os.path.exists(f"{path_to_data}{video_name}.txt"):
    with open(f"{path_to_data}{video_name}.txt", "r") as file:
        for line in file:
            key, temp = line.split(":", 1)
            temp = temp.strip()
            if key == "firstLED":
                firstLED = json.loads(temp)
            elif key == "secondLED":
                secondLED = json.loads(temp)
            elif key == "Pivot":
                pivot = json.loads(temp)

    def pos_time_graph(data, data2, pivot, label, label2, pivotLabel):
        t = [point[0] for point in data]
        x = [point[2][0] for point in data]
        y = [-point[2][1] for point in data]
        t2 = [point[0] for point in data2]
        x2 = [point[2][0] for point in data2]
        y2 = [-point[2][1] for point in data2]
        xP = pivot[0]
        yP = pivot[1]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plot the trajectory: x and y positions with time into the page
        ax.plot(x, t, y, label=label, color='b')
        ax.plot(x2, t2, y2, label=label2, color='r')
        ax.plot(xP, t, yP, label=pivotLabel, color='g')

        ax.set_box_aspect((3, 7, 2))

        # Label axes
        ax.set_xlabel('X Position')
        ax.set_ylabel('Time')
        ax.set_zlabel('Y Position')

        # Add a legend and display the plot
        ax.legend()
        plt.show()

    def plot_graph(data, title):
        times = [point[0] for point in data]
        angles = [math.degrees(point[1]) for point in data]
        
        plt.figure(figsize=(8, 6))
        plt.plot(times, angles, linestyle='-', color='b')
        plt.xlabel("Time (seconds)")
        plt.ylabel("Angle (degrees)")
        plt.title(title)
        plt.grid(True)
        plt.show()

    def plot_graph_comparison(data, data2, title):
        times = [point[0] for point in data]
        angles = [math.degrees(point[1]) for point in data]
        times2 = [point[0] for point in data2]
        angles2 = [math.degrees(point[1]) for point in data2]
        
        plt.figure(figsize=(8, 6))
        plt.plot(times, angles, linestyle='-', color='b', label='LED 1')
        plt.plot(times2, angles2, linestyle='-', color='r', label='LED 2')
        plt.xlabel("Time (seconds)")
        plt.ylabel("Angle (degrees)")
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.show()

    plot_graph(firstLED, f"LED 1 Angle {graph_title}")
    plot_graph(secondLED, f"LED 2 Angle {graph_title}")
    plot_graph_comparison(firstLED, secondLED, graph_title)
    pos_time_graph(firstLED, secondLED, pivot, "LED 1", "LED 2", "Pivot Point")
    
else:
    cap = cv2.VideoCapture(f"{path_to_videos}{video_name}.AVI")
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

    def putTextOutline(img, text, org, font, fontScale, textColor, thickness, outlineColor, outlineThickness):
        # Draw the outline first
        cv2.putText(img, text, org, font, fontScale, outlineColor, outlineThickness, cv2.LINE_AA)
        # Then draw the text on top
        cv2.putText(img, text, org, font, fontScale, textColor, thickness, cv2.LINE_AA)

    def putBoxOutline(img, contour, color, outlineColor, boxThickness, outlineThickness):
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(img, (x, y), (x+w+8, y+h+8), outlineColor, outlineThickness)
        cv2.rectangle(img, (x, y), (x+w+8, y+h+8), color, boxThickness)

    # Initialize previous positions with the initially clicked points
    previous_first_position = middle_point
    previous_second_position = end_point

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Use grayscale thresholding to detect bright LEDs
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Use 140 for low aperture videos like DSC_0059, 245 for any other videos
        _, thresh = cv2.threshold(gray, brightness_value, 255, cv2.THRESH_BINARY)
        
        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
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
                # This contour is identified as LED1
                current_first_position = (cX, cY)
                putTextOutline(frame, "LED1", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, (0, 0, 0), 5)
                #x, y, w, h = cv2.boundingRect(cnt)
                #cv2.rectangle(frame, (x, y), (x+w+4, y+h+4), (255, 255, 255), 2)
                putBoxOutline(frame, cnt, (255, 255, 255), (0, 0, 0), 2, 6)
            else:
                # This contour is identified as LED2
                current_second_position = (cX, cY)
                putTextOutline(frame, "LED2", (100, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, (255, 255, 255), 5)
                #x, y, w, h = cv2.boundingRect(cnt)
                #cv2.rectangle(frame, (x, y), (x+w+4, y+h+4), (0, 0, 0), 2)
                putBoxOutline(frame, cnt, (0, 0, 0), (255, 255, 255), 2, 4)


        # Fallback in case no LED was detected in this frame
        if current_first_position is None:
            current_first_position = previous_first_position
        if current_second_position is None:
            current_second_position = previous_second_position

        # Get frame time
        frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        fps = cap.get(cv2.CAP_PROP_FPS)
        time_value = frame_index / fps

        # LED1 angle from the pivot point:
        theta1 = math.atan2(current_first_position[0] - reference_point[0], current_first_position[1] - reference_point[1])
        # LED2 angle from LED1 (relative to vertical at LED1):
        theta2 = math.atan2(current_second_position[0] - current_first_position[0], current_second_position[1] - current_first_position[1])
        # Append the computed angles with their timestamp, also the (x,y) position for some more interesting graphs
        firstLED.append((time_value, theta1, current_first_position))
        secondLED.append((time_value, theta2, current_second_position))

        # Update previous positions for next frame
        previous_first_position = current_first_position
        previous_second_position = current_second_position

        cv2.imshow("Original with LED Coordinates", frame)
        key = cv2.waitKey(30) & 0xFF
        if key == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()

    with open(f"{path_to_data}{video_name}.txt", "w") as file:
        file.write("Pivot:" + json.dumps(reference_point) + "\n")
        file.write("firstLED:" + json.dumps(firstLED) + "\n")
        file.write("secondLED:" + json.dumps(secondLED))

    # Graphing functions
    def pos_time_graph(data, data2, pivot, label, label2, pivotLabel):
        t = [point[0] for point in data]
        x = [point[2][0] for point in data]
        y = [-point[2][1] for point in data]
        t2 = [point[0] for point in data2]
        x2 = [point[2][0] for point in data2]
        y2 = [-point[2][1] for point in data2]
        xP = pivot[0]
        yP = pivot[1]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plot the trajectory: x and y positions with time into the page
        ax.plot(x, t, y, label=label, color='b')
        ax.plot(x2, t2, y2, label=label2, color='r')
        ax.plot(xP, t, yP, label=pivotLabel, color='g')

        ax.set_box_aspect((3, 7, 2))

        # Label axes
        ax.set_xlabel('X Position')
        ax.set_ylabel('Time')
        ax.set_zlabel('Y Position')

        # Add a legend and display the plot
        ax.legend()
        plt.show()

    def plot_graph(data, title):
        times = [point[0] for point in data]
        angles = [math.degrees(point[1]) for point in data]
        
        plt.figure(figsize=(8, 6))
        plt.plot(times, angles, linestyle='-', color='b')
        plt.xlabel("Time (seconds)")
        plt.ylabel("Angle (degrees)")
        plt.title(title)
        plt.grid(True)
        plt.show()

    def plot_graph_comparison(data, data2, title):
        times = [point[0] for point in data]
        angles = [math.degrees(point[1]) for point in data]
        times2 = [point[0] for point in data2]
        angles2 = [math.degrees(point[1]) for point in data2]
        
        plt.figure(figsize=(8, 6))
        plt.plot(times, angles, linestyle='-', color='b', label='LED 1')
        plt.plot(times2, angles2, linestyle='-', color='r', label='LED 2')
        plt.xlabel("Time (seconds)")
        plt.ylabel("Angle (degrees)")
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_graph(data, title):
        times = [point[0] for point in data]
        angles = [math.degrees(point[1]) for point in data]
        
        plt.figure(figsize=(8, 6))
        plt.plot(times, angles, linestyle='-', color='b')
        plt.xlabel("Time (seconds)")
        plt.ylabel("Angle (degrees)")
        plt.title(title)
        plt.grid(True)
        plt.show()

    def plot_graph_comparison(data, data2, title):
        times = [point[0] for point in data]
        angles = [math.degrees(point[1]) for point in data]
        times2 = [point[0] for point in data2]
        angles2 = [math.degrees(point[1]) for point in data2]
        
        plt.figure(figsize=(8, 6))
        plt.plot(times, angles, linestyle='-', color='b', label='LED 1')
        plt.plot(times2, angles2, linestyle='-', color='r', label='LED 2')
        plt.xlabel("Time (seconds)")
        plt.ylabel("Angle (degrees)")
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.show()

    plot_graph(firstLED, f"LED 1 Angle {graph_title}")
    plot_graph(secondLED, f"LED 2 Angle {graph_title}")
    plot_graph_comparison(firstLED, secondLED, graph_title)
    pos_time_graph(firstLED, secondLED, reference_point, "LED 1", "LED 2", "Pivot Point")