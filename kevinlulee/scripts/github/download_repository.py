from typing import TYPE_CHECKING

import kevinlulee

if TYPE_CHECKING:
    from github import Github

from github import Github
import os
import re
import requests
import pathspec
from kevinlulee import fancy_filetree, bartender

class GitHubDownloader:
    """
    A class to download a subdirectory from a GitHub repository,
    with support for ignoring files and directories based on patterns.

    self.display()
        prints the filetree

    self.local_dest
        the download path (~/github/{name})

    self.download(<url>)
        the entry point
    """

    def __init__(self, github: Github, ignore_patterns: list = None):
        self.github = github
        self.ignore_patterns = ignore_patterns if ignore_patterns is not None else []
        self.spec = pathspec.PathSpec.from_lines('gitwildmatch', self.ignore_patterns)
        self.local_dest = ''

    def _parse_github_url(self, url: str) -> tuple[str, str]:
        """Parses the GitHub URL to extract repository name and subdirectory."""
        match = re.match(r'https://github\.com/([^/]+)/([^/]+)(/tree/[^/]+/(.+))?', url)
        if not match:
            raise ValueError('Invalid GitHub URL format')
        user, repo_name, _, subdir = match.groups()
        return f'{user}/{repo_name}', subdir or ''

    def _should_ignore(self, rel_path: str) -> bool:
        """Checks if a relative path should be ignored based on the patterns."""
        return self.spec.match_file(rel_path)

    def _download_file(self, file_content, dest_dir: str):
        """Downloads a single file."""
        # Get the path relative to the original subdir
        rel_path = file_content.path[len(self.subdir.rstrip('/')) + 1:] if self.subdir else file_content.path

        if self._should_ignore(rel_path):
            print(f"Ignoring file: {rel_path}")
            return

        file_path = os.path.join(dest_dir, rel_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        print(f"Downloading file: {rel_path}")
        try:
            r = requests.get(file_content.download_url, stream=True)
            r.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {file_content.download_url}: {e}")


    def _download_dir(self, contents_list, dest_dir: str):
        """Recursively downloads contents of a directory."""
        for content in contents_list:
            # Get the path relative to the original subdir
            rel_path_full = content.path[len(self.subdir.rstrip('/')) + 1:] if self.subdir else content.path

            if content.type == 'dir':
                # Add a trailing slash for directory matching in pathspec
                if self._should_ignore(rel_path_full + '/'):
                    print(f"Ignoring directory: {rel_path_full}")
                    continue
                print(f"Entering directory: {rel_path_full}")
                try:
                    subdir_contents = self.repo.get_contents(content.path)
                    self._download_dir(subdir_contents, dest_dir)
                except Exception as e:
                     print(f"Error listing contents of directory {content.path}: {e}")

            else: # file
                self._download_file(content, dest_dir)

    def download(self, github_url, name = None):
        """Starts the download process."""

        self.repo_name, self.subdir = self._parse_github_url(github_url)

        if not name: name = self.repo_name.split('/')[-1].lower()
        self.local_dest = os.path.expanduser(os.path.join('~/github', name))

        if os.path.exists(self.local_dest):
            print('already exists')
            return 
        self.repo = self.github.get_repo(self.repo_name)

        print(f"Starting download from {github_url} to {self.local_dest}")
        try:
            initial_contents = self.repo.get_contents(self.subdir)
            self._download_dir(initial_contents, self.local_dest)
            print("Download complete.")
        except Exception as e:
            print(f"An error occurred during the download process: {e}")
    
    def display(self):
        bartender(fancy_filetree(self.local_dest))

# Example Usage:
if __name__ == "__main__":

    GITHUB_URL = 'https://github.com/google-deepmind/alphafold/tree/main/alphafold'
    IGNORE_PATTERNS = [
        '*.png',
        '*.gif',
        '*.jpg',
        '*.jpeg',
        '*/test/*',
        '*.config.js',
    ]


    from kevinlulee.initializers.github import github # initializes it
    downloader = GitHubDownloader(
        github=github,
        ignore_patterns=IGNORE_PATTERNS
    )

    downloader.download(GITHUB_URL)
    downloader.display()
