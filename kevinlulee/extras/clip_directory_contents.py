import re
import kevinlulee as kx
from kevinlulee.extras.collect_files import collect_files


# ---------------------------
# Exclusion sources (intent)
# ---------------------------

EXCLUDE_EXTS = {
    # media / binary
    "png", "svg", "pdf", "jpg", "jpeg", "gif", "ico", "webp",
    "mp3", "mp4", "wav",
    "woff", "ttf", "eot", "otf",
}

EXCLUDE_NAMES = {
    # vcs / os
    ".gitignore",
    ".gitattributes",
    ".DS_Store",

    # env / tooling
    ".env",
    ".python-version",
    ".nvmrc",
    ".npmrc",
    ".dockerignore",
    ".editorconfig",

    # package managers
    "uv.lock",
    "poetry.lock",
    "Cargo.lock",
    "Gemfile.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",

    # frontend config
    "tsconfig.json",
    "tsconfig.node.json",
}

EXCLUDE_PATTERNS = [
    r"\.git/",
    r"postcss\.config\.",
    r"tailwind\.config\.",
    r"vite\.config\.",
    r"webpack\.config\.",
]


# ---------------------------
# Helpers → regex
# ---------------------------

def _exts_to_patterns(exts):
    return [rf"\.{re.escape(ext)}$" for ext in exts]


def _names_to_patterns(names):
    return [rf"{re.escape(name)}$" for name in names]


def build_exclude_patterns(*, exts=None, names=None, exclude=None):
    return (
        EXCLUDE_PATTERNS
        + _exts_to_patterns(EXCLUDE_EXTS | set(exts or []))
        + _names_to_patterns(EXCLUDE_NAMES | set(names or []))
        + (exclude or [])
    )


# ---------------------------
# Public API
# ---------------------------

def clip_directory_contents(
    paths,
    *,
    header=True,
    tree=True,
    date=False,
    min_chars=100,
    exts=None,
    names=None,
    exclude=None,
    **kwargs,
):
    files = collect_files(
        paths,
        exclude=build_exclude_patterns(
            exts=exts,
            names=names,
            exclude=exclude,
        ),
        **kwargs,
    )

    def render(file):
        text = kx.serialize_data(kx.readfile(file, raw=True))
        if len(text) < min_chars:
            return None

        if not header:
            return text

        label = (
            kx.join_text(file, kx.strftime(file, mode="detailed"))
            if date
            else file
        )
        return kx.comment(kx.parens(label, "-" * 60), file), text

    body = kx.mapfilter(files, render)
    tree_block = (
        kx.comment(kx.fancy_file_tree(files), files[0])
        if tree and files
        else None
    )

    return kx.join_text(tree_block, body)


# ---------------------------
# CLI
# ---------------------------

if __name__ == "__main__":
    kx.clip(
        clip_directory_contents(
            "~/.cache/typst/packages/preview/cetz/0.3.3/"
        )
    )

