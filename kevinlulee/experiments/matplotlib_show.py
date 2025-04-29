import tempfile
import webbrowser
import os
from kevinlulee import writefile
from kevinlulee.scripts.matplotshow import matplotshow as show

# Example Usage:
if __name__ == '__main__':
    # Create a simple plot
    plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
    plt.title("Example Plot")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.grid(True)

    # Use the custom show() function instead of plt.show()
    show()

    # You can create another plot, and it will also be shown in a new browser tab
    plt.figure() # Create a new figure
    plt.bar(['A', 'B', 'C'], [10, 15, 5])
    plt.title("Example Bar Chart")
    show()

    # Note: The temporary files are not automatically cleaned up by this script.
    # You might want to add cleanup logic if you generate many plots.
    # For simple testing, manually cleaning your temp directory is usually fine.
