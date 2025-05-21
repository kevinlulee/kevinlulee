#!/usr/bin/env python3
"""
Script to search through git history for filenames containing a specific word.
"""
import subprocess
import sys
import re

def search_git_history_for_filename(search_term):
    """
    Search through all git history for filenames containing the search term.
    
    Args:
        search_term (str): The term to search for in filenames.
        
    Returns:
        list: Tuples of (commit_hash, filename) where the filename contains the search term.
    """
    try:
        # Check if we're in a git repository
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                       check=True, 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository")
        sys.exit(1)
    
    try:
        # Get all filenames that have ever existed in the repository
        # The format is: commit_hash filename
        cmd = ['git', 'log', '--all', '--format=%H', '--name-only']
        result = subprocess.run(cmd, 
                               check=True, 
                               capture_output=True, 
                               text=True)
        
        s = result.stdout.strip()
        print(s)
        lines = s.split('\n')
        
        matches = []
        current_commit = None
        
        # Process the output
        for line in lines:
            if not line:  # Skip empty lines
                continue
                
            # If this is a commit hash (40 hex characters)
            if re.match(r'^[0-9a-f]{40}$', line):
                current_commit = line
            # Otherwise it's a filename
            elif current_commit and search_term.lower() in line.lower():
                matches.append((current_commit, line))
                
        return matches
    
    except subprocess.CalledProcessError as e:
        print(f"Error executing git command: {e}")
        sys.exit(1)

def main(search_term):
    matches = search_git_history_for_filename(search_term)
    
    if not matches:
        print("No matching filenames found in git history.")
        return
    
    print(f"Found {len(matches)} matching filenames:")
    
    # Group by unique filenames
    unique_files = {}
    for commit, filename in matches:
        if filename not in unique_files:
            unique_files[filename] = []
        unique_files[filename].append(commit)
    
    # Print results grouped by filename
    for filename, commits in unique_files.items():
        print(f"\nFilename: {filename}")
        print(f"Found in {len(commits)} commits")
        # Print first and last commit for this file
        if len(commits) > 0:
            first_commit = commits[-1]  # Last in the list is earliest commit
            last_commit = commits[0]    # First in the list is latest commit
            
            # Get commit details
            cmd_first = ['git', 'show', '-s', '--format=%h %an <%ae> %ad', first_commit]
            cmd_last = ['git', 'show', '-s', '--format=%h %an <%ae> %ad', last_commit]
            
            first_result = subprocess.run(cmd_first, capture_output=True, text=True, check=True)
            last_result = subprocess.run(cmd_last, capture_output=True, text=True, check=True)
            
            print(f"First commit: {first_result.stdout.strip()}")
            print(f"Latest commit: {last_result.stdout.strip()}")

if __name__ == "__main__":
    import os
    os.chdir('/home/kdog3682/projects/hammymathclass/')
    main('consistent')




