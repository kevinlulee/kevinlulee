from manimlib import *
import numpy as np

class Document(Mobject):
    """
    A class for creating document-like layouts with manimlib.
    Uses the same architecture as Scene but without camera animations.
    Sets up a page with dimensions 8.5 × 11 inches by default.
    """
    CONFIG = {
        "width": 8.5,
        "height": 11,
        "margin": 0.5,  # Margin in inches
        "flipped": False,  # Whether to exchange width and height
        "background_color": WHITE,
    }
    
    def __init__(self, **kwargs):
        super().__init__()
        
        # Apply flipped orientation if needed
        if self.flipped:
            self.width, self.height = self.height, self.width
            
        # Convert inches to manimlib units
        # Assuming standard manimlib coordinates where height = 8 units
        self.scale_factor = 8 / self.height
        self.width_units = self.width * self.scale_factor
        self.height_units = self.height * self.scale_factor
        self.margin_units = self.margin * self.scale_factor
        
        # Create the page background
        self.page = Rectangle(
            width=self.width_units,
            height=self.height_units,
            fill_color=self.background_color,
            fill_opacity=1,
            stroke_width=1,
            stroke_color=LIGHT_GREY
        )
        self.add(self.page)
        
        # Set up content area (accounting for margins)
        self.content_width = self.width_units - 2 * self.margin_units
        self.content_height = self.height_units - 2 * self.margin_units
        self.content_area = Rectangle(
            width=self.content_width,
            height=self.content_height,
            stroke_width=0,
            fill_opacity=0
        )
        self.add(self.content_area)
