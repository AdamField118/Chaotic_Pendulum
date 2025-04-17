import matplotlib.pyplot as plt
import numpy as np
import math
import json
from pathlib import Path
from typing import Tuple, List, NamedTuple, Dict, Any
from scipy.optimize import curve_fit

CONFIG = {
    "title": "Verification of the Simulation with Respect to Real Life",
    "path_to_data": "C:\\Users\\adamf\\Downloads\\",
    "sim_data_name": "simulation_45df02e102a7b311c45a387d97d3856f720a1adcfb1d30d1a41ff66d88e170a0.txt",
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

def get_vid_data_path() -> Path:
    """Return the full path to the video data file."""
    return Path(CONFIG['path_to_data']) / CONFIG['vid_data_name']

def get_data_sim_path() -> Path:
    """Return the full path to the simulation data file."""
    return Path(CONFIG['path_to_data']) / CONFIG['sim_data_name']

def load_saved_vid_data() -> Tuple[Point, LEDData, LEDData]:
    """Load and parse video data from the configured file."""
    pivot, first_led, second_led = None, [], []
    with open(get_vid_data_path(), "r") as f:
        for line in f:
            key, value = line.split(":", 1)
            if key == "Pivot":
                pivot = json.loads(value)
            elif key == "firstLED":
                first_led = json.loads(value)
            elif key == "secondLED":
                second_led = json.loads(value)
    return pivot, first_led, second_led

def load_saved_data() -> Dict[str, Any]:
    """Load simulation data from the configured JSON file."""
    with open(get_data_sim_path(), "r") as f:
        data = json.load(f)
    return {
        "y": np.array(data["y"]),
        "t": np.array(data["t"]),
        "lengths": np.array(data["lengths"])
    }

def get_cartesian_coords(theta1: np.ndarray, theta2: np.ndarray, lengths: Tuple[float, float]) -> CartesianCoords:
    """Calculate Cartesian coordinates for both pendulum masses using vectorized operations."""
    l1, l2 = lengths
    x1 = l1 * np.sin(theta1)
    y1 = -l1 * np.cos(theta1)
    x2 = x1 + l2 * np.sin(theta2)
    y2 = y1 - l2 * np.cos(theta2)
    return x1, y1, x2, y2

def process_pendulum_data(solution: Dict[str, Any]) -> Tuple[List[PendulumData], List[PendulumData]]:
    """Process simulation data to generate pendulum trajectories using vectorized operations."""
    theta1 = solution["y"][0]
    theta2 = solution["y"][1]
    times = solution["t"]
    lengths = (solution["lengths"][0], solution["lengths"][1])

    x1, y1, x2, y2 = get_cartesian_coords(theta1, theta2, lengths)
    
    # Calculate angles using vectorized operations
    angle1 = np.arctan2(x1, -y1)
    dx = x2 - x1
    dy = y2 - y1
    angle2 = np.arctan2(dx, -dy)
    
    # Create pendulum data lists
    arm1_data = [
        PendulumData(t, a1, (x, y))
        for t, a1, x, y in zip(times, angle1, x1, y1)
    ]
    arm2_data = [
        PendulumData(t, a2, (x, y))
        for t, a2, x, y in zip(times, angle2, x2, y2)
    ]
    return arm1_data, arm2_data

def find_motion_start(angles: np.ndarray, window_size: int = 5, threshold: float = 1.0) -> int:
    """Detect the start of motion using moving average of angular differences."""
    if len(angles) < 2:
        return 0
    diffs = np.abs(np.diff(angles))
    if len(diffs) < window_size:
        return 0
    moving_avg = np.convolve(diffs, np.ones(window_size)/window_size, mode='valid')
    above_threshold = moving_avg > threshold
    if not np.any(above_threshold):
        return 0
    start_idx = np.argmax(above_threshold) + window_size
    return min(start_idx, len(angles) - 1)

def process_arm(vid_data: LEDData, sim_data: List[PendulumData]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Process and align video/simulation data for a single pendulum arm."""
    vid_t = np.array([d[0] for d in vid_data])
    angles_rad = np.array([d[1] for d in vid_data])
    vid_angles = np.degrees(angles_rad)
    
    start_idx = find_motion_start(vid_angles)
    vid_t_trimmed = vid_t[start_idx:] - vid_t[start_idx]
    vid_angles_trimmed = vid_angles[start_idx:]
    max_time = vid_t_trimmed[-1] if len(vid_t_trimmed) > 0 else 0.0

    sim_t = np.array([d.time for d in sim_data])
    sim_angles_rad = np.array([d.angle for d in sim_data])
    sim_angles = np.degrees(sim_angles_rad)
    sim_mask = sim_t <= max_time
    return (vid_t_trimmed, vid_angles_trimmed, sim_t[sim_mask], sim_angles[sim_mask])

def plot_deviation(arm1: List[PendulumData], arm2: List[PendulumData], 
                  data1: LEDData, data2: LEDData) -> None:
    """Plot angle deviation between video and simulation data using Fourier approximations."""
    vid_t1, vid_ang1, sim_t1, sim_ang1 = process_arm(data1, arm1)
    vid_t2, vid_ang2, sim_t2, sim_ang2 = process_arm(data2, arm2)

    def fit_and_extend(t: np.ndarray, y: np.ndarray, evaluation_t: np.ndarray) -> np.ndarray:
        if len(t) < 2:
            return np.zeros_like(evaluation_t)
        coeffs, _ = fit_fourier(t, y)
        T = t[-1] if len(t) > 0 else 1.0
        return fourier_series(evaluation_t, T, *coeffs)

    max_time = min(np.max(vid_t1) if len(vid_t1) else 0, np.max(vid_t2) if len(vid_t2) else 0,
                   np.max(sim_t1) if len(sim_t1) else 0, np.max(sim_t2) if len(sim_t2) else 0)
    common_t = np.linspace(0, max_time, 1000) if max_time > 0 else np.array([])

    vid_fit1 = fit_and_extend(vid_t1, vid_ang1, common_t)
    sim_fit1 = fit_and_extend(sim_t1, sim_ang1, common_t)
    vid_fit2 = fit_and_extend(vid_t2, vid_ang2, common_t)
    sim_fit2 = fit_and_extend(sim_t2, sim_ang2, common_t)

    plt.figure(figsize=(24, 6))
    plt.plot(common_t, vid_fit1 - sim_fit1, label="Arm 1 Deviation", color='b', alpha=0.7)
    plt.plot(common_t, vid_fit2 - sim_fit2, label="Arm 2 Deviation", color='r', alpha=0.7)
    plt.xlabel("Time from Motion Start (seconds)")
    plt.ylabel("Angle Difference (degrees)")
    plt.title(f"{CONFIG['title']} - Fourier-based Deviation")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{CONFIG['ver_outpath']}Fourier_Deviation_{CONFIG['title']}.png")
    plt.show()

def fourier_series(t: np.ndarray, T: float, *coefficients) -> np.ndarray:
    """Evaluate Fourier series with given coefficients and period T at times t."""
    T = max(T, 1e-6)  # Prevent division by zero
    result = coefficients[0] * np.ones_like(t) if coefficients else np.zeros_like(t)
    n_terms = len(coefficients) // 2
    for n in range(1, n_terms + 1):
        a = coefficients[2*n-1] if (2*n-1) < len(coefficients) else 0.0
        b = coefficients[2*n] if 2*n < len(coefficients) else 0.0
        result += a * np.cos(2 * n * np.pi * t / T) + b * np.sin(2 * n * np.pi * t / T)
    return result

def fit_fourier(t: np.ndarray, y: np.ndarray, num_terms: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """Fit Fourier series to data and return coefficients and fitted values."""
    T = t[-1] if len(t) > 0 else 1.0
    initial_guess = [np.mean(y)] + [0.0] * (2 * num_terms)
    popt, _ = curve_fit(
        lambda t_, *coeffs: fourier_series(t_, T, *coeffs),
        t, y, p0=initial_guess, maxfev=10000
    )
    return popt, fourier_series(t, T, *popt)

def plot_fourier_comparison(vid_data: LEDData, sim_data: List[PendulumData], 
                            arm_num: int, num_terms: int = 499) -> None:
    """Plot Fourier series comparison between video and simulation data for a single arm."""
    vid_t, vid_ang, sim_t, sim_ang = process_arm(vid_data, sim_data)
    vid_coeffs, vid_fit = fit_fourier(vid_t, vid_ang, num_terms)
    sim_coeffs, sim_fit = fit_fourier(sim_t, sim_ang, num_terms)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(24, 12), sharex=True)
    ax1.scatter(vid_t, vid_ang, s=10, color='blue', alpha=0.5, label='Video Data')
    ax1.plot(vid_t, vid_fit, 'r-', lw=2, label=f'Fourier Fit ({num_terms} terms)')
    ax1.set_ylabel("Angle (degrees)")
    ax1.legend()
    ax1.grid(True)
    
    ax2.scatter(sim_t, sim_ang, s=10, color='green', alpha=0.5, label='Simulation Data')
    ax2.plot(sim_t, sim_fit, 'orange', lw=2, label=f'Fourier Fit ({num_terms} terms)')
    ax2.set_xlabel("Time from Motion Start (seconds)")
    ax2.set_ylabel("Angle (degrees)")
    ax2.legend()
    ax2.grid(True)
    

    plt.suptitle(f"Arm {arm_num} - Fourier Series Comparison")
    plt.tight_layout()
    plt.savefig(f"{CONFIG['ver_outpath']}Fourier_Comparison_Arm{arm_num}.png")
    plt.show()

def main():
    sim_data = load_saved_data()
    arm1, arm2 = process_pendulum_data(sim_data)
    pivot, first_led, second_led = load_saved_vid_data()

    plot_fourier_comparison(first_led, arm1, arm_num=1)
    plot_fourier_comparison(second_led, arm2, arm_num=2)
    plot_deviation(arm1, arm2, first_led, second_led)

if __name__ == "__main__":
    main()