import kevinlulee as kx


def dataform(src_path, fn):
    def validate(name):
        return name in ["python", "typst", "global", "typescript"]

    def func(path):
        return fn(kx.readfile(path))

    if kx.is_dir(src_path):
        return {
            kx.check(kx.get_filename(path), validate): func(path)
            for path in kx.get_paths(src_path)
        }
    else:
        return func(src_path)
