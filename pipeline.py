import numpy as np
from typing import Tuple, Dict, Any
from factory import QuantifierFactory

def quantify_damage(label: str, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict[str, Any]:
    """Quantify the specified damage type in the given image and bounding box.
    
    Args:
        label: The damage type label
        image: The input image as a numpy array
        bbox: Bounding box coordinates as (x, y, width, height)
        
    Returns:
        Dictionary containing quantification results
    """
    quantifier = QuantifierFactory.create(label)
    return quantifier.run(image, bbox)
