from github import Github
import os

TOKEN = os.environ.get('KDOG3682_GITHUB_API_KEY')
github = Github(TOKEN)
