import nvim
import kevinlulee as kx


def example():
    import kevinlulee as kx
    import nvim

    files = kx.get_most_recent_file_groups(kx.DLDIR, pattern="zip$", minutes=60)
    font_dir = "~/.local/share/fonts"
    for file in files:
        path = kx.fnamemodify(file, name=kx.snake_case, dir=font_dir, ext="")
        p = kx.extract_zip(file, path)

    nvim.fs.clip(kx.fancy_file_tree(font_dir))
