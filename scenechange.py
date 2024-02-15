import cv2
import argparse
from datetime import timedelta
import time

# Set up argument parsing
parser = argparse.ArgumentParser(description="Detects scene changes in a video and optionally write timestamps to a text file.")
parser.add_argument("--input", help="Path to the input video file.", required=True)
parser.add_argument("--textout", help="Enable text output to a file and specify the file path.", nargs='?', const="scene_changes.txt", type=str)
parser.add_argument("--silent", help="Run the process in the background without opening the video window. Performance significantly reduced if not running silently", action="store_true")
parser.add_argument("--verbose", help="Enable verbose output to provide progress and frame rate information.", action="store_true")

args = parser.parse_args()

VIDEO_SOURCE = args.input
TEXTOUT_FILE = args.textout if args.textout is not None else None
SILENT_MODE = args.silent
VERBOSE_MODE = args.verbose

# Load the video
cap = cv2.VideoCapture(VIDEO_SOURCE)

if not cap.isOpened():
    print(f"Error opening video file: {VIDEO_SOURCE}")
    exit(1)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
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

    while cap.isOpened():
        incoming_data, frame = cap.read()
        if not incoming_data:
            break

        current_frame += 1
        histogram = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        histogram = cv2.normalize(histogram, histogram).flatten()

        d = cv2.compareHist(previous_histogram, histogram, cv2.HISTCMP_CORREL)
        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

        if d < 0.98 and current_time - last_scene_change >= 1:
            time_stamp = timedelta(seconds=current_time)
            formatted_time = str(time_stamp)
            if file_out:
                file_out.write(f"Scene change at: {formatted_time}\n")
            if not SILENT_MODE:
                cv2.putText(frame, "Scene Change Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            last_scene_change = current_time

        if VERBOSE_MODE:
            progress = int(50 * current_frame / total_frames)
            bar = "[" + "=" * progress + " " * (50 - progress) + "]"
            print(f"\r{bar} {current_frame}/{total_frames} frames processed, FPS: {current_frame / (time.time() - start_time):.2f}", end="")

        previous_histogram = histogram

        if not SILENT_MODE:
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
finally:
    # Final newline to move past the overwritten line
    if VERBOSE_MODE:
        print()  # Ensure the terminal line is properly finished
    cap.release()
    cv2.destroyAllWindows()
    if file_out:
        file_out.close()
