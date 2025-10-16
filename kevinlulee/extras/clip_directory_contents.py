import kevinlulee as kx

def clip_directory_contents(dir, with_header = True, with_file_tree = True, **kwargs):
    """
    finds all files in a directory via fd
    reads them and joins them together

    option: with_header: true
    option: with_file_tree: true
    """

    files = kx.fd(dir, ignore_file='~/.ignore', **kwargs)

    def runner(file):
        text = kx.serialize_data(kx.readfile(file, raw = True))
        if len(text) < 100:
            return 

        if with_header == False:
            return text

        inner = kx.join_text(file, kx.strftime(file, mode = 'detailed'))
        h = kx.parens(inner, '-' * 60)
        header = kx.comment(h, file)
        return header, text

    a = kx.mapfilter(files, runner)
    b = kx.comment(kx.fancy_file_tree(files), files[0]) if with_file_tree else None
    return kx.join_text(b, a)
