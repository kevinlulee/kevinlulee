
import subprocess
import re
import os
from kevinlulee import git

def git_history_parser(repo_path):
    g = git.load(repo_path, strict = True)
    
    git_log_cmd = [
        "git", "-C", repo_path, "log", "--numstat", "--date=iso", "--pretty=format:%H|%an|%ad|%s"
    ]
    result = g.cmd(git_log_cmd)
    
    commits = []
    commit = None
    
    for line in result.stdout.splitlines():
        commit_match = re.match(r"^(\w+)\|(.*?)\|(.*?)\|(.*)$", line)
        if commit_match:
            if commit:
                commits.append(commit)
            commit = {
                "hash": commit_match.group(1),
                "author": commit_match.group(2),
                "date": commit_match.group(3),
                "message": commit_match.group(4),
                "files": []
            }
        elif commit and line.strip():
            numstat_match = re.match(r"^(\d+|-)\s+(\d+|-)\s+(.+)$", line)
            if numstat_match:
                insertions = numstat_match.group(1)
                deletions = numstat_match.group(2)
                filename = numstat_match.group(3)
                
                if insertions == "-":
                    insertions = 0
                if deletions == '-':
                    deletions = 0

                # 

                changes = int(insertions) + int(deletions)
                    
                file_entry = {
                    "filename": filename,
                    "deletions": deletions,
                    'insertions': insertions,
                }
                
                commit["files"].append(file_entry)
    
    if commit:
        commits.append(commit)
    
    return commits

