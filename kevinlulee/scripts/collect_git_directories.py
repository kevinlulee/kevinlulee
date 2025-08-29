import kevinlulee as kx


def collect_git_directories(dirpath):
    results = kx.fdfind(
        dirs=[dirpath],
        query=".git",
        only_directories=True,
        include_dirs=[".git"],
    )
    return sorted(
        [kx.re.sub(r"/?\.git/?$", "", p) for p in results],
        key=kx.os.path.getmtime,
    )


if __name__ == "__main__":
    repos = collect_git_directories("~/")
    kx.cache_write('git_repositories.json', repos)
