import os
import shutil
import kevinlulee as kx
import re
from pathlib import Path



def get_filtered_files(directory, size_limit=50, delete_duplicates=True):
    """
    Get files from a directory that either:
    1. Have a number in parentheses (e.g., foo (1).MD)
    2. Are smaller than the specified size limit (default: 50 bytes)
    
    If a numbered file exists and its original (without number) exists with the same size,
    the numbered file is deleted.
    
    Args:
        directory: Path to the directory to search
        size_limit: Maximum file size in bytes (default: 50)
        delete_duplicates: If True, delete numbered files when original exists with same size
    
    Returns:
        dict with three lists: 'numbered_files', 'small_files', and 'deleted_files'
    """
    directory = Path(directory)
    
    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    
    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    # Pattern to match files with numbers in parentheses
    # Matches: foo (1).txt, bar (123).md, etc.
    pattern = re.compile(r'^(.+?)\s*\((\d+)\)(.*)$')
    
    numbered_files = []
    small_files = []
    deleted_files = []
    
    # First pass: collect all files
    for item in directory.iterdir():
        if item.is_file():
            # Check if filename matches pattern
            match = pattern.match(item.name)
            if match:
                numbered_files.append(item)
            
            # Check file size
            if item.stat().st_size < size_limit:
                small_files.append(item)
    
    # Second pass: process numbered files to check for duplicates
    if numbered_files and delete_duplicates:
        files_to_keep = []
        for numbered_file in numbered_files:
            match = pattern.match(numbered_file.name)
            if match:
                # Reconstruct original filename
                prefix = match.group(1).rstrip()
                suffix = match.group(3)
                original_name = prefix + suffix
                original_path = numbered_file.parent / original_name
                
                # Check if original exists and has same size
                should_delete = False
                if original_path.exists() and original_path.is_file():
                    if original_path.stat().st_size == numbered_file.stat().st_size:
                        should_delete = True
                
                if should_delete:
                    try:
                        numbered_file.unlink()
                        deleted_files.append(numbered_file.name)
                    except Exception as e:
                        print(f"Could not delete {numbered_file.name}: {e}")
                        files_to_keep.append(numbered_file)
                else:
                    files_to_keep.append(numbered_file)
            else:
                files_to_keep.append(numbered_file)
        
        numbered_files = files_to_keep
    
    return {
        'numbered_files': sorted(numbered_files),
        'small_files': sorted(small_files),
        'deleted_files': deleted_files
    }


def cleanup(target_dir):

    results = get_filtered_files(target_dir, size_limit=50)
    
    if results['deleted_files']:
        print("Deleted duplicate numbered files:")
        for name in results['deleted_files']:
            print(f"  {name}")
        print()
    
    if results['numbered_files']:
        print("Remaining files with numbers in parentheses:")
        for f in results['numbered_files']:
            print(f"  {f.name} ({f.stat().st_size} bytes)")
        print()
    
    if results['small_files']:
        print(f"Files smaller than 50 bytes:")
        for f in results['small_files']:
            print(f"  {f.name} ({f.stat().st_size} bytes)")


    kx.pretty_print(delete_files_by_extension(target_dir))


# def delete_files_by_extension(target_dir, exts = ['py', 'js', 'ts', 'tsx', 'deb']):
#     paths = kx.get_paths(target_dir, exts=exts, depth = 1)
#     # return kx.pretty_print(paths)
#     # return 
#     for path in paths:
#         kx.os.unlink(path)
#
#     return paths
#
#
# if __name__ == '__main__':
#     print(delete_files_by_extension(kx.DLDIR, exts = ['py']))


s = """

/mnt/chromeos/MyFiles/Downloads/code (2).json
/mnt/chromeos/MyFiles/Downloads/https：_www.nytimes.com_2025_09_05_business_social-security-wealth-benefits.html.html
/mnt/chromeos/MyFiles/Downloads/claude.ai-2025-11-01T16-11-02-412Z-dom.html
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-11-15 9.35.24 AM.png
/mnt/chromeos/MyFiles/Downloads/corpus_errors.zip
/mnt/chromeos/MyFiles/Downloads/error_refactor.zip
/mnt/chromeos/MyFiles/Downloads/unnamed.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-11-01 11.32.49 AM.png
/mnt/chromeos/MyFiles/Downloads/extracted.json
/mnt/chromeos/MyFiles/Downloads/manimlib-drawing.skill
/mnt/chromeos/MyFiles/Downloads/kdog3682_github_io.zip
/mnt/chromeos/MyFiles/Downloads/code (1).json
/mnt/chromeos/MyFiles/Downloads/luli-gapi-credentials.json
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-18 4.56.56 PM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-14 6.32.14 PM.png
/mnt/chromeos/MyFiles/Downloads/v1.pdf
/mnt/chromeos/MyFiles/Downloads/scratch.txt
/mnt/chromeos/MyFiles/Downloads/templates-minimal.zip
/mnt/chromeos/MyFiles/Downloads/long_division.py
/mnt/chromeos/MyFiles/Downloads/fs-view.zip
/mnt/chromeos/MyFiles/Downloads/files (2).zip
/mnt/chromeos/MyFiles/Downloads/nvim-api-docs.md
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-17 6.56.50 PM.png
/mnt/chromeos/MyFiles/Downloads/Kevin Lee - NYS Driver ID Form.pdf
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-11-18 6.20.59 PM.png
/mnt/chromeos/MyFiles/Downloads/sublime-merge_build-2112_amd64.deb
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-18 4.29.35 PM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-14 11.47.18 AM.png
/mnt/chromeos/MyFiles/Downloads/reservation_706516269.pdf
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-14 11.39.16 AM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-26 3.39.42 PM.png
/mnt/chromeos/MyFiles/Downloads/takeout-20250808T212106Z-1-001.zip
/mnt/chromeos/MyFiles/Downloads/client_secret_973933192887-8v1fra8m21t30412d078bqglu3rn2569.apps.googleusercontent.com.json
/mnt/chromeos/MyFiles/Downloads/chatgpt_conversation_2025-11-01-15-53-04.json
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-14 2.39.09 PM.png
/mnt/chromeos/MyFiles/Downloads/shape_friend.zip
/mnt/chromeos/MyFiles/Downloads/files.zip
/mnt/chromeos/MyFiles/Downloads/math_in_focus_reteach_5a.pdf
/mnt/chromeos/MyFiles/Downloads/claude-chat-downloader.zip
/mnt/chromeos/MyFiles/Downloads/Claude-JavaScript console script for downloading code blocks (1).md
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-19 6.55.03 PM.png
/mnt/chromeos/MyFiles/Downloads/mv44.pdf
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-14 2.40.25 PM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-27 10.13.35 PM.png
/mnt/chromeos/MyFiles/Downloads/ChatGPT-Python watchdog explanation.md
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-11-15 9.35.12 AM.png
/mnt/chromeos/MyFiles/Downloads/extracted (1).txt
/mnt/chromeos/MyFiles/Downloads/tempfile.pdf
/mnt/chromeos/MyFiles/Downloads/log_viewer_component.jsx
/mnt/chromeos/MyFiles/Downloads/extracted.txt
/mnt/chromeos/MyFiles/Downloads/https：_www.seriouseats.com_how-to-wrap-sandwich-sub-wrap-deli-style.html
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-18 4.22.56 PM.png
/mnt/chromeos/MyFiles/Downloads/sublime-merge_build-2110_amd64.deb
/mnt/chromeos/MyFiles/Downloads/kitchen-sink-samples-renamed.zip
/mnt/chromeos/MyFiles/Downloads/749771938-PRIMARY-GRADE-CHALLENGE-MATH.pdf
/mnt/chromeos/MyFiles/Downloads/long_division_fixed.py
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-11-15 9.35.38 AM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-17 11.25.09 AM.png
/mnt/chromeos/MyFiles/Downloads/morning_birdsong.yml
/mnt/chromeos/MyFiles/Downloads/ChatGPT_Conversation_2025-11-01-15-20-49.md
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-11-15 9.34.20 AM.png
/mnt/chromeos/MyFiles/Downloads/code (5).json
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-12-08 11.43.21 AM.png
/mnt/chromeos/MyFiles/Downloads/https：_chatgpt.com_c_69062321-61a4-8326-8aca-953aaec22cb9.html
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-12-08 12.04.04 PM.png
/mnt/chromeos/MyFiles/Downloads/instructions.txt
/mnt/chromeos/MyFiles/Downloads/REFACTOR_SUMMARY.md
/mnt/chromeos/MyFiles/Downloads/ChatGPT-Backend file watcher setup.md
/mnt/chromeos/MyFiles/Downloads/extracted (1).json
/mnt/chromeos/MyFiles/Downloads/extracted (2).json
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-18 4.53.19 PM.png
/mnt/chromeos/MyFiles/Downloads/COMPARISON.md
/mnt/chromeos/MyFiles/Downloads/claude.ai-2025-11-01T16-09-12-434Z-dom.html
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-15 10.44.45 AM.png
/mnt/chromeos/MyFiles/Downloads/Claude-Node class refactoring clarification.md
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-11-01 11.36.50 AM.png
/mnt/chromeos/MyFiles/Downloads/react-fzf-kit.zip
/mnt/chromeos/MyFiles/Downloads/id44.pdf
/mnt/chromeos/MyFiles/Downloads/palette_map.json
/mnt/chromeos/MyFiles/Downloads/code.json
/mnt/chromeos/MyFiles/Downloads/equation_expression.txt
/mnt/chromeos/MyFiles/Downloads/page-2025-11-01T16-01-21-658Z-dom.html
/mnt/chromeos/MyFiles/Downloads/code (4).json
/mnt/chromeos/MyFiles/Downloads/long_division_fixed (1).py
/mnt/chromeos/MyFiles/Downloads/code-implementation.skill
/mnt/chromeos/MyFiles/Downloads/freeformatter-out.html
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-14 6.32.49 PM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-11-15 9.34.30 AM.png
/mnt/chromeos/MyFiles/Downloads/files (1).zip
/mnt/chromeos/MyFiles/Downloads/more_python_errors.zip
/mnt/chromeos/MyFiles/Downloads/code (3).json
/mnt/chromeos/MyFiles/Downloads/body (1).html
/mnt/chromeos/MyFiles/Downloads/claude-chat-2025-11-01.txt
/mnt/chromeos/MyFiles/Downloads/MD Curriculum Guide 2024-2025.pdf
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-17 6.59.44 PM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-14 11.47.56 AM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-26 5.03.55 PM.png
/mnt/chromeos/MyFiles/Downloads/body.html
/mnt/chromeos/MyFiles/Downloads/typstyle-aarch64-unknown-linux-gnu
/mnt/chromeos/MyFiles/Downloads/claude-chat-2025-11-18.txt
/mnt/chromeos/MyFiles/Downloads/ny_grade5_math_2025.md
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-15 9.51.29 AM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-19 5.31.46 PM.png
/mnt/chromeos/MyFiles/Downloads/extracted (3).json
/mnt/chromeos/MyFiles/Downloads/ChatGPT-Dotfile management script.md
/mnt/chromeos/MyFiles/Downloads/chatgpt.com-2025-11-01T15-57-20-317Z-dom.html
/mnt/chromeos/MyFiles/Downloads/yeye & nainai.jpg
/mnt/chromeos/MyFiles/Downloads/mv44 (1).pdf
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-17 7.39.43 PM.png
/mnt/chromeos/MyFiles/Downloads/birdsong.txt
/mnt/chromeos/MyFiles/Downloads/Claude-JavaScript console script for downloading code blocks.md
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-19 11.07.19 PM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-17 6.45.00 PM.png
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-11-26 7.58.52 AM.png
/mnt/chromeos/MyFiles/Downloads/ChatGPT-Text similarity function.md
/mnt/chromeos/MyFiles/Downloads/shapefriend_patched_files.zip
/mnt/chromeos/MyFiles/Downloads/hsk_by_category.json
/mnt/chromeos/MyFiles/Downloads/d42076a2-abcf-4f5b-8ad8-197afcd40b93
/mnt/chromeos/MyFiles/Downloads/Screenshot 2025-10-16 10.42.30 AM.png
/mnt/chromeos/MyFiles/Downloads/README.md
""".strip().splitlines()


#
# paths = kx.get_paths(s, exclude = 'yeye|nainai|luli', include = 'REFACTOR|Claude|ChatGPT|README|(?:code|extracted)(?: \(\d+\))?\.(?:json|txt)')
#
# more_paths = kx.get_paths(s, exts = ['png', 'tsx', 'jsx', 'py', 'js', 'ts', 'svg', 'html', ])
# a = "/mnt/chromeos/MyFiles/Downloads/palette_map.json"
# print(a in paths)
import nvim
# nvim.fs.clip(sorted(paths + more_paths))
# files = paths + more_paths
# for file in files:
#     os.unlink(file)


dir = '~/scratch/__temp__/'

def move_directory_contents(src_dir, dst_dir):
    """ moves all contents from the src_dir to the dst_dir """
    
    src_path = Path(src_dir).expanduser()
    dst = Path(dst_dir).expanduser()
    dst.mkdir(parents=True, exist_ok=True)

    for item in src_path.iterdir():
        print(item)
        # if item.name == '.Trash':
        #     continue
        # return 
        # print(str(item))
        # print(str(dst))
        # return 
        # shutil.move(str(item), str(dst))
    return 
# move_directory_contents(dir, os.path.join(kx.DLDIR, 'downloads_2024_to_2025'))
