# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 15:03:18 2024

@author: alext
"""

import argparse
from pynput import mouse, keyboard
import threading
import time
import csv
import tkinter as tk

# Variables to store statistics
mouse_distance = 0
mouse_clicks = 0
keyboard_hits = 0
mouse_x = 0
mouse_y = 0

# Last mouse position
last_mouse_position = None

# Lock for synchronizing access to variables
lock = threading.Lock()

# Flag to control the running state
running = True

# Mouse move event handler
def on_move(x, y):
    global last_mouse_position, mouse_distance, mouse_x, mouse_y
    with lock:
        if last_mouse_position is not None:
            dx = x - last_mouse_position[0]
            dy = y - last_mouse_position[1]
            mouse_distance += (dx**2 + dy**2)**0.5
        last_mouse_position = (x, y)
        mouse_x = x
        mouse_y = y

# Mouse click event handler
def on_click(x, y, button, pressed):
    global mouse_clicks
    if pressed:
        with lock:
            mouse_clicks += 1

# Keyboard press event handler
def on_press(key):
    global keyboard_hits
    with lock:
        keyboard_hits += 1

# Function to print and save statistics at regular intervals
def print_and_save_stats(interval, duration, csv_file):
    global mouse_distance, mouse_clicks, keyboard_hits, running, mouse_x, mouse_y
    start_time = time.time()
    
    # Initialize the CSV file
    csv_headers = ['timestamp', 'mouse_x', 'mouse_y', 'mouse_distance', 'mouse_clicks', 'keyboard_hits']
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers)
    
    while running and (time.time() - start_time) < duration:
        time.sleep(interval)
        with lock:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            stats = [timestamp, mouse_x, mouse_y, mouse_distance, mouse_clicks, keyboard_hits]
            print(f"time: {timestamp}, mouse_x: {mouse_x}, mouse_y: {mouse_y}, mouse_distance: {mouse_distance:.2f}, mouse_clicks: {mouse_clicks}, keyboard_hits: {keyboard_hits}")
            # Save to CSV file
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(stats)
            # Reset statistics
            mouse_distance = 0
            mouse_clicks = 0
            keyboard_hits = 0
    running = False

# Function to stop the program
def stop_program():
    global running
    running = False
    root.quit()

def update_time_label(start_time, duration, interval):
    elapsed_time = time.time() - start_time
    remaining_time = max(0, duration - elapsed_time)
    elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
    remaining_str = time.strftime('%H:%M:%S', time.gmtime(remaining_time))
    time_label.config(text=f"Elapsed Time: {elapsed_str}\nRemaining Time: {remaining_str}")
    if running:
        root.after(int(interval * 1000), update_time_label, start_time, duration, interval)

def main():
    global running, root, time_label

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Mouse and Keyboard Activity Logger")
    parser.add_argument('--duration', type=int, default=3*60*60, help='The duration of the logging in seconds (default: 3 hours)')
    parser.add_argument('--interval', type=float, default=0.5, help='The time interval for logging in seconds (default: 0.5 seconds)')
    parser.add_argument('--name', type=str, default='stats', help='The prefix for the output CSV file name (default: "stats")')
    args = parser.parse_args()

    # Generate the CSV file name
    csv_file = f"{args.name}_stats.csv"
    print(f"CSV file to be created: {csv_file}")

    # Start listeners
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press)

    mouse_listener.start()
    keyboard_listener.start()

    # Start the print and save thread
    stats_thread = threading.Thread(target=print_and_save_stats, args=(args.interval, args.duration, csv_file))
    stats_thread.start()

    # Create a tkinter window for stopping the program
    root = tk.Tk()
    root.title("Stop Logger")

    # Display logging information
    log_info_label = tk.Label(root, text=f"Logging Duration: {time.strftime('%H:%M:%S', time.gmtime(args.duration))}\nTime Interval: {args.interval} seconds")
    log_info_label.pack(padx=20, pady=10)

    time_label = tk.Label(root, text="Elapsed Time: 00:00:00\nRemaining Time: 00:00:00")
    time_label.pack(padx=20, pady=10)

    # Stop button
    stop_button = tk.Button(root, text="Stop", command=stop_program)
    stop_button.pack(padx=20, pady=20)

    # Start updating the time label
    start_time = time.time()
    update_time_label(start_time, args.duration, args.interval)

    # Run the tkinter main loop
    root.mainloop()

    # Stop listeners and join the thread
    mouse_listener.stop()
    keyboard_listener.stop()
    stats_thread.join()

if __name__ == "__main__":
    main()
