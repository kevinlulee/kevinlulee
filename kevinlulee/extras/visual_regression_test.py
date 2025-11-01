import numpy as np
from PIL import Image
import io
import cairosvg
import os
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SimilarityMetrics:
    """Container for similarity metrics."""
    pixel_similarity: float
    mse: float
    ssim: float
    histogram_similarity: float
    overall_similarity: float
    
    def __str__(self):
        return (
            f"Pixel Similarity: {self.pixel_similarity:.1%}\n"
            f"MSE: {self.mse:.2f}\n"
            f"SSIM: {self.ssim:.1%}\n"
            f"Histogram Similarity: {self.histogram_similarity:.1%}\n"
            f"Overall Similarity: {self.overall_similarity:.1%}"
        )


class SVGComparator:
    """Compare two SVG images with fine-grained control over metrics."""
    
    def __init__(
        self,
        size: Optional[Tuple[int, int]] = None,
        enable_pixel: bool = False,
        enable_mse: bool = False,
        enable_histogram: bool = False,
        enable_ssim: bool = True,
        ssim_weight: float = 0.6,
        pixel_weight: float = 0.2,
        histogram_weight: float = 0.2
    ):
        """
        Initialize SVG comparator with configurable metrics.
        
        Args:
            size: Size to render SVGs (width, height). If None, uses native dimensions.
            enable_pixel: Calculate pixel-by-pixel similarity
            enable_mse: Calculate Mean Squared Error
            enable_ssim: Calculate Structural Similarity Index
            enable_histogram: Calculate histogram similarity
            ssim_weight: Weight for SSIM in overall calculation
            pixel_weight: Weight for pixel similarity in overall calculation
            histogram_weight: Weight for histogram similarity in overall calculation
        """
        self.size = size
        self.enable_pixel = enable_pixel
        self.enable_mse = enable_mse
        self.enable_ssim = enable_ssim
        self.enable_histogram = enable_histogram
        
        # Normalize weights
        total = ssim_weight + pixel_weight + histogram_weight
        self.ssim_weight = ssim_weight / total
        self.pixel_weight = pixel_weight / total
        self.histogram_weight = histogram_weight / total
        
        self._arr1 = None
        self._arr2 = None
    
    def _svg_to_array(self, svg_path: str) -> np.ndarray:
        """Convert SVG to numpy array."""
        svg_path = os.path.expanduser(svg_path)
        with open(svg_path, 'r') as f:
            svg_data = f.read()
        
        kwargs = {'bytestring': svg_data.encode('utf-8')}
        if self.size is not None:
            kwargs['output_width'] = self.size[0]
            kwargs['output_height'] = self.size[1]
        
        png_data = cairosvg.svg2png(**kwargs)
        img = Image.open(io.BytesIO(png_data)).convert('RGB')
        return np.array(img)
    
    def _calculate_pixel_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate exact pixel match ratio."""
        return np.mean(img1 == img2)
    
    def _calculate_mse(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Mean Squared Error."""
        return np.mean((img1.astype(float) - img2.astype(float)) ** 2)
    
    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Structural Similarity Index."""
        gray1 = np.mean(img1, axis=2)
        gray2 = np.mean(img2, axis=2)
        
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2
        
        mu1 = np.mean(gray1)
        mu2 = np.mean(gray2)
        
        sigma1_sq = np.var(gray1)
        sigma2_sq = np.var(gray2)
        sigma12 = np.cov(gray1.flatten(), gray2.flatten())[0, 1]
        
        numerator = (2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)
        denominator = (mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2)
        
        return numerator / denominator
    
    def _calculate_histogram_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate histogram similarity using correlation."""
        hist1 = np.histogram(img1.flatten(), bins=256, range=(0, 255))[0]
        hist2 = np.histogram(img2.flatten(), bins=256, range=(0, 255))[0]
        
        hist1 = hist1 / np.sum(hist1)
        hist2 = hist2 / np.sum(hist2)
        
        correlation = np.corrcoef(hist1, hist2)[0, 1]
        return max(0, correlation)
    
    def compare(self, svg1_path: str, svg2_path: str) -> SimilarityMetrics:
        """
        Compare two SVG files and return similarity metrics.
        
        Args:
            svg1_path: Path to first SVG file
            svg2_path: Path to second SVG file
        
        Returns:
            SimilarityMetrics object with all enabled metrics
        """
        # Convert SVGs to arrays
        self._arr1 = self._svg_to_array(svg1_path)
        self._arr2 = self._svg_to_array(svg2_path)
        
        # Calculate enabled metrics
        pixel_sim = self._calculate_pixel_similarity(self._arr1, self._arr2) if self.enable_pixel else 0.0
        mse = self._calculate_mse(self._arr1, self._arr2) if self.enable_mse else 0.0
        ssim = self._calculate_ssim(self._arr1, self._arr2) if self.enable_ssim else 0.0
        hist_sim = self._calculate_histogram_similarity(self._arr1, self._arr2) if self.enable_histogram else 0.0
        
        # Calculate overall similarity based on enabled metrics and weights
        overall = 0.0
        if self.enable_ssim:
            overall += ssim * self.ssim_weight
        if self.enable_pixel:
            overall += pixel_sim * self.pixel_weight
        if self.enable_histogram:
            overall += hist_sim * self.histogram_weight
        
        return SimilarityMetrics(
            pixel_similarity=round(float(pixel_sim), 3),
            mse=round(float(mse), 2),
            ssim=round(float(ssim), 3),
            histogram_similarity=round(float(hist_sim), 3),
            overall_similarity=round(float(overall), 3)
        )
    
    def are_same(
        self,
        svg1_path: str,
        svg2_path: str,
        threshold: float = 0.95,
        metric: str = 'ssim'
    ) -> bool:
        """
        Check if two SVG images are basically the same.
        
        Args:
            svg1_path: Path to first SVG file
            svg2_path: Path to second SVG file
            threshold: Similarity threshold (0-1). Default 0.95 means 95% similar.
            metric: Which metric to use ('ssim', 'pixel', 'histogram', 'overall')
        
        Returns:
            True if images meet the similarity threshold, False otherwise
        """
        metrics = self.compare(svg1_path, svg2_path)
        
        if metric == 'ssim':
            return metrics.ssim >= threshold
        elif metric == 'pixel':
            return metrics.pixel_similarity >= threshold
        elif metric == 'histogram':
            return metrics.histogram_similarity >= threshold
        elif metric == 'overall':
            return metrics.overall_similarity >= threshold
        else:
            raise ValueError(f"Unknown metric: {metric}. Use 'ssim', 'pixel', 'histogram', or 'overall'")


comparator = SVGComparator()

class VisualRegressionTestSuite:
    def __init__(self):
        
    


# Example usage
if __name__ == "__main__":
    # Basic usage - all metrics enabled
    paths = ('~/scratch/a.svg', '~/scratch/b.svg')
    # Check if images are basically the same
    is_same = comparator.are_same(*paths)
    print(f"Images are basically the same: {is_same}")


# a 
