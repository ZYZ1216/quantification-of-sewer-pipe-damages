#!/usr/bin/env python3
import cv2
import numpy as np
from pipeline import quantify_damage

def main():
    # Create a simple test image
    image = np.zeros((500, 500, 3), dtype=np.uint8)
    
    # Draw a crack-like feature
    cv2.line(image, (100, 200), (300, 250), (255, 255, 255), 5)
    
    # Define bounding box around the crack
    bbox = (90, 190, 220, 70)  # x, y, width, height
    
    # Draw the bounding box for visualization
    cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)
    
    # Quantify the damage
    result = quantify_damage("Crack", image, bbox)
    
    # Display results
    print(f"Quantification result: {result}")
    
    # Show the image
    cv2.imshow("Test Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
