#!/bin/bash

# Define color codes for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Creating sewer damage quantification project structure...${NC}"

# Create main project directory
mkdir -p sewer_damage
cd sewer_damage

# Create subdirectories
mkdir -p quantifiers preprocessing tests docs

# Create base files
cat > quantifiers/__init__.py << 'EOF'
# Makes quantifiers available from the package
from .base import DamageQuantifier
EOF

cat > quantifiers/base.py << 'EOF'
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
EOF

cat > factory.py << 'EOF'
from typing import Type, Dict, Callable, TypeVar
from quantifiers.base import DamageQuantifier

T = TypeVar('T', bound=DamageQuantifier)

class QuantifierFactory:
    _registry: Dict[str, Type[DamageQuantifier]] = {}

    @classmethod
    def register(cls, label: str) -> Callable[[Type[T]], Type[T]]:
        def decorator(qclass: Type[T]) -> Type[T]:
            cls._registry[label] = qclass
            return qclass
        return decorator

    @classmethod
    def create(cls, label: str) -> DamageQuantifier:
        if label not in cls._registry:
            raise ValueError(f"No quantifier for {label}")
        return cls._registry[label]()
EOF

cat > pipeline.py << 'EOF'
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
EOF

cat > preprocessing/__init__.py << 'EOF'
# Import preprocessing modules
EOF

cat > preprocessing/transforms.py << 'EOF'
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
EOF

# Create template for each damage type
damage_types=(
    "Crack:width_mm:Width in mm"
    "Root:blockage_percent:Area % blockage"
    "Deposition:coverage_percent:% area covered"
    "Obstacle:relative_size:Size vs pipe"
    "Connection:protrusion_mm:Protrusion length"
    "Misalignment:deviation_mm:Pipe center deviation"
    "Deformation:distortion_percent:Shape distortion"
    "JointDamage:is_broken:Broken segment detection"
    "MaterialLoss:wall_loss_percent:Wall loss detection"
    "Break:missing_part_percent:Missing part size"
)

for damage_info in "${damage_types[@]}"; do
    IFS=':' read -r damage metric description <<< "$damage_info"
    
    # Convert CamelCase to snake_case for filename
    damage_file=$(echo "$damage" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1_\2/g' | tr '[:upper:]' '[:lower:]')
    
    cat > "quantifiers/${damage_file}.py" << EOF
import numpy as np
import cv2
from typing import Tuple, Dict, Any
from quantifiers.base import DamageQuantifier
from factory import QuantifierFactory
from preprocessing.transforms import crop_roi, resize_roi, enhance_contrast

@QuantifierFactory.register("$damage")
class ${damage}Quantifier(DamageQuantifier):
    """Quantifier for $damage damage type.
    
    Quantifies: $description
    """
    
    def preprocess(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Extract & preprocess the region of interest for $damage.
        
        Args:
            image: The input image as a numpy array
            bbox: Bounding box coordinates as (x, y, width, height)
            
        Returns:
            Preprocessed region of interest
        """
        # Basic preprocessing steps
        roi = crop_roi(image, bbox)
        
        # $damage-specific preprocessing
        # TODO: Implement specific preprocessing for $damage
        
        return roi
    
    def quantify(self, roi: np.ndarray) -> Dict[str, Any]:
        """Quantify the $damage damage.
        
        Args:
            roi: Preprocessed region of interest
            
        Returns:
            Dictionary with quantification metrics
        """
        # TODO: Implement $damage-specific quantification algorithm
        
        # This is a placeholder implementation
        result = {
            "$metric": 0.0,  # Replace with actual calculation
            "confidence": 0.85  # Confidence score of the measurement
        }
        
        return result
EOF
    
    # Create test file for this damage type
    cat > "tests/test_${damage_file}.py" << EOF
import unittest
import numpy as np
from quantifiers.${damage_file} import ${damage}Quantifier

class Test${damage}Quantifier(unittest.TestCase):
    def setUp(self):
        self.quantifier = ${damage}Quantifier()
        # Create a test image (100x100 with a simple pattern)
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.test_bbox = (10, 10, 50, 50)  # x, y, width, height
    
    def test_preprocess(self):
        """Test that preprocessing returns expected output shape."""
        roi = self.quantifier.preprocess(self.test_image, self.test_bbox)
        self.assertEqual(roi.shape[:2], (50, 50))
    
    def test_quantify(self):
        """Test that quantification returns expected metric."""
        # Create a dummy ROI
        roi = np.zeros((50, 50, 3), dtype=np.uint8)
        result = self.quantifier.quantify(roi)
        
        # Check that result has the expected key
        self.assertIn("$metric", result)
        self.assertIn("confidence", result)
        
        # Add more specific tests here

if __name__ == '__main__':
    unittest.main()
EOF
done

# Create setup files
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="sewer_damage",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "opencv-python>=4.5.0",
        "scikit-image>=0.18.0",
    ],
    description="Framework for quantifying sewer pipe damage",
    author="Your Team",
    python_requires=">=3.7",
)
EOF

cat > requirements.txt << 'EOF'
numpy>=1.20.0
opencv-python>=4.5.0
scikit-image>=0.18.0
matplotlib>=3.4.0
pytest>=6.2.0
EOF

# Create example script
cat > example.py << 'EOF'
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
EOF

# Create a README.md file
cat > README.md << 'EOF'
# Sewer Damage Quantification

A modular framework for quantifying various types of damage in sewer pipes from images.

## Damage Types and Metrics

1. **Crack** → Width in mm
2. **Root** → Area % blockage
3. **Deposition** → % area covered
4. **Obstacle** → Size vs pipe
5. **Connection** → Protrusion length
6. **Misalignment** → Pipe center deviation
7. **Deformation** → Shape distortion
8. **JointDamage** → Broken segment detection
9. **MaterialLoss** → Wall loss detection
10. **Break** → Missing part size

## Project Structure

