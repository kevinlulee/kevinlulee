from pprint import pprint
import subprocess
import re
import os
from kevinlulee import GitRepo

def parse_git_history(path):
    repo = GitRepo(path)

    cmd = ["log", "--numstat", "--date=iso", "--pretty=format:%H|%an|%ad|%s"]
    result = repo.cmd(*cmd)

    commits = []
    commit = None

    for line in result.splitlines():
        commit_match = re.search(r"^(\w+)\|(.*?)\|(.*?)\|(.*)$", line)
        if commit_match:
            if commit:
                commits.append(commit)
            commit = {
                "hash": commit_match.group(1),
                "author": commit_match.group(2),
                "date": commit_match.group(3),
                "message": commit_match.group(4),
                "files": [],
            }
        elif commit and line.strip():
            numstat_match = re.match(r"^(\d+|-)\s+(\d+|-)\s+(.+)$", line)
            if numstat_match:
                insertions = numstat_match.group(1)
                deletions = numstat_match.group(2)
                filename = numstat_match.group(3)

                if insertions == "-":
                    insertions = 0
                if deletions == "-":
                    deletions = 0

                changes = int(insertions) + int(deletions)

                file_entry = {
                    "filename": filename,
                    "deletions": deletions,
                    "insertions": insertions,
                }

                commit["files"].append(file_entry)

    if commit:
        commits.append(commit)

    return commits



# path = "/home/kdog3682/projects/old_projects/VSCodeExtensions/qwe-jump/.git/"
# pprint(parse_git_history(path))
