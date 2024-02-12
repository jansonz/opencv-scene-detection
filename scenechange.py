import cv2
from datetime import timedelta

VIDEO_SOURCE = "data/video.mp4"

# Load the video
cap = cv2.VideoCapture(VIDEO_SOURCE)

# Initialize the color histogram of the first frame
incoming_data, frame = cap.read()
previous_histogram = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
previous_histogram = cv2.normalize(previous_histogram, previous_histogram).flatten()

# Initialize a counter for the text display
text_counter = 0

# Initialize a variable for the time of the last logged scene change
last_scene_change = 0

while (cap.isOpened()):
    incoming_data, frame = cap.read()
    if not incoming_data:
        break

    # Calculate the color histogram of the current frame
    histogram = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    histogram = cv2.normalize(histogram, histogram).flatten()

    # Compare the color histogram of the current frame with that of the previous frame
    d = cv2.compareHist(previous_histogram, histogram, cv2.HISTCMP_CORREL)

    # Get the current time in the video
    current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

    # If the correlation is less than 0.98, it's likely that a scene change has occurred
    if d < 0.98 and current_time - last_scene_change >= 1:
        time = timedelta(seconds=cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
        text_counter = int(cap.get(cv2.CAP_PROP_FPS))
        last_scene_change = current_time

    # If the text counter is greater than 0, overlay the text on the frame
    if text_counter > 0:
        cv2.putText(frame, f"Scene change: {time}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        text_counter -= 1

    previous_histogram = histogram

    # Display the frame
    cv2.imshow('Frame', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
