def move_directory_to_existing_directory(
    source_dir, destination_dir, delete_source_directory_afterwards=True
):
    """Moves all files and subdirectories from the source directory
    to the destination directory.

    Args:
        source_dir (str): The path to the source directory.
        destination_dir (str): The path to the destination directory.
    """
    import os
    import shutil

    source_dir = os.path.expanduser(source_dir)
    destination_dir = os.path.expanduser(destination_dir)
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return
    if not os.path.isdir(destination_dir):
        print(
            f"Error: Destination directory '{destination_dir}' does not exist."
        )
        return

    for item in os.listdir(source_dir):
        source_item_path = os.path.join(source_dir, item)
        destination_item_path = os.path.join(destination_dir, item)
        try:
            shutil.move(source_item_path, destination_item_path)
            print(f"Moved '{item}' from '{source_dir}' to '{destination_dir}'")
        except Exception as e:
            print(f"Error moving '{item}': {e}")

    if delete_source_directory_afterwards:
        if len(os.listdir(source_dir)) == 0:
            shutil.rmtree(source_dir)  # delete the empty dir after
