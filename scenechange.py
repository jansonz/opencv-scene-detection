import cv2
import argparse
from datetime import timedelta
import time
import signal  # Import the signal module

# Set up argument parsing
parser = argparse.ArgumentParser(
    description="Detects scene changes in a video or live stream and optionally writes timestamps to a text file.")
parser.add_argument(
    "--input", help="Path to the input video file or URL of the live stream.", required=True)
parser.add_argument(
    "--textout", help="Enable text output to a file and specify the file path.",
    nargs='?', const="scene_changes.txt", type=str)
parser.add_argument(
    "--silent", help="Run the process in the background without opening the video window.\
    Performance significantly reduced if not running silently", action="store_true")
parser.add_argument(
    "--verbose", help="Enable verbose output to provide progress and frame rate information.", action="store_true")

args = parser.parse_args()

VIDEO_SOURCE = args.input
TEXTOUT_FILE = args.textout if args.textout is not None else None
SILENT_MODE = args.silent
VERBOSE_MODE = args.verbose

# Initialize global variables for cleanup in signal handler
cap = None
file_out = None

overlay_timeout = 25
frame_counter = 0
overlay_active = False


# Signal handler function for graceful shutdown
def signal_handler(signum, frame):
    print("\nReceived termination signal. Exiting gracefully...")
    global cap, file_out
    if cap:
        cap.release()
    if file_out:
        file_out.close()
    cv2.destroyAllWindows()
    exit(0)


# Register signal handler for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Load the video or live stream
cap = cv2.VideoCapture(VIDEO_SOURCE)

if not cap.isOpened():
    print(f"Error opening video source: {VIDEO_SOURCE}")
    exit(1)

try:
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
except ValueError:
    total_frames = -1  # Indicates live stream

current_frame = 0

# Check if text output is enabled and prepare the file
if TEXTOUT_FILE:
    file_out = open(TEXTOUT_FILE, "w")
else:
    file_out = None

try:
    # Initialize the color histogram of the first frame
    incoming_data, frame = cap.read()
    if not incoming_data:
        print("Error reading the first frame from the video.")
        exit(1)

    previous_histogram = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    previous_histogram = cv2.normalize(previous_histogram, previous_histogram).flatten()

    last_scene_change = 0
    start_time = time.time()  # Record start time for FPS calculation

    while True:
        incoming_data, frame = cap.read()
        if not incoming_data:
            time.sleep(1)  # Wait for a second and try to read again
            continue

        current_frame += 1
        histogram = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        histogram = cv2.normalize(histogram, histogram).flatten()

        d = cv2.compareHist(previous_histogram, histogram, cv2.HISTCMP_CORREL)
        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

        if d < 0.98 and (current_time - last_scene_change >= 1 or last_scene_change == 0):
            time_stamp = timedelta(seconds=current_time)
            formatted_time = str(time_stamp)
            if file_out:
                file_out.write(f"Scene change at: {formatted_time}\n")
            if not SILENT_MODE:
                if frame_counter < overlay_timeout:
                    cv2.putText(frame, "Scene Change Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    overlay_active = True
            last_scene_change = current_time

        if not SILENT_MODE:
            if frame_counter < overlay_timeout and overlay_active:
                cv2.putText(frame, "Scene Change Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                frame_counter += 1
            else:
                overlay_active = False
                frame_counter = 0

        if VERBOSE_MODE and total_frames > 0:
            progress = int(50 * current_frame / total_frames)
            bar = "[" + "=" * progress + " " * (50 - progress) + "]"
            print(
                f"\r{bar} {current_frame}/{total_frames} frames processed, FPS:\
                {current_frame / (time.time() - start_time):.2f}", end="")
        elif VERBOSE_MODE:
            print(f"\r{current_frame} frames processed, FPS: {current_frame / (time.time() - start_time):.2f}", end="")

        previous_histogram = histogram

        if not SILENT_MODE:
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
finally:
    signal_handler(None, None)  # Ensure resources are released properly
