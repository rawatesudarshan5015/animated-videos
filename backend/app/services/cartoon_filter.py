"""
Cartoon style filter service for video frames.
Uses OpenCV to apply cartoon-like effects to images.
"""
import cv2
import numpy as np


class CartoonFilter:
    """Applies cartoon-style effects to images using OpenCV."""

    @staticmethod
    def apply_cartoon_filter(frame: np.ndarray, intensity: float = 1.0) -> np.ndarray:
        """
        Apply cartoon-style filter to a single frame.
        
        Uses bilateral filtering + edge detection to create cartoon effect.
        - Bilateral filter: Reduces noise while preserving edges
        - Edge detection: Highlights outlines
        - Color reduction: Simplifies color palette
        
        Args:
            frame: Input frame (BGR image from OpenCV)
            intensity: Filter strength (0.5 to 2.0, default 1.0)
                      Higher = more cartoon effect
            
        Returns:
            Filtered frame with cartoon effect
        """
        if frame is None or frame.size == 0:
            raise ValueError("Invalid frame: frame is None or empty")

        # Normalize intensity
        intensity = max(0.5, min(2.0, intensity))

        # Convert to RGB for processing (OpenCV uses BGR)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Step 1: Bilateral filtering (edge-preserving blur)
        # This creates smooth regions while keeping edges sharp
        num_bilateral = int(9 * intensity)
        if num_bilateral % 2 == 0:
            num_bilateral += 1
        img_filtered = cv2.bilateralFilter(img_rgb, num_bilateral, 75, 75)

        # Step 2: Convert to grayscale for edge detection
        img_gray = cv2.cvtColor(img_filtered, cv2.COLOR_RGB2GRAY)

        # Step 3: Adaptive thresholding for edge detection
        # Creates black outlines on white background
        img_edges = cv2.adaptiveThreshold(
            img_gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            2
        )

        # Step 4: Invert edges (white outlines on black background)
        img_edges = cv2.bitwise_not(img_edges)

        # Step 5: Quantize colors (reduce color palette)
        # Create cartoon look by reducing colors
        img_cartoon = img_filtered.copy()
        for i in range(3):  # Process each color channel
            img_cartoon[:, :, i] = (img_cartoon[:, :, i] // 25) * 25

        # Step 6: Dilate edges for more visible outlines
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        img_edges = cv2.dilate(img_edges, kernel, iterations=1)

        # Step 7: Resize edges to match frame dimensions
        img_edges_rgb = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

        # Step 8: Combine cartoon image with edges
        # Where edges are white (255), use black; elsewhere use cartoon colors
        img_result = np.where(img_edges_rgb == 255, 0, img_cartoon)

        # Convert back to BGR for OpenCV
        img_result_bgr = cv2.cvtColor(img_result.astype(np.uint8), cv2.COLOR_RGB2BGR)

        return img_result_bgr

    @staticmethod
    def apply_light_cartoon(frame: np.ndarray) -> np.ndarray:
        """
        Apply a lighter, faster cartoon effect.
        Good for real-time or low-resource scenarios.
        
        Args:
            frame: Input frame (BGR image)
            
        Returns:
            Filtered frame with light cartoon effect
        """
        if frame is None or frame.size == 0:
            raise ValueError("Invalid frame: frame is None or empty")

        # Light bilateral filter (faster)
        img_filtered = cv2.bilateralFilter(frame, 9, 75, 75)

        # Simple color quantization
        img_cartoon = img_filtered.copy()
        for i in range(3):
            img_cartoon[:, :, i] = (img_cartoon[:, :, i] // 32) * 32

        return img_cartoon

    @staticmethod
    def apply_heavy_cartoon(frame: np.ndarray) -> np.ndarray:
        """
        Apply a heavier, more pronounced cartoon effect.
        More CPU-intensive but creates stronger effect.
        
        Args:
            frame: Input frame (BGR image)
            
        Returns:
            Filtered frame with heavy cartoon effect
        """
        if frame is None or frame.size == 0:
            raise ValueError("Invalid frame: frame is None or empty")

        # Heavy bilateral filtering
        img_filtered = cv2.bilateralFilter(frame, 15, 80, 80)

        # Convert to LAB color space for better color processing
        img_lab = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2LAB)

        # Quantize each channel
        for i in range(3):
            img_lab[:, :, i] = (img_lab[:, :, i] // 20) * 20

        # Convert back to BGR
        img_cartoon = cv2.cvtColor(img_lab, cv2.COLOR_LAB2BGR)

        return img_cartoon
