import matplotlib.pyplot as plt
import numpy as np
import math
import json
from typing import Tuple, List, NamedTuple

CONFIG = {
    "title": "Verification of the Simulation with Respect to Real Life",
    "path_to_data": "C:\\Users\\adamf\\Downloads\\",
    "sim_data_name": "simulation_99eca7f166d6a14cf96786b53cc3b9aacca062bd6ec066104e0fa7f0e56599c1.txt",
    "vid_data_name": "DSC_0058.txt",
    "ver_outpath": "./Verification/ver_outfiles/"
}

class PendulumData(NamedTuple):
    time: float
    angle: float
    position: Tuple[float, float]

Point = Tuple[int, int]
LEDData = List[Tuple[float, float, Point]]
CartesianCoords = Tuple[float, float, float, float]

def get_vid_data_path() -> str:
    return f"{CONFIG['path_to_data']}{CONFIG['vid_data_name']}"

def get_data_sim_path() -> str:
    return f"{CONFIG['path_to_data']}{CONFIG['sim_data_name']}"

def load_saved_vid_data() -> Tuple[Point, LEDData, LEDData]:
    with open(get_vid_data_path(), "r") as f:
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

def load_saved_data() -> dict:
    with open(get_data_sim_path(), "r") as f:
        data = json.load(f)
        return {
            "y": np.array(data["y"]),
            "t": np.array(data["t"]),
            "lengths": np.array(data["lengths"])
        }
    
def get_cartesian_coords(theta1: float, theta2: float, lengths: Tuple) -> CartesianCoords:
    x1 = lengths[0] * np.sin(theta1)
    y1 = -lengths[0] * np.cos(theta1)
    x2 = x1 + lengths[1] * np.sin(theta2)
    y2 = y1 - lengths[1] * np.cos(theta2)
    return x1, y1, x2, y2


def process_pendulum_data(solution: dict) -> Tuple[List[PendulumData], List[PendulumData]]:
    theta1 = solution["y"][0]
    theta2 = solution["y"][1]
    times = solution["t"]
    
    arm1_data = [
        PendulumData(t, math.atan2(x, (-y)), (x, y))
        for t, x, y in zip(times, *get_cartesian_coords(theta1, theta2, (solution["lengths"][0],solution["lengths"][1]))[:2])
    ]
    
    arm2_data = [
        PendulumData(t, math.atan2(x, (-y)), (x, y))
        for t, x, y in zip(times, *get_cartesian_coords(theta1, theta2, (solution["lengths"][0],solution["lengths"][1]))[2:])
    ]
    
    return arm1_data, arm2_data


def plot_deviation(
    arm1: List[PendulumData], 
    arm2: List[PendulumData], 
    data1: LEDData, 
    data2: LEDData
) -> None:
    # Convert simulation data to arrays
    sim_times = np.array([d.time for d in arm1])
    sim_ang1 = np.array([math.degrees(d.angle) for d in arm1])
    sim_ang2 = np.array([math.degrees(d.angle) for d in arm2])
    
    # Convert video data to arrays
    vid_times = np.array([d[0] for d in data1])
    vid_ang1 = np.array([math.degrees(d[1]) for d in data1])
    vid_ang2 = np.array([math.degrees(d[1]) for d in data2])

    # Detect motion start in video data
    def find_motion_start(angles: np.ndarray, window_size=5, threshold=1.0):
        diffs = np.abs(np.diff(angles))
        moving_avg = np.convolve(diffs, np.ones(window_size)/window_size, mode='valid')
        start_idx = np.argmax(moving_avg > threshold) + window_size
        return max(start_idx, 0)  # Ensure we don't get negative index

    start_idx = find_motion_start(vid_ang1)

    # Trim video data to motion period
    vid_times = vid_times[start_idx:] - vid_times[start_idx]  # Make time start at 0
    vid_ang1 = vid_ang1[start_idx:]
    vid_ang2 = vid_ang2[start_idx:]

    # Adjust simulation data to match video start
    sim_start_time = sim_times[np.argmin(np.abs(sim_times - vid_times[0]))]
    sim_mask = sim_times >= sim_start_time
    sim_times = sim_times[sim_mask] - sim_start_time
    sim_ang1 = sim_ang1[sim_mask]
    sim_ang2 = sim_ang2[sim_mask]

    # Interpolate simulation data to video timestamps
    interp_ang1 = np.interp(vid_times, sim_times, sim_ang1)
    interp_ang2 = np.interp(vid_times, sim_times, sim_ang2)
    
    # Calculate differences
    diff1 = vid_ang1 - interp_ang1
    diff2 = vid_ang2 - interp_ang2
    
    # Create plot
    plt.figure(figsize=(24, 6))
    plt.plot(vid_times, diff1, label="Arm 1 Deviation", color='b')
    plt.plot(vid_times, diff2, label="Arm 2 Deviation", color='r')
    
    plt.xlabel("Time from Motion Start (seconds)")
    plt.ylabel("Angle Difference (degrees)")
    plt.title(f"{CONFIG['title']}")
    plt.legend()
    plt.grid(True)
    
    plt.savefig(f"{CONFIG['ver_outpath']}{CONFIG['title']}.png")
    plt.show()

def main():
    sim = load_saved_data()
    arm1, arm2 = process_pendulum_data(sim)
    pivot, first, second = load_saved_vid_data()

    plot_deviation(arm1, arm2, first, second)


if __name__ == "__main__":
    main()