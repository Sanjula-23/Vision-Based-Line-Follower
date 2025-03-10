# Line following Algorithm only using webcam

import cv2
import numpy as np
import math
import time


# get centroid of the contour
def get_centroid(contour):
    M = cv2.moments(contour)
    if M["m00"] != 0:  #contour eke valid nm centroid eka calculate karanne
        cx = int(M["m10"] / M["m00"])   # Calculate the x coordinate of the centroid
        cy = int(M["m01"] / M["m00"])   # Calculate the y coordinate of the centroid
        return cx, cy
    return None, None



# detect turn directions 
def detect_turn(centroid_x, width, contour_width):
    # parameters tune karanne
    left_threshold = width * 0.32
    right_threshold = width * 0.45
    min_turn_width = width * 0.35   # Minimum width to detect a turn

    if contour_width > min_turn_width:  # Check if it's a valid turn
        if centroid_x < left_threshold:
            return "LEFT"
        elif centroid_x > right_threshold:
            return "RIGHT"
        else:
            return "FORWARD"    # If the centroid is in the middle of the frame, the robot will move forward

    return "FORWARD"    # If the contour width is less than the minimum turn width, the robot will move forward



# draw grid on the frame for better visualization
def draw_grid(frame):
    h, w = frame.shape[:2]
    for i in range(0, w, 50):
        cv2.line(frame, (i, 0), (i, h), (50, 50, 50), 1)    # Hama 50 pixels vala ma grid eke adenewa 1 pixel width eka
    for i in range(0, h, 50):
        cv2.line(frame, (0, i), (w, i), (50, 50, 50), 1)    # Hama 50 pixels vala ma grid eke adenewa 1 pixel height eka



def main():
    cap = cv2.VideoCapture(0)  # Use external webcam
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    try:
        turning = False  # New state variable
        turn_start_time = None  # Track turn start time
        turn_duration = 2.0  # Set turning duration to 2 seconds

        while True:
            ret, frame = cap.read()  # Read frame
            if not ret:
                break

            # Resize for performance
            frame = cv2.resize(frame, (800, 600))  # Resize to 640x480 or 800x600 for faster processing
            height, width, _ = frame.shape  # Get frame dimensions

            # Define ROI (lower 2/3 of the frame)
            roi = frame[int(height * 0.67):, :] # processing speed eke increase karanne
            cv2.rectangle(frame, (0, int(height * 0.67)), (width, height), (0, 255, 0), 2)  # to show the 2/3 size eke (one nattam comment karanne)

            # Convert to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian Blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Apply Otsu's Thresholding to get binary image (Hybrid thresholding method)
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Apply Morphological Opening (Removes small white noise)
            kernel = np.ones((5,5), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            direction = "FORWARD"  # Default direction is forward

            if contours and not turning:  # Only detect turns if NOT already turning
                # Get largest contour (assume it's the line)
                largest_contour = max(contours, key=cv2.contourArea)
                cx, cy = get_centroid(largest_contour)
                
                if cx is not None and cy is not None:
                    contour_width = cv2.boundingRect(largest_contour)[2]
                    new_direction = detect_turn(cx, width, contour_width)

                    if new_direction in ["LEFT", "RIGHT"]:  
                        turning = True  # Lock the turn
                        turn_start_time = time.time()  # Start timing the turn
                        direction = new_direction  # Save the turn direction
                        # Display turn direction
                        while time.time() - turn_start_time < turn_duration:
                            ret, frame = cap.read()  # Read frame
                            if not ret:
                                break
                            # Draw grid
                            draw_grid(frame)
                            # Draw contours
                            cv2.drawContours(roi, [largest_contour], -1, (0, 255, 127), 2)
                            # Display turn direction
                            cv2.putText(frame, f"Turn {direction}", (250, 50), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 2)
                            cv2.imshow("Line Following Algo", frame)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break

            if contours and not turning:
                # Get largest contour (assume it's the line)
                largest_contour = max(contours, key=cv2.contourArea)
                cv2.drawContours(roi, [largest_contour], -1, (0, 255, 127), 2)

                # Calculate centroid
                cx, cy = get_centroid(largest_contour)
                if cx is not None and cy is not None:
                    # Draw centroid as a thick circle
                    cv2.circle(roi, (cx, cy), 15, (49, 49, 255), -2)

                    # Calculate contour width and detect turn
                    contour_width = cv2.boundingRect(largest_contour)[2]  # Get contour width
                    direction = detect_turn(cx, width, contour_width)  # Pass cx as centroid_x

                    # Overlay turn direction
                    if direction == "LEFT":
                        cv2.arrowedLine(roi, (cx, cy), (cx - 70, cy), (49, 49, 255), 5, tipLength=0.3)  # Draw an arrow pointing left
                    elif direction == "RIGHT":
                        cv2.arrowedLine(roi, (cx, cy), (cx + 70, cy), (49, 49, 255), 5, tipLength=0.3)  # Draw an arrow pointing right
                    else:
                        cv2.arrowedLine(roi, (cx, cy), (cx, cy - 70), (49, 49, 255), 5, tipLength=0.3)  # Draw an arrow pointing up

                    # Draw a circle that zooms in and out continuously at the centroid
                    radius = abs(int(15 + 20 * math.sin(time.time() * 2)))
                    color = (255, 0, 255) if int(time.time() * 2) % 2 == 0 else (230, 230, 230)
                    cv2.circle(roi, (cx, cy), radius, color, 2)

            # Reset turning state after a delay
            if turning and time.time() - turn_start_time > turn_duration:
                turning = False  # Unlock turn detection

            # Display direction text
            cv2.putText(frame, f"Direction: {direction}", (250, 50), cv2.FONT_HERSHEY_TRIPLEX, 1, (240, 240, 240), 2)

            # Draw grid
            draw_grid(frame)

            # Show frames
            cv2.imshow("Line Following Algo", frame)

            # Break loop with 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()



if __name__ == "__main__":
    main()
