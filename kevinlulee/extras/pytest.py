import os
import kevinlulee as kx
def pytest(
    *paths,
    config_file="~/dotfiles/templates/pytest.ini",
    cwd=None,
    verbose: bool = True, 
    maxfail: int = 0,
    collect_only: bool = False,
    rootdir = True,
):
    parts = ["pytest"]
    paths = kx.flat(paths)

    if config_file:
        parts += ["--config-file", str(os.path.expanduser(config_file))]

    if collect_only:
        parts.append('--collect-only')

    for p in paths:
        parts.append(str(p))

    if verbose:
        parts.append("-v")

    if maxfail:
        parts += ["--maxfail", str(maxfail)]

    if rootdir:
        if rootdir == True:
            rootdir = kx.find_project_root(paths[0])
        parts += ["--rootdir", rootdir]

    return kx.bash_shell(parts)
