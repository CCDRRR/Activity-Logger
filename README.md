# Mouse and Keyboard Activity Logger
This Python script logs mouse and keyboard activity over a specified duration. 
It records mouse movements, clicks, and keyboard presses at regular intervals and saves the data to a CSV file.

## Requirements
* Python 3x
* pynput
* tkinter

You can install the required packages using pip:  
```sh
pip install pynput tkinter
```
## Usage
Run the script with command line
```sh
python ActivityLogger.py [options]
```
## Options
* --duration: The duration of the logging in seconds. Default is 3 hours (10,800 seconds).
* --interval: The time interval for logging in seconds. Default is 0.5 seconds.
* --name: The prefix for the output CSV file name. Default is "stats".
## Examples
* Log for 2 hours (7,200 seconds) with a 1-second interval and save the file as Alex_stats.csv:
```sh
python ActivityLogger.py --duration 7200 --interval 1.0 --name Alex
```
## Stopping the Logger
A tkinter window will pop up with a "Stop" button. Click this button to stop the logger.
The script generates a CSV file with the following columns:
* timestamp: The date and time of the logged entry.
* mouse_x: The x-coordinate of the mouse.
* mouse_y: The y-coordinate of the mouse.
* mouse_distance: The distance the mouse moved since the last log entry.
* mouse_clicks: The number of mouse clicks since the last log entry.
* keyboard_hits: The number of keyboard presses since the last log entry.
  

## Notes
Ensure you have the necessary permissions to write to the directory where you run the script. 
If you encounter any permission issues, try running the script with elevated privileges or change the directory to a writable location.
