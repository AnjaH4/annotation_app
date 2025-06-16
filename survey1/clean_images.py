import os

def clean_directory(paths_file, target_directory, dry_run=True):
    """
    Deletes files from a directory and its subdirectories if they are not listed
    in the provided text file.

    Args:
        paths_file (str): The path to the .txt file containing the image paths to keep.
        target_directory (str): The directory to clean.
        dry_run (bool): If True, only prints the files that would be deleted.
                        If False, performs the deletion.
    """
    try:
        # Read the list of files to keep and store them in a set for efficient lookup.
        # Paths are normalized to use forward slashes for cross-platform compatibility.
        with open(paths_file, 'r') as f:
            files_to_keep = {line.strip().replace('\\', '/') for line in f}
        print(f"✅ Found {len(files_to_keep)} valid paths to keep.")
    except FileNotFoundError:
        print(f"❌ Error: The file '{paths_file}' was not found.")
        return

    files_to_delete = []
    # Recursively walk through the target directory.
    for root, _, files in os.walk(target_directory):
        for name in files:
            file_path = os.path.join(root, name)
            # Normalize the current file path to match the format in the text file.
            normalized_path = file_path.replace('\\', '/')

            # If the file is not in our list of files to keep, add it to the deletion list.
            if normalized_path not in files_to_keep:
                files_to_delete.append(file_path)

    # --- Deletion Logic ---
    if dry_run:
        print("\n--- 🌵 DRY RUN MODE 🌵 ---")
        if files_to_delete:
            print("The following files would be deleted:")
            for path in files_to_delete:
                print(f"  - {path}")
            print(f"\nTo permanently delete these {len(files_to_delete)} files, run the script with 'dry_run=False'.")
        else:
            print("✨ Your directories are already clean! No files to delete.")
    else:
        print(f"\n--- 🗑️ DELETING {len(files_to_delete)} FILES 🗑️ ---")
        if not files_to_delete:
            print("✨ No files to delete.")
            return

        for path in files_to_delete:
            try:
                os.remove(path)
                print(f"Deleted: {path}")
            except OSError as e:
                print(f"Error deleting {path}: {e}")
        print("\n✅ Deletion complete.")


if __name__ == '__main__':
    # --- CONFIGURATION ---

    # 1. Set the path to your text file containing the list of file paths to KEEP.
    #    Example: 'C:/Users/YourUser/Desktop/my_images.txt'
    image_list_filepath = '/home/anjah/Documents/mag/DeepFakes/FakeFacesSurvey/survey1/image_list5_4fr.txt'

    # 2. Set the root directory that you want to clean.
    #    Based on your example, this would be the base path.
    directory_to_clean = 'surveyapp/static/img/SBIs/sbi_fake/frames'

    # --- EXECUTION ---

    # 🚨 IMPORTANT: First, run the script with dry_run=True to review the files
    # that will be deleted.
    # After you confirm the list is correct, change this to dry_run=False to
    # actually delete the files.
    clean_directory(image_list_filepath, directory_to_clean, dry_run=False)