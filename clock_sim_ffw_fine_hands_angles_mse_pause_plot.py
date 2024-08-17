import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from datetime import datetime, timedelta, time as time_measure

# Global variable to keep track of the pause state
pause_start_time = None
pause_interval = 15  # Default pause interval
jump_interval = 13000 # frames
jump_after_find = 0 

# Function to calculate the mean square error based on the relative difference between angles
def calculate_mse(hour_angle, min_angle, sec_angle):
    diff_hour_min = min(abs(hour_angle - min_angle), 2 * np.pi - abs(hour_angle - min_angle))
    diff_hour_sec = min(abs(hour_angle - sec_angle), 2 * np.pi - abs(hour_angle - sec_angle))
    diff_min_sec = min(abs(min_angle - sec_angle), 2 * np.pi - abs(min_angle - sec_angle))
    # mse = np.mean([diff_hour_min**2, diff_hour_sec**2, diff_min_sec**2])
    mse = np.max([diff_hour_min**2, diff_hour_sec**2, diff_min_sec**2])
    return mse

# Function to close the plot when the animation is complete
def close_plot(event):
    plt.close(event.canvas.figure)

# Function to update the hands and MSE
def update_usec(frame, start_time, fast_forward, mseAccuracy):
    global pause_start_time, jump_after_find, jump_interval

    # Clear the current plot
    plt.clf()

    # Calculate the current time with fast forward factor
    elapsed_time = timedelta(seconds=frame * fast_forward * 0.1) if pause_start_time is None else timedelta(seconds=(frame+jump_after_find) * fast_forward * 0.1)
    now = start_time + elapsed_time
    second = now.second + now.microsecond / 1e6
    minute = now.minute
    hour = now.hour % 12

    # Calculate angles for the hands
    sec_angle = np.deg2rad(360 * second / 60.0)
    min_angle = np.deg2rad(360 * (minute + second / 60.0) / 60.0)
    hour_angle = np.deg2rad(360 * (hour + (minute + second / 60.0) / 60.0) / 12.0)

    # Calculate the Mean Square Error based on the relative differences between angles
    mse = calculate_mse(hour_angle, min_angle, sec_angle)

    # Check if MSE is less than 0.5
    if mse < mseAccuracy:
        pause_start_time = now
        round_seconds = timedelta(microseconds=500000)
        pause_start_time += round_seconds
        print(f"Clock Hands Overlap at: {pause_start_time.strftime('%H:%M:%S')}")        
        plt.text(1.6, -0.2, f'Clock Hands Overlap at: {pause_start_time.strftime("%H:%M:%S")}', fontsize=12, color='red', va='center')
        jump_after_find += jump_interval

    # Create the clock hands
    plt.plot([0, 0.9 * np.sin(hour_angle)], [0, 0.9 * np.cos(hour_angle)], lw=6, color='black')
    plt.plot([0, 1.1 * np.sin(min_angle)], [0, 1.1 * np.cos(min_angle)], lw=4, color='blue')
    plt.plot([0, 1.2 * np.sin(sec_angle)], [0, 1.2 * np.cos(sec_angle)], lw=2, color='red')

    # Draw the clock face
    clock_face = plt.Circle((0, 0), 1.3, color='black', fill=False, lw=2)
    plt.gca().add_patch(clock_face)

    # Draw hour markers
    for angle in range(0, 360, 30):
        x_inner = 1.15 * np.sin(np.deg2rad(angle))
        y_inner = 1.15 * np.cos(np.deg2rad(angle))
        x_outer = 1.25 * np.sin(np.deg2rad(angle))
        y_outer = 1.25 * np.cos(np.deg2rad(angle))
        plt.plot([x_inner, x_outer], [y_inner, y_outer], lw=3, color='black')

    # Draw minute markers
    for angle in range(0, 360, 6):
        if angle % 30 != 0:  # Skip the hour markers
            x_inner = 1.2 * np.sin(np.deg2rad(angle))
            y_inner = 1.2 * np.cos(np.deg2rad(angle))
            x_outer = 1.25 * np.sin(np.deg2rad(angle))
            y_outer = 1.25 * np.cos(np.deg2rad(angle))
            plt.plot([x_inner, x_outer], [y_inner, y_outer], lw=1, color='black')

    # Display the MSE and paused time
    plt.text(1.6, 0, f'MSE: {mse:.4f}', fontsize=12, color='black', va='center')
    if pause_start_time is not None:
        plt.text(0, -1.6, f'Clock Hands Overlap at: {pause_start_time.strftime("%H:%M:%S")}', fontsize=12, color='red', ha='center')

    # Set limits and aspect ratio
    plt.xlim(-1.5, 2.5)  # Extend xlim to make space for the text
    plt.ylim(-1.5, 1.5)
    plt.gca().set_aspect('equal', adjustable='box')

    # Hide axes
    plt.axis('off')

def run_clock():
    fast_forward = 3.0  # Change this to any factor you want to fast forward time
    mseAccuracy = 0.00250

    # Initialize a specific time (e.g., 14:30:00)
    specific_time = time_measure(hour=0, minute=0, second=0)
    now_with_specific_time = datetime.combine(datetime.today(), specific_time)
    start_time = now_with_specific_time

    fig = plt.figure(figsize=(8, 6))
    ani = animation.FuncAnimation(fig, update_usec, frames=10000000, interval=10, repeat=True, fargs=(start_time, fast_forward, mseAccuracy))

    # Connect the close_plot function to the end of the animation
    ani._stop = lambda: close_plot(fig)

    plt.show()

run_clock()
