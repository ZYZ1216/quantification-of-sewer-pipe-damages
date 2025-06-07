import numpy as np
import torch
import os
from pathlib import Path
import cv2
from typing import Tuple, Dict, Any
from quantifiers.base import DamageQuantifier
from factory import QuantifierFactory
from preprocessing.transforms import crop_roi, resize_roi
from torchvision import transforms
from PIL import Image
import segmentation_models_pytorch as smp


@QuantifierFactory.register("JointDamage")
class JointDamageQuantifier(DamageQuantifier):
    """Quantifier for JointDamage damage type. Quantifies: offset width"""

    def __init__(self):
        current_dir = Path(__file__).parent.parent
        model_path = current_dir / "Joint_damage_model.pth"

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = smp.Unet(encoder_name="resnet18", in_channels=3, classes=1, encoder_weights=None)
        self.model.load_state_dict(torch.load(str(model_path), map_location=self.device))
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])

    def preprocess(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        roi = crop_roi(image, bbox)
        self.original_roi_size = roi.shape[:2]  # 存储 ROI 的原始尺寸 (height, width)
        roi_resized = resize_roi(roi, (256, 256))
        return roi_resized

    def postprocess_mask(self, mask: np.ndarray) -> np.ndarray:
        mask = mask.astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # deal with tiny parts
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        cleaned = np.zeros_like(mask)
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= 200:  # 你可以调整面积阈值
                cleaned[labels == i] = 1
        return cleaned

    def quantify(self, roi: np.ndarray) -> Dict[str, Any]:
        pil_img = Image.fromarray(roi).convert("RGB")
        input_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)
            pred_mask = (output > 0.5).float().squeeze().cpu().numpy()

        # Resize original ROI  (width, height)
        mask_resized = cv2.resize(
            pred_mask,
            (self.original_roi_size[1], self.original_roi_size[0]),  # (width, height)
            interpolation=cv2.INTER_NEAREST
        )


        cleaned_mask = self.postprocess_mask(mask_resized)

        # calculate offset Region pixel coordinates
        offset_pixels = np.argwhere(cleaned_mask == 1)

        if offset_pixels.size == 0:
            return {
                "offset_mean_width_mm": 0.0,
                "confidence": 0.0
            }

        # Calculate the left and right margins for each row
        row_bounds = {}
        for y, x in offset_pixels:
            if y not in row_bounds:
                row_bounds[y] = [x, x]
            else:
                row_bounds[y][0] = min(row_bounds[y][0], x)
                row_bounds[y][1] = max(row_bounds[y][1], x)

        widths = [right - left + 1 for left, right in row_bounds.values()]
        mean_width = np.mean(widths)
        mean_width_mm = mean_width  # 1 pixel = 1 mm

        # confidence
        mask_area = np.sum(cleaned_mask)
        roi_area = self.original_roi_size[0] * self.original_roi_size[1]
        confidence = min(1.0, round(mask_area / roi_area * 3, 2))

        return {
            "offset_mean_width_mm": round(float(mean_width_mm), 2),
            "confidence": confidence

        }
