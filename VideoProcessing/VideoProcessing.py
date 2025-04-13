import cv2
import math
import matplotlib.pyplot as plt
import os
import json
import numpy as np
from typing import Tuple, List, Optional

# Configuration
CONFIG = {
    "video_name": "DSC_0059",
    "brightness_value": 140,
    "graph_title": "Chaotic Double Pendulum",
    "path_to_videos": "C:\\Users\\adamf\\OneDrive\\Desktop\\IPL\\Double Pendulum\\Videos\\",
    "path_to_data": "C:\\Users\\adamf\\Downloads\\",
    "video_extension": ".AVI"
}

Point = Tuple[int, int]
LEDData = List[Tuple[float, float, Point]]

def get_data_path() -> str:
    return f"{CONFIG['path_to_data']}{CONFIG['video_name']}.txt"

def get_video_path() -> str:
    return f"{CONFIG['path_to_videos']}{CONFIG['video_name']}{CONFIG['video_extension']}"

def select_point(image: np.ndarray, window_title: str) -> Optional[Point]:
    selected_point = None
    def callback(event, x, y, *args):
        nonlocal selected_point
        if event == cv2.EVENT_LBUTTONDOWN:
            selected_point = (x, y)
            cv2.destroyWindow(window_title)
    cv2.namedWindow(window_title)
    cv2.imshow(window_title, image)
    cv2.setMouseCallback(window_title, callback)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return selected_point

def load_saved_data() -> Tuple[Point, LEDData, LEDData]:
    with open(get_data_path(), "r") as f:
        pivot, first_led, second_led = None, [], []
        for line in f:
            key, value = line.split(":", 1)
            if key == "Pivot":
                pivot = json.loads(value)
            elif key == "firstLED":
                first_led = json.loads(value)
            elif key == "secondLED":
                second_led = json.loads(value)
        return pivot, first_led, second_led

def save_data(pivot: Point, first_led: LEDData, second_led: LEDData) -> None:
    with open(get_data_path(), "w") as f:
        f.write(f"Pivot:{json.dumps(pivot)}\n")
        f.write(f"firstLED:{json.dumps(first_led)}\n")
        f.write(f"secondLED:{json.dumps(second_led)}\n")

def process_frame(
    frame: np.ndarray,
    reference: Point,
    prev_pos: Tuple[Point, Point],
    brightness: int,
    arm_length: float
) -> Tuple[np.ndarray, Tuple[Point, Point]]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, brightness, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    current = [None, None]
    for cnt in filter(lambda c: 5 < cv2.contourArea(c) < 500, contours):
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cX, cY = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
        
        dist_pivot = math.hypot(cX - reference[0], cY - reference[1])
        dist_prev = [math.hypot(cX - p[0], cY - p[1]) for p in prev_pos]
        
        if (arm_length-20 <= dist_pivot <= arm_length+20) and (dist_prev[0] < dist_prev[1] + 20):
            current[0] = (cX, cY)
            put_text_outline(frame, "LED1", (100, 100), (255, 255, 255), (0, 0, 0))
            put_box_outline(frame, cnt, (255, 255, 255), (0, 0, 0))
        else:
            current[1] = (cX, cY)
            put_text_outline(frame, "LED2", (100, 120), (0, 0, 0), (255, 255, 255))
            put_box_outline(frame, cnt, (0, 0, 0), (255, 255, 255))

    current = [prev if curr is None else curr for curr, prev in zip(current, prev_pos)]
    return frame, current

def put_text_outline(
    img: np.ndarray,
    text: str,
    pos: Tuple[int, int],
    fg: Tuple[int, int, int],
    bg: Tuple[int, int, int]
) -> None:
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, bg, 5, cv2.LINE_AA)
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, fg, 2, cv2.LINE_AA)

def put_box_outline(
    img: np.ndarray,
    contour: np.ndarray,
    fg: Tuple[int, int, int],
    bg: Tuple[int, int, int]
) -> None:
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(img, (x, y), (x+w+8, y+h+8), bg, 5)
    cv2.rectangle(img, (x, y), (x+w+8, y+h+8), fg, 2)

def process_video() -> Tuple[Point, LEDData, LEDData]:
    cap = cv2.VideoCapture(get_video_path())
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Failed to read video")

    reference = select_point(frame, "Select Pivot Point")
    first_point = select_point(frame, "Select first LED")
    second_point = select_point(frame, "Select second LED")
    arm_length = math.hypot(first_point[0]-reference[0], first_point[1]-reference[1])

    prev_pos = [first_point, second_point]
    first_led, second_led = [], []
    fps = cap.get(cv2.CAP_PROP_FPS)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, current = process_frame(frame, reference, prev_pos, CONFIG["brightness_value"], arm_length)
        time_val = cap.get(cv2.CAP_PROP_POS_FRAMES) / fps
        
        theta1 = math.atan2(current[0][0]-reference[0], current[0][1]-reference[1])
        theta2 = math.atan2(current[1][0]-current[0][0], current[1][1]-current[0][1])
        
        first_led.append((time_val, theta1, current[0]))
        second_led.append((time_val, theta2, current[1]))
        prev_pos = current

        cv2.imshow("Processing", frame)
        if cv2.waitKey(30) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return reference, first_led, second_led

def plot_pos_time(data1: LEDData, data2: LEDData, pivot: Point) -> None:
    extract_x = lambda data: [p[2][0] for p in data]
    extract_y = lambda data: [-p[2][1] for p in data]
    extract_t = lambda data: [p[0] for p in data]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    ax.plot(extract_x(data1), extract_t(data1), extract_y(data1), 
            color='b', label='LED 1')
    
    ax.plot(extract_x(data2), extract_t(data2), extract_y(data2), 
            color='r', label='LED 2')
    
    t_points = extract_t(data1)
    ax.plot([pivot[0]]*len(t_points),  
            t_points, 
            [ -pivot[1]]*len(t_points),
            color='g', label='Pivot')

    ax.set_box_aspect((3, 7, 2))
    ax.set_xlabel('X Position')
    ax.set_ylabel('Time')
    ax.set_zlabel('Y Position')
    ax.legend()
    plt.show()

def plot_angles(data: LEDData, num: int) -> None:
    plt.figure(figsize=(8, 6))
    plt.plot([d[0] for d in data], [math.degrees(d[1]) for d in data], 'b')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Angle (degrees)")
    plt.title(f"LED {num}: {CONFIG['graph_title']}")
    plt.grid(True)
    plt.show()

def plot_comparison(data1: LEDData, data2: LEDData) -> None:
    plt.figure(figsize=(8, 6))
    plt.plot([d[0] for d in data1], [math.degrees(d[1]) for d in data1], 'b', label='LED 1')
    plt.plot([d[0] for d in data2], [math.degrees(d[1]) for d in data2], 'r', label='LED 2')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Angle (degrees)")
    plt.title(CONFIG["graph_title"])
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    data_path = get_data_path()
    if os.path.exists(data_path):
        pivot, first, second = load_saved_data()
    else:
        pivot, first, second = process_video()
        save_data(pivot, first, second)

    plot_angles(first, 1)
    plot_angles(second, 2)
    plot_comparison(first, second)
    plot_pos_time(first, second, pivot)

if __name__ == "__main__":
    main()