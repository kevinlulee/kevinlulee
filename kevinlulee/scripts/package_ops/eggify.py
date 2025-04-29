def eggify(dir, name = None):

    """
    eggifies a directory
    # eggify('~/projects/python/manim')
    """

    cwd = find_git_directory(dir)
    assert cwd, "a git directory is required"
    name = name or os.path.basename(cwd)
    display(name = name, cwd = cwd)
    file = "/home/kdog3682/dotfiles/templates/setup.py"
    setup_dot_py = templater(readfile(file), {'name': name})
    writefile(os.path.join(cwd, 'setup.py'), setup_dot_py)
    bash('pip', 'install', '-e', cwd, '--break-system-packages')

    try:
        exec(f"""import {name}""")
        print('installation successful!')
    except Exception as e:
        print(e)
