import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from matplotlib.animation import FuncAnimation, PillowWriter
from typing import NamedTuple, Tuple, List
import math
import os
import json
import hashlib

CONFIG = {
    "title": "Chaotic Pendulum Oscillation",
    "sim_outpath": "./Simulations/sim_outfiles/",
    "path_to_data": "C:\\Users\\adamf\\Downloads\\",
    "params": {
        "masses": (1.137, 1.455),
        "lengths": (0.525, 0.473),
        "gravity": 9.81,
        "initial_angles": (1.58544729307629, 0.007936341307466063), 
        "initial_velocities": (0.0, 0.0), 
        "time_span": (0.0, 40.0),
        "num_points": 4000,
        "solver": {
            "method": "Radau",
            "rtol": 1e-9,
            "atol": 1e-10
        }
    }
}

class PendulumData(NamedTuple):
    time: float
    angle: float
    position: Tuple[float, float]

StateVector = Tuple[float, float, float, float]
CartesianCoords = Tuple[float, float, float, float]

def get_solver_params() -> dict:
    return CONFIG["params"]["solver"]

def get_data_path() -> str:
    # Convert tuples to lists for consistent hashing
    params = CONFIG["params"].copy()
    for key in ["masses", "lengths", "initial_angles", "initial_velocities"]:
        if isinstance(params[key], tuple):
            params[key] = list(params[key])
    
    param_hash = hashlib.sha256(
        json.dumps(params, sort_keys=True).encode()
    ).hexdigest()
    return f"{CONFIG['path_to_data']}simulation_{param_hash}.txt"

def equations_of_motion(t: float, y: StateVector) -> List[float]:
    m1, m2 = CONFIG["params"]["masses"]
    l1, l2 = CONFIG["params"]["lengths"]
    g = CONFIG["params"]["gravity"]
    theta1, theta2, omega1, omega2 = y
    
    denominator = l1*(m1 + 4*m2) - 4*m2*l1*np.cos(theta1 - theta2)**2
    numerator = (
        -6*(m1 + 2*m2)*g*np.sin(theta1)
        - 2*m2*l1*omega1**2*np.sin(2*(theta1 - theta2))
        + 12*m2*g*np.sin(theta2)*np.cos(theta1 - theta2)
        - 2*m2*l2*omega2**2*np.sin(theta1 - theta2)
    )
    ddtheta1 = numerator / denominator
    
    ddtheta2 = (
        -2*(l1/l2)*ddtheta1*np.cos(theta1 - theta2)
        + 2*(l1/l2)*omega1**2*np.sin(theta1 - theta2)
        - 6*(g/l2)*np.sin(theta2)
    )

    return [omega1, omega2, ddtheta1, ddtheta2]

def save_data(solution: dict, lengths: Tuple) -> None:
    data = {
        "y": solution["y"].tolist(),
        "t": solution["t"].tolist(),
        "lengths": list(lengths)
    }
    with open(get_data_path(), "w") as f:
        json.dump(data, f)

def load_saved_data() -> dict:
    with open(get_data_path(), "r") as f:
        data = json.load(f)
        return {
            "y": np.array(data["y"]),
            "t": np.array(data["t"])
        }

def solve_pendulum_ode() -> Tuple[dict, Tuple]:
    t_span = CONFIG["params"]["time_span"]
    t_eval = np.linspace(*t_span, CONFIG["params"]["num_points"])
    y0 = (*CONFIG["params"]["initial_angles"], *CONFIG["params"]["initial_velocities"])
    
    sol = solve_ivp(
        fun=equations_of_motion,
        t_span=t_span,
        y0=y0,
        t_eval=t_eval,
        **get_solver_params()
    )
    return {
        "y": sol.y,
        "t": sol.t
    }, (CONFIG["params"]["lengths"])

def get_cartesian_coords(theta1: float, theta2: float) -> CartesianCoords:
    l1, l2 = CONFIG["params"]["lengths"]
    x1 = l1 * np.sin(theta1)
    y1 = -l1 * np.cos(theta1)
    x2 = x1 + l2 * np.sin(theta2)
    y2 = y1 - l2 * np.cos(theta2)
    return x1, y1, x2, y2

def create_animation(solution: dict) -> FuncAnimation:
    theta1 = solution["y"][0]
    theta2 = solution["y"][1]
    times = solution["t"]
    
    fig, ax = plt.subplots()
    ax.set_xlim(-sum(CONFIG["params"]["lengths"]), sum(CONFIG["params"]["lengths"]))
    ax.set_ylim(-sum(CONFIG["params"]["lengths"]), sum(CONFIG["params"]["lengths"]))
    ax.set_aspect('equal')
    line, = ax.plot([], [], 'o-', lw=2)
    
    def init():
        line.set_data([], [])
        return (line,) 
    
    def update(frame: int):
        x1, y1, x2, y2 = get_cartesian_coords(theta1[frame], theta2[frame])
        line.set_data([0, x1, x2], [0, y1, y2])
        return (line,) 
    
    ani = FuncAnimation(
        fig, 
        update, 
        frames=len(times),
        init_func=init, 
        blit=True, 
        interval=20
    )
    
    os.makedirs(CONFIG["sim_outpath"], exist_ok=True)
    ani.save(f"{CONFIG['sim_outpath']}{CONFIG['title']}.gif", 
            writer=PillowWriter(fps=15, bitrate=1800))
    plt.show()
    return ani

def process_pendulum_data(solution: dict) -> Tuple[List[PendulumData], List[PendulumData]]:
    theta1 = solution["y"][0]
    theta2 = solution["y"][1]
    times = solution["t"]
    
    arm1_data = []
    arm2_data = []
    
    # Iterate through each time step's angles
    for t, th1, th2 in zip(times, theta1, theta2):
        # Get coordinates for both masses
        x1, y1, x2, y2 = get_cartesian_coords(th1, th2)
        
        # Arm 1: Angle is relative to the origin (0,0)
        angle1 = math.atan2(x1, -y1)
        arm1_data.append(PendulumData(t, angle1, (x1, y1)))
        
        # Arm 2: Angle is relative to the end of Arm 1 (x1, y1)
        dx = x2 - x1  # Horizontal displacement from Arm 1's end
        dy = y2 - y1  # Vertical displacement from Arm 1's end
        angle2 = math.atan2(dx, -dy)  # Negative because positive y is downward
        arm2_data.append(PendulumData(t, angle2, (x2, y2)))
    
    return arm1_data, arm2_data

def plot_angle_comparison(arm1: List[PendulumData], arm2: List[PendulumData]) -> None:
    plt.figure(figsize=(24, 6))
    plt.plot(
        [d.time for d in arm1], [math.degrees(d.angle) for d in arm1], 
        label="Arm 1", color='b'
    )
    plt.plot(
        [d.time for d in arm2], [math.degrees(d.angle) for d in arm2], 
        label="Arm 2", color='r'
    )

    plt.xlabel("Time (seconds)")
    plt.ylabel("Angle (degrees)")
    plt.title(f"Angle Comparison - {CONFIG['title']}")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{CONFIG['sim_outpath']}Angle Comparison - {CONFIG['title']}.png")
    plt.show()

def plot_3d_trajectory(arm1: List[PendulumData], arm2: List[PendulumData]) -> None:
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    ax.plot(0, [d.time for d in arm1], 0, label="Pivot", color="g")

    ax.plot(
        [d.position[0] for d in arm1],
        [d.time for d in arm1],
        [d.position[1] for d in arm1],
        label="Arm 1", color='b'
    )
    
    ax.plot(
        [d.position[0] for d in arm2],
        [d.time for d in arm2],
        [d.position[1] for d in arm2],
        label="Arm 2", color='r'
    )
    
    ax.set_xlabel("X Position")
    ax.set_ylabel("Time")
    ax.set_zlabel("Y Position")
    ax.legend()
    ax.set_box_aspect((3, 7, 2))
    plt.savefig(f"{CONFIG['sim_outpath']}3D Trajectory - {CONFIG['title']}.png")
    plt.show()

def compute_energy(solution: dict):
    theta1 = solution["y"][0]
    theta2 = solution["y"][1]
    omega1 = solution["y"][2]
    omega2 = solution["y"][3]
    t = solution["t"]

    m1, m2 = CONFIG["params"]["masses"]
    l1, l2 = CONFIG["params"]["lengths"]
    g = CONFIG["params"]["gravity"]

    T = ((1/24)*(m1 + 4*m2)*(l1**2)*(omega1**2) + 
         (1/24)*m2*(l2**2)*(omega2**2) + 
         (1/6)*m2*l1*l2*omega1*omega2*np.cos(theta1 - theta2))

    V = -((1/2)*(m1 + 2*m2)*g*l1*np.cos(theta1)) - (1/2)*m2*g*l2*np.cos(theta2)

    E = T + V
    return t, T, V, E

def plot_energy(solution: dict):
    t, T, V, E = compute_energy(solution)
    
    plt.figure(figsize=(24, 6))
    plt.plot(t, T, label="Kinetic Energy", color='g')
    plt.plot(t, V, label="Potential Energy", color='orange')
    plt.plot(t, E, label="Total Energy", linestyle="--", color='blue')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Energy (Joules)")
    plt.title(f"Energy vs Time - {CONFIG['title']}")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{CONFIG['sim_outpath']}Energy Analysis - {CONFIG['title']}.png")
    plt.show()

def main():
    data_path = get_data_path()
    
    if os.path.exists(data_path):
        solution = load_saved_data()
        arm1_data, arm2_data = process_pendulum_data(solution)
    else:
        solution, lengths = solve_pendulum_ode()
        arm1_data, arm2_data = process_pendulum_data(solution)
        save_data(solution, lengths)
        create_animation(solution)
    
    plot_angle_comparison(arm1_data, arm2_data)
    plot_3d_trajectory(arm1_data, arm2_data)
    plot_energy(solution)

if __name__ == "__main__":
    main()