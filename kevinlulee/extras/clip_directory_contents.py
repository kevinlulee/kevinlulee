import kevinlulee as kx


def clip_directory_contents(
    dir, with_header=True, with_file_tree=True, with_date = False, **kwargs
):
    """
    finds all files in a directory via fd
    reads them and joins them together

    option: with_header: true
    option: with_file_tree: true
    """

    files = kx.fd(dir, ignore_file=None, **kwargs) if kx.is_string(dir) else dir
    ignored_files = [
        "index.html",
        "package.json",
        "pnpm-lock.yaml",
        "tsconfig.json",
        "vite.config.ts",
            ".prettierrc",
    "postcss.config.js",
    "tailwind.config.ts",
    "tsconfig.node.json",
    ]
    cfiles = kx.filtered(files, lambda x: kx.os.path.basename(x) not in ignored_files)

    def runner(file):
        text = kx.serialize_data(kx.readfile(file, raw=True))
        if len(text) < 100:
            return

        if with_header == False:
            return text

        inner = kx.join_text(file, kx.strftime(file, mode="detailed")) if with_date else file
        h = kx.parens(inner, "-" * 60)
        header = kx.comment(h, file)
        return header, text

    a = kx.mapfilter(cfiles, runner)
    b = (
        kx.comment(kx.fancy_file_tree(files), files[0])
        if with_file_tree
        else None
    )
    return kx.join_text(b, a)


if __name__ == "__main__":
    kx.clip(clip_directory_contents('~/.cache/typst/packages/preview/cetz/0.3.3/'))
