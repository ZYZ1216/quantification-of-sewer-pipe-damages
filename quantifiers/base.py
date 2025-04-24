from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple, Dict, Any

class DamageQuantifier(ABC):
    def run(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """Template Method defining the workflow.
        
        Args:
            image: The input image as a numpy array
            bbox: Bounding box coordinates as (x, y, width, height)
            
        Returns:
            Dictionary containing quantification results
        """
        roi = self.preprocess(image, bbox)
        return self.quantify(roi)

    @abstractmethod
    def preprocess(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Extract & normalize the ROI for this damage type.
        
        Args:
            image: The input image as a numpy array
            bbox: Bounding box coordinates as (x, y, width, height)
            
        Returns:
            Preprocessed region of interest
        """
        pass

    @abstractmethod
    def quantify(self, roi: np.ndarray) -> Dict[str, Any]:
        """Compute the metric (e.g. width, area %) from the ROI.
        
        Args:
            roi: Preprocessed region of interest
            
        Returns:
            Dictionary containing quantification results with metrics
        """
        pass
