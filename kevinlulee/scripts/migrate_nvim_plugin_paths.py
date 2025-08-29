import os
import re
import kevinlulee as kx
ROOT_DIR = "/home/kdog3682/projects/python/maelstrom/lib/nvim/plugins/v1/"

# Keep the tilde version for source edits; expand to absolute paths for filesystem ops.
OLD_ROOT_TILDE = "~/.cache/maelstrom/"
NEW_ROOT_TILDE = "~/data/nvim/plugins/"
OLD_ROOT_ABS = os.path.expanduser(OLD_ROOT_TILDE)
NEW_ROOT_ABS = os.path.expanduser(NEW_ROOT_TILDE)

# Regex to *parse/replace* data_path values; captures the quote and the tail after the root.
DATA_PATH_RE = re.compile(
    r'data_path\s*=\s*(["\'])~\/\.cache\/maelstrom\/([^"\']+)\1'
)

# Pattern to *find files* with your kx.rg (a bit looser, to ensure we catch variants/spacing)
RG_PAT = r'data_path\s*=\s*["\']~/.cache/maelstrom/.*?["\']'
RG_PAT = ''' data_path\s*=\s*["']~/.cache/maelstrom/[^"']*["'] '''.strip()
RG_PAT = '~/.cache/maelstrom'


def migrate_nvim_plugin_paths(
    root_dir: str = ROOT_DIR,
    rg_pat: str = RG_PAT,
    old_root_tilde: str = OLD_ROOT_TILDE,
    new_root_tilde: str = NEW_ROOT_TILDE,
):
    """
    - Finds files under `root_dir` containing data_path = "~/.cache/maelstrom/<tail>"
    - Copies each referenced directory from ~/.cache/maelstrom/<tail> to ~/data/nvim/plugins/<tail>
      using kx.cpdir
    - Rewrites the files so data_path points at the new root (preserving ~ in the file)

    Prints a short log of what it changed/copied.
    """
    files = list(kx.rg(root_dir, rg_pat))
    if not files:
        print("[INFO] No files matched the data_path pattern.")
        return

    # Track unique src->dst copies to avoid duplicate work
    copy_jobs = set()

    updated_files = 0
    total_rewrites = 0

    for file in files:
        path = file["path"]
        lnum = file["lnum"]
        text = kx.readfile(path)

        matches = list(DATA_PATH_RE.finditer(text))
        if not matches:
            # File matched rg_pat but didn't match the stricter parser; skip gracefully.
            continue

        # Plan copies for each match
        for m in matches:
            tail = m.group(2)  # the part after ~/.cache/maelstrom/
            src = os.path.join(OLD_ROOT_ABS, tail)
            dst = os.path.join(NEW_ROOT_ABS, tail)
            copy_jobs.add((src, dst))

        # Rewrite data_path lines to the new tilde-root (preserve original quote char)
        def _repl(m: re.Match) -> str:
            quote = m.group(1)
            tail = m.group(2)
            return f'data_path = {quote}{new_root_tilde}{tail}{quote}'

        new_text = DATA_PATH_RE.sub(_repl, text)
        if new_text != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)
            updated_files += 1
            total_rewrites += len(matches)
            print(f"[UPDATED] {file}  (+{len(matches)} rewrite{'s' if len(matches)!=1 else ''})")

    # Execute copy jobs
    for src, dst in sorted(copy_jobs):
        kx.cpfile(src, dst, verbose=True)

    print(f"[DONE] Files updated: {updated_files}, total data_path rewrites: {total_rewrites}, copy ops: {len(copy_jobs)}")


# If you want to run immediately:
# migrate_nvim_plugin_paths()


# if __name__ == "__main__":
#     cpdir('~/.cache/maelstrom/', '~/data/nvim/plugins/')

