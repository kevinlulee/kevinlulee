import matplotlib.pyplot as plt
import tempfile
import webbrowser
import os

def show():
    """
    Saves the current Matplotlib figure to a temporary PNG file
    and opens it in the default web browser.
    """
    # Get the current figure
    fig = plt.gcf()

    # Create a temporary file with .png extension
    # delete=False ensures the file is not deleted immediately after closing,
    # so the browser has time to open it.
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        # Save the figure to the temporary file
        fig.savefig(tmpfile.name)
        temp_filepath = tmpfile.name

    # Close the figure to free up memory and prevent it from being displayed
    # by a standard backend later if any show calls are made.
    plt.close(fig)

    # Open the temporary file in the default web browser
    try:
        webbrowser.open("file://" + os.path.realpath(temp_filepath))
    except Exception as e:
        print(f"Could not open plot in browser: {e}")
        print(f"Plot saved temporarily to: {temp_filepath}")

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
