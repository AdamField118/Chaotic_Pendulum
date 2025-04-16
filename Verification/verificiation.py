import matplotlib.pyplot as plt
import numpy as np
import math
import json
from typing import Tuple, List, NamedTuple
from scipy.optimize import curve_fit

CONFIG = {
    "title": "Verification of the Simulation with Respect to Real Life",
    "path_to_data": "C:\\Users\\adamf\\Downloads\\",
    "sim_data_name": "simulation_4fa2850890bf9769841974f080a31e603689af602b49631c0da0913405acc2b2.txt",
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
    
    arm1_data = []
    arm2_data = []
    
    # Iterate through each time step's angles
    for t, th1, th2 in zip(times, theta1, theta2):
        # Get coordinates for both masses
        x1, y1, x2, y2 = get_cartesian_coords(th1, th2, (solution["lengths"][0],solution["lengths"][1]))
        
        # Arm 1: Angle is relative to the origin (0,0)
        angle1 = math.atan2(x1, -y1)
        arm1_data.append(PendulumData(t, angle1, (x1, y1)))
        
        # Arm 2: Angle is relative to the end of Arm 1 (x1, y1)
        dx = x2 - x1  # Horizontal displacement from Arm 1's end
        dy = y2 - y1  # Vertical displacement from Arm 1's end
        angle2 = math.atan2(dx, -dy)  # Negative because positive y is downward
        arm2_data.append(PendulumData(t, angle2, (x2, y2)))
    
    return arm1_data, arm2_data

def plot_deviation(
    arm1: List[PendulumData], 
    arm2: List[PendulumData], 
    data1: LEDData, 
    data2: LEDData
) -> None:
    def process_arm(vid_data: LEDData, sim_data: List[PendulumData]):
        # Extract video data
        vid_t = np.array([d[0] for d in vid_data])
        vid_angles = np.array([math.degrees(d[1]) for d in vid_data])
        
        # Detect motion start in video data
        def find_motion_start(angles: np.ndarray, window_size=5, threshold=1.0):
            diffs = np.abs(np.diff(angles))
            moving_avg = np.convolve(diffs, np.ones(window_size)/window_size, mode='valid')
            start_idx = np.argmax(moving_avg > threshold) + window_size
            return max(start_idx, 0)
        
        start_idx = find_motion_start(vid_angles)
        vid_t_trimmed = vid_t[start_idx:] - vid_t[start_idx]  # Start time at 0
        vid_angles_trimmed = vid_angles[start_idx:]

        # Align simulation data
        sim_t = np.array([d.time for d in sim_data])
        sim_angles = np.array([math.degrees(d.angle) for d in sim_data])
        sim_mask = sim_t >= vid_t[start_idx]
        sim_t_aligned = sim_t[sim_mask] - sim_t[sim_mask][0]
        sim_angles_aligned = sim_angles[sim_mask]

        return (vid_t_trimmed, vid_angles_trimmed, 
                sim_t_aligned, sim_angles_aligned)

    # Process both arms
    (vid_t1, vid_ang1, sim_t1, sim_ang1) = process_arm(data1, arm1)
    (vid_t2, vid_ang2, sim_t2, sim_ang2) = process_arm(data2, arm2)

    # Fit Fourier series to all datasets
    def fit_and_extend(t: np.ndarray, y: np.ndarray, evaluation_t: np.ndarray):
        if len(t) < 2:
            return np.zeros_like(evaluation_t)

        # Get coefficients and period from original data
        coeffs, fitted_curve = fit_fourier(t, y)
        T = t[-1] if len(t) > 0 else 1.0  # Handle empty array case

        # Use the original period when evaluating
        return fourier_series(evaluation_t, T, *coeffs)

    # Create common time axis
    max_time = min(vid_t1[-1], vid_t2[-1], sim_t1[-1], sim_t2[-1])
    common_t = np.linspace(0, max_time, 1000)

    # Get Fourier approximations
    vid_fit1 = fit_and_extend(vid_t1, vid_ang1, common_t)
    sim_fit1 = fit_and_extend(sim_t1, sim_ang1, common_t)
    vid_fit2 = fit_and_extend(vid_t2, vid_ang2, common_t)
    sim_fit2 = fit_and_extend(sim_t2, sim_ang2, common_t)

    # Calculate deviations
    diff1 = vid_fit1 - sim_fit1
    diff2 = vid_fit2 - sim_fit2

    # Create plot
    plt.figure(figsize=(24, 6))
    plt.plot(common_t, diff1, label="Arm 1 Deviation", color='b', alpha=0.7)
    plt.plot(common_t, diff2, label="Arm 2 Deviation", color='r', alpha=0.7)
    
    plt.xlabel("Time from Motion Start (seconds)")
    plt.ylabel("Angle Difference (degrees)")
    plt.title(f"{CONFIG['title']} - Fourier-based Deviation")
    plt.legend()
    plt.grid(True)
    
    plt.savefig(f"{CONFIG['ver_outpath']}Fourier_Deviation_{CONFIG['title']}.png")
    plt.show()

def fourier_series(t: np.ndarray, T: float, *coefficients) -> np.ndarray:
    """
    Create a Fourier series approximation with period T and coefficients.
    Format: coefficients = [a0, a1, b1, a2, b2, ..., an, bn]
    """
    if T <= 0:
        T = 1.0  # Prevent division by zero
    
    n_terms = len(coefficients) // 2
    result = coefficients[0] * np.ones_like(t)
    
    for n in range(1, n_terms+1):
        a = coefficients[2*n-1] if 2*n-1 < len(coefficients) else 0
        b = coefficients[2*n] if 2*n < len(coefficients) else 0
        result += a * np.cos(2*n*np.pi*t/T) + b * np.sin(2*n*np.pi*t/T)
    
    return result

def fit_fourier(t: np.ndarray, y: np.ndarray, num_terms: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """Return (coefficients, fitted_curve)"""
    # Calculate period from input data
    T = t[-1] if len(t) > 0 else 1.0
    
    # Initial guess for coefficients (a0, a1, b1, a2, b2, ...)
    initial_guess = [np.mean(y)] + [0.0]*(2*num_terms)
    
    # Set bounds to avoid runaway values
    bounds = ([-np.inf] + [-np.inf]*(2*num_terms), 
              [np.inf] + [np.inf]*(2*num_terms))
    
    # Perform the fit with correct period
    popt, _ = curve_fit(
        lambda t, *coeffs: fourier_series(t, T, *coeffs),
        t, y,
        p0=initial_guess,
        bounds=bounds,
        maxfev=10000
    )
    
    # Generate fitted curve with original period
    fitted_curve = fourier_series(t, T, *popt)
    return popt, fitted_curve

def plot_fourier_comparison(vid_data: LEDData, sim_data: List[PendulumData], 
                           arm_num: int, num_terms: int = 499) -> None:
    # Extract data based on arm number
    vid_t = np.array([d[0] for d in vid_data])
    vid_angles = np.array([math.degrees(d[1]) for d in vid_data])
    sim_t = np.array([d.time for d in sim_data])
    sim_angles = np.array([math.degrees(d.angle) for d in sim_data])

    # Detect motion start in video data (same as before)
    def find_motion_start(angles: np.ndarray, window_size=5, threshold=1.0):
        diffs = np.abs(np.diff(angles))
        moving_avg = np.convolve(diffs, np.ones(window_size)/window_size, mode='valid')
        start_idx = np.argmax(moving_avg > threshold) + window_size
        return max(start_idx, 0)

    start_idx = find_motion_start(vid_angles)
    vid_t = vid_t[start_idx:] - vid_t[start_idx]
    vid_angles = vid_angles[start_idx:]

    # Align simulation data with video timing
    sim_mask = sim_t >= vid_t[0]
    sim_t_aligned = sim_t[sim_mask] - sim_t[sim_mask][0]
    sim_angles_aligned = sim_angles[sim_mask]

    # Fit Fourier series to both datasets
    vid_coeffs, vid_fitted = fit_fourier(vid_t, vid_angles, num_terms)
    sim_coeffs, sim_fitted = fit_fourier(sim_t_aligned, sim_angles_aligned, num_terms)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(24, 12), sharex=True)
    
    # Video data plot
    ax1.scatter(vid_t, vid_angles, s=10, label='Video Data', 
               color='blue', alpha=0.5)
    ax1.plot(vid_t, vid_fitted, label=f'Fourier Fit ({num_terms} terms)', 
            color='red', linewidth=2)
    ax1.set_title(f"Arm {arm_num} - Video Data with Fourier Approximation")
    ax1.set_ylabel("Angle (degrees)")
    ax1.legend()
    ax1.grid(True)
    
    # Simulation data plot
    ax2.scatter(sim_t_aligned, sim_angles_aligned, s=10, 
               label='Simulation Data', color='green', alpha=0.5)
    ax2.plot(sim_t_aligned, sim_fitted, label=f'Fourier Fit ({num_terms} terms)', 
            color='orange', linewidth=2)
    ax2.set_title(f"Arm {arm_num} - Simulation Data with Fourier Approximation")
    ax2.set_xlabel("Time from Motion Start (seconds)")
    ax2.set_ylabel("Angle (degrees)")
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(f"{CONFIG['ver_outpath']}Fourier_Comparison_Arm{arm_num}.png")
    plt.show()

def main():
    sim = load_saved_data()
    arm1, arm2 = process_pendulum_data(sim)
    pivot, first, second = load_saved_vid_data()

    plot_fourier_comparison(first, arm1, arm_num=1)
    plot_fourier_comparison(second, arm2, arm_num=2)
    plot_deviation(arm1, arm2, first, second)

if __name__ == "__main__":
    main()