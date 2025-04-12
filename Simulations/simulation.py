import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from matplotlib.animation import FuncAnimation
import math
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import PillowWriter

title = 'Chaotic Pendulum Oscillation'
sim_outpath = './Simulations/sim_outfiles/'

# ----------------------------------------------------------
# 1. Define system parameters
# ----------------------------------------------------------
m1 = 5.0    # mass of first link
m2 = 4.0    # mass of second link
l1 = 0.525    # length of first link
l2 = 0.473   # length of second link
g  = 9.81   # gravitational acceleration

# ----------------------------------------------------------
# 2. Define the equations of motion using the provided equations
# ----------------------------------------------------------
def equations_of_motion(t, y):
    """
    Returns the time derivatives of [theta1, theta2, omega1, omega2]
    using the given equations of motion.
    y is [theta1, theta2, omega1, omega2].
    """
    theta1, theta2, omega1, omega2 = y

    '''
    \[
    \ddot{\theta}_1 = \frac{
    -6(m_1+2m_2)g\sin\theta_1 
    -2m_2l_1\dot{\theta}_1^2\sin(2\theta_1-2\theta_2)
    +12m_2g\sin\theta_2\cos(\theta_1-\theta_2)
    -2m_2l_2\dot{\theta}_2^2\sin(\theta_1-\theta_2)
    }
    {
    l_1(m_1+4m_2) 
    -4m_2l_1\cos^2(\theta_1-\theta_2)
    }
    \]

    \[
    \ddot{\theta}_2=
    -2\frac{l_1}{l_2}\ddot{\theta}_1\cos(\theta_1-\theta_2)
    +2\frac{l_1}{l_2}\dot{\theta}_1^2\sin(\theta_1-\theta_2)
    -6\frac{g}{l_2}\sin\theta_2
    \]
    '''

    ddtheta1 = (
        -(6*(m1+2*m2)*g*np.sin(theta1))
        - (2*m2*l1*(omega1**2)*np.sin(2*theta1 - 2*theta2))
        + (12*m2*g*np.sin(theta2)*np.cos(theta1 - theta2))
        - (2*m2*l2*(omega2**2)*np.sin(theta1 - theta2))
    ) / ((l1*(m1+4*m2)) - (4*m2*l1*(np.cos(theta1 - theta2)**2)))

    ddtheta2 = (
        -(2*(l1/l2)*ddtheta1*np.cos(theta1 - theta2)) 
        +(2*(l1/l2)*omega1**2*np.sin(theta1 - theta2)) 
        - (6*(g/l2)*np.sin(theta2))
        )

    return [omega1, omega2, ddtheta1, ddtheta2]

# ----------------------------------------------------------
# 3. Set up initial conditions and time span
# ----------------------------------------------------------
theta1_0 = 1.5708   # initial angle of link 1 (90 degrees)
theta2_0 = 0.0         # initial angle of link 2 (0 degrees)
omega1_0 = 0.0         # initial angular velocity of link 1
omega2_0 = 0.0         # initial angular velocity of link 2

# Initial state vector: [theta1, theta2, omega1, omega2]
y0 = [theta1_0, theta2_0, omega1_0, omega2_0]

# Time span for the simulation
t_start = 0.0
t_end   = 40.0   # 40 seconds simulation
num_points = 4000
t_eval = np.linspace(t_start, t_end, num_points)

# ----------------------------------------------------------
# 4. Solve the ODE using RK45 via solve_ivp
# ----------------------------------------------------------
sol = solve_ivp(
    fun=equations_of_motion, 
    t_span=[t_start, t_end], 
    y0=y0, 
    t_eval=t_eval, 
    method='Radau',  # Using the implicit Radau method for stiff ODEs
    rtol=1e-9,       # tighter tolerances may help with stiff problems
    atol=1e-10
)

# Extract the solutions
theta1_sol = sol.y[0]
theta2_sol = sol.y[1]
omega1_sol = sol.y[2]
omega2_sol = sol.y[3]
time       = sol.t

# ----------------------------------------------------------
# 5. Set up a visualization/animation
# ----------------------------------------------------------
def get_cartesian_coords(theta1, theta2, l1, l2):
    """
    Converts angular coordinates to Cartesian coordinates.
    (x1, y1) is the end of the first link,
    (x2, y2) is the end of the second link.
    """
    # Using the full lengths instead of half-lengths:
    x1 = l1 * np.sin(theta1)
    y1 = -l1 * np.cos(theta1)
    x2 = (l1 * np.sin(theta1)) + (l2 * np.sin(theta2))
    y2 = (-l1 * np.cos(theta1)) - (l2 * np.cos(theta2))
    return x1, y1, x2, y2

# Create a figure and axis for the animation
fig, ax = plt.subplots()
ax.set_xlim(-(l1+l2), (l1+l2))
ax.set_ylim(-(l1+l2), (l1+l2))
ax.set_aspect('equal', 'box')
line, = ax.plot([], [], 'o-', lw=2)

def init():
    """Initialize the animation frame."""
    line.set_data([], [])
    return (line,)

def update(frame):
    """Update the animation for frame index 'frame'."""
    x1, y1, x2, y2 = get_cartesian_coords(theta1_sol[frame], theta2_sol[frame], l1, l2)
    line.set_data([0, x1, x2], [0, y1, y2])
    return (line,)

ani = FuncAnimation(
    fig, update, frames=range(num_points),
    init_func=init, blit=True, interval=20
)

plt.title(title)
writer = PillowWriter(fps=15, metadata=dict(artist='Me'), bitrate=1800)
ani.save(f'{sim_outpath}{title}.gif', writer=writer)
plt.close()

arm1_positions = []  # Each tuple: (time, x1, y1)
arm2_positions = []  # Each tuple: (time, x2, y2)

for i, t in enumerate(time):
    x1, y1, x2, y2 = get_cartesian_coords(theta1_sol[i], theta2_sol[i], l1, l2)
    arm1_positions.append((t, math.atan2(y1,x1), (x1, y1)))
    arm2_positions.append((t, math.atan2(y2,x2), (x2, y2)))

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
    plt.plot(times, angles, linestyle='-', color='b', label='Arm 1')
    plt.plot(times2, angles2, linestyle='-', color='r', label='Arm 2')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Angle (degrees)")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

plot_graph(arm1_positions, f"Theta 1 {title}")
plot_graph(arm2_positions, f"Theta 2 {title}")
plot_graph_comparison(arm1_positions, arm2_positions, title)
pos_time_graph(arm1_positions, arm2_positions, (0,0), "Arm 1", "Arm 2", "Pivot Point")