def set_git_auth_token_if_author(self):
    # Load .env variables
    load_dotenv()
    token = os.getenv("KEVINLULEE_GITHUB_API_KEY")

    if not token:
        print("GITHUB_TOKEN not found in .env")
        return

    first_author = self.cmd(
        "log", "--reverse", "--pretty=format:%an", "--max-parents=0"
    )

    if first_author.lower() == "kdog3682":
        # Get the current remote URL
        origin_url = self.cmd("remote", "get-url", "origin").strip()

        # Only modify if using HTTPS
        if origin_url.startswith("https://"):
            repo_path = origin_url.replace("https://github.com/", "")
            new_url = f"https://{token}@github.com/{repo_path}"

            self.cmd("git", "remote", "set-url", "origin", new_url)
            print(f"Set new origin URL with token for author: {first_author}")
        else:
            print("Remote is not HTTPS, skipping token injection.")

    else:
        print(
            f"Skipping: first commit author is {first_author}, not kevinlulee"
        )
