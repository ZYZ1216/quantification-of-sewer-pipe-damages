import numpy as np
import cv2
from typing import Tuple, Optional

def crop_roi(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
    """Crop region of interest from image.
    
    Args:
        image: The input image as a numpy array
        bbox: Bounding box coordinates as (x, y, width, height)
        
    Returns:
        Cropped image region
    """
    x, y, w, h = bbox
    return image[y:y+h, x:x+w]

def resize_roi(roi: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """Resize region of interest.
    
    Args:
        roi: Region of interest as numpy array
        target_size: Target size as (width, height)
        
    Returns:
        Resized region of interest
    """
    return cv2.resize(roi, target_size, interpolation=cv2.INTER_AREA)

def enhance_contrast(roi: np.ndarray) -> np.ndarray:
    """Enhance contrast of ROI for better feature extraction.
    
    Args:
        roi: Region of interest
        
    Returns:
        Contrast-enhanced image
    """
    # Convert to grayscale if RGB
    if len(roi.shape) == 3:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    else:
        gray = roi.copy()
        
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)
