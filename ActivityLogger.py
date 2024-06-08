# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 15:03:18 2024

@author: alext
"""

import argparse
import threading
import time
import csv
import tkinter as tk
from pynput import mouse, keyboard
import pyaudio
import numpy as np
import scipy.fftpack

# Constants for audio recording
CHUNK = 1024  # Number of samples per frame
FORMAT = pyaudio.paInt16  # Audio format (bytes per sample)
CHANNELS = 1  # Single channel for microphone
RATE = 44100  # Sample rate (samples per second)

# Variables to store statistics
mouse_distance = 0
mouse_clicks = 0
keyboard_hits = 0
mouse_x = 0
mouse_y = 0
audio_peak_freq = 0
audio_wavelength = 0
audio_amplitude = 0

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

# Function to analyze audio data
def analyze_audio_data(data):
    global audio_amplitude
    audio_data = np.frombuffer(data, dtype=np.int16)
    fft_data = np.abs(scipy.fftpack.fft(audio_data))
    freqs = np.fft.fftfreq(len(fft_data)) * RATE
    peak_freq = abs(freqs[np.argmax(fft_data)])
    wavelength = RATE / peak_freq if peak_freq > 0 else 0
    audio_amplitude = np.max(np.abs(audio_data))
    return peak_freq, wavelength

# Function to record and analyze audio
def record_audio():
    global running, audio_peak_freq, audio_wavelength, audio_amplitude

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    start_time = time.time()
    while running and (time.time() - start_time) < args.duration:
        data = stream.read(CHUNK)
        peak_freq, wavelength = analyze_audio_data(data)
        with lock:
            audio_peak_freq = peak_freq
            audio_wavelength = wavelength
        time.sleep(args.interval)

    stream.stop_stream()
    stream.close()
    p.terminate()

# Function to print and save statistics at regular intervals
def print_and_save_stats(interval, duration, csv_file):
    global mouse_distance, mouse_clicks, keyboard_hits, running, mouse_x, mouse_y, audio_peak_freq, audio_wavelength, audio_amplitude
    start_time = time.time()

    csv_headers = ['timestamp', 'mouse_x', 'mouse_y', 'mouse_distance', 'mouse_clicks', 'keyboard_hits', 'audio_peak_freq', 'audio_wavelength', 'audio_amplitude']
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers)
    
    while running and (time.time() - start_time) < duration:
        time.sleep(interval)
        with lock:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            stats = [timestamp, mouse_x, mouse_y, mouse_distance, mouse_clicks, keyboard_hits, audio_peak_freq, audio_wavelength, audio_amplitude]
            print(f"time: {timestamp}, mouse_x: {mouse_x}, mouse_y: {mouse_y}, mouse_distance: {mouse_distance:.2f}, mouse_clicks: {mouse_clicks}, keyboard_hits: {keyboard_hits}, audio_peak_freq: {audio_peak_freq:.2f}, audio_wavelength: {audio_wavelength:.2f}, audio_amplitude: {audio_amplitude:.2f}")
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(stats)
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
    global running, root, time_label, args

    parser = argparse.ArgumentParser(description="Mouse, Keyboard, and Audio Activity Logger")
    parser.add_argument('--duration', type=int, default=3*60*60, help='The duration of the logging in seconds (default: 3 hours)')
    parser.add_argument('--interval', type=float, default=0.5, help='The time interval for logging in seconds (default: 0.5 seconds)')
    parser.add_argument('--name', type=str, default='stats', help='The prefix for the output CSV file name (default: "stats")')
    args = parser.parse_args()

    csv_file = f"{args.name}_stats.csv"
    print(f"CSV file to be created: {csv_file}")

    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press)

    mouse_listener.start()
    keyboard_listener.start()

    stats_thread = threading.Thread(target=print_and_save_stats, args=(args.interval, args.duration, csv_file))
    audio_thread = threading.Thread(target=record_audio)
    stats_thread.start()
    audio_thread.start()

    root = tk.Tk()
    root.title("Stop Logger")

    log_info_label = tk.Label(root, text=f"Logging Duration: {time.strftime('%H:%M:%S', time.gmtime(args.duration))}\nTime Interval: {args.interval} seconds")
    log_info_label.pack(padx=20, pady=10)

    time_label = tk.Label(root, text="Elapsed Time: 00:00:00\nRemaining Time: 00:00:00")
    time_label.pack(padx=20, pady=10)

    stop_button = tk.Button(root, text="Stop", command=stop_program)
    stop_button.pack(padx=20, pady=20)

    start_time = time.time()
    update_time_label(start_time, args.duration, args.interval)

    root.mainloop()

    mouse_listener.stop()
    keyboard_listener.stop()
    stats_thread.join()
    audio_thread.join()

if __name__ == "__main__":
    main()