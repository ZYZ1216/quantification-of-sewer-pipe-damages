import unittest
import numpy as np
from quantifiers.joint_damage import JointDamageQuantifier

class TestJointDamageQuantifier(unittest.TestCase):
    def setUp(self):
        self.quantifier = JointDamageQuantifier()
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
        self.assertIn("is_broken", result)
        self.assertIn("confidence", result)
        
        # Add more specific tests here

if __name__ == '__main__':
    unittest.main()
