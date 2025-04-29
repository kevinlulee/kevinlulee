import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

class Arrow:
    def __init__(self, start, end, head_width=0.1, head_length=0.2):
        """
        Create an arrow from start point to end point.
        
        Parameters:
        - start: Starting point (x, y)
        - end: Ending point (x, y)
        - head_width: Width of the arrow head
        - head_length: Length of the arrow head
        """
        self.start = np.array(start)
        self.end = np.array(end)
        self.head_width = head_width
        self.head_length = head_length
        
        # Calculate the line vector
        self.vec = self.end - self.start
        self.length = np.linalg.norm(self.vec)
        self.unit_vec = self.vec / self.length if self.length > 0 else np.array([0, 0])
        
        # Calculate points for the arrow head (triangle)
        self.arrow_head = self._calculate_arrow_head()
    
    def _calculate_arrow_head(self):
        """Calculate the three points of the arrow head (triangle)."""
        if self.length <= self.head_length:
            # If the arrow is too short, just use the end point
            return np.array([self.end, self.end, self.end])
        
        # Arrow head base point
        base = self.end - self.unit_vec * self.head_length
        
        # Calculate the perpendicular vector for the arrow head width
        perp = np.array([-self.unit_vec[1], self.unit_vec[0]])
        
        # Calculate the three points of the arrow head
        p1 = base + perp * (self.head_width / 2)
        p2 = self.end  # The tip of the arrow
        p3 = base - perp * (self.head_width / 2)
        
        return np.array([p1, p2, p3])
    
    def draw(self, ax=None, color='blue', linewidth=2):
        """Draw the arrow on the specified matplotlib axis."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
        
        # Draw the line (shaft of the arrow)
        line_end = self.end - self.unit_vec * self.head_length if self.length > self.head_length else self.start
        ax.plot([self.start[0], line_end[0]], [self.start[1], line_end[1]], 
                color=color, linewidth=linewidth)
        
        # Draw the arrow head (triangle)
        arrow_head = Polygon(self.arrow_head, closed=True, color=color)
        ax.add_patch(arrow_head)
        
        return ax

# Example usage
if __name__ == "__main__":
    # Create an arrow from (0,0) to (1,1)
    arrow = Arrow([0, 0], [1, 1])
    
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Draw the arrow
    arrow.draw(ax)
    
    # Set axis limits with some padding
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    
    # Add grid and labels
    ax.grid(True)
    ax.set_aspect('equal')
    ax.set_title('Arrow Object')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    
    plt.show()
