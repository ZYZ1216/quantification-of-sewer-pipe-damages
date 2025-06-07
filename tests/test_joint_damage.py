# import unittest
# import numpy as np
# from quantifiers.joint_damage import JointDamageQuantifier
#
# class TestJointDamageQuantifier(unittest.TestCase):
#     def setUp(self):
#         self.quantifier = JointDamageQuantifier()
#         # Create a test image (100x100 with a simple pattern)
#         self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
#         self.test_bbox = (10, 10, 50, 50)  # x, y, width, height
#
#     def test_preprocess(self):
#         """Test that preprocessing returns expected output shape."""
#         roi = self.quantifier.preprocess(self.test_image, self.test_bbox)
#         self.assertEqual(roi.shape[:2], (50, 50))
#
#     def test_quantify(self):
#         """Test that quantification returns expected metric."""
#         # Create a dummy ROI
#         roi = np.zeros((50, 50, 3), dtype=np.uint8)
#         result = self.quantifier.quantify(roi)
#
#         # Check that result has the expected key
#         self.assertIn("is_broken", result)
#         self.assertIn("confidence", result)
#
#         # Add more specific tests here
#
# if __name__ == '__main__':
#     unittest.main()


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
        self.assertEqual(roi.shape[:2], (256, 256))
        self.assertTrue(hasattr(self.quantifier, 'original_roi_size'))
        self.assertEqual(self.quantifier.original_roi_size, (50, 50))

    def test_quantify(self):
        """Test that quantification returns expected metric."""
        _ = self.quantifier.preprocess(self.test_image, self.test_bbox)
        roi = np.zeros((256, 256, 3), dtype=np.uint8)
        result = self.quantifier.quantify(roi)

        self.assertIn("offset_mean_width_mm", result)
        self.assertIn("confidence", result)
        self.assertIsInstance(result["offset_mean_width_mm"], float)
        self.assertIsInstance(result["confidence"], float)



if __name__ == '__main__':
    unittest.main()

# import unittest
# from quantifiers.joint_damage import JointDamageQuantifier
# import cv2
# import os
#
# class TestJointDamageQuantifier(unittest.TestCase):
#     def setUp(self):
#         self.quantifier = JointDamageQuantifier()
#
#         self.img_path = "/Users/zyz/Documents/quantification-of-sewer-pipe-damages/0003110600042104_20230711_FL01_esic_esic_x066096_y0816_w1633_h1633.png"
#         self.bbox = (137, 0, 226, 1633)
#
#     def test_preprocess_real_image(self):
#         """Test preprocess step on real image and bbox."""
#         if not os.path.exists(self.img_path):
#             self.skipTest("Test image not found")
#         image = cv2.imread(self.img_path)
#         roi = self.quantifier.preprocess(image, self.bbox)
#         self.assertEqual(roi.shape[:2], (256, 256))
#         print("Preprocessing shape:", roi.shape)
#
#     def test_quantify_real_image(self):
#         """Test full pipeline: preprocess + quantify on real image."""
#         if not os.path.exists(self.img_path):
#             self.skipTest("Test image not found")
#         image = cv2.imread(self.img_path)
#         roi = self.quantifier.preprocess(image, self.bbox)
#         result = self.quantifier.quantify(roi)
#         self.assertIn("offset_mean_width_mm", result)
#         self.assertIn("confidence", result)
#         print("Quantify result:", result)
#
# if __name__ == '__main__':
#     unittest.main()
