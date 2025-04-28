import pkgutil
import importlib
import quantifiers

# Load all quantifier modules
for _, module_name, _ in pkgutil.iter_modules(quantifiers.__path__):
    importlib.import_module(f"quantifiers.{module_name}")

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
