from pprint import pprint
from kevinlulee import fdfind, clip

# python3('/home/kdog3682/projects/python/kevinlulee/kevinlulee/__main__.py', as_module=True)
# this would be recursive
temp = [
        "/home/kdog3682/2023/.git/",
        "/home/kdog3682/2023/~/GITHUB/typst-fletcher/.git/",
        "/home/kdog3682/2024/.git/",
        "/home/kdog3682/2024/prosemirror-math/.git/",
        "/home/kdog3682/2024-javascript/.git/",
        "/home/kdog3682/2024-javascript/csx/.git/",
        "/home/kdog3682/2024-javascript/datetime/.git/",
        "/home/kdog3682/2024-javascript/evalenv/.git/",
        "/home/kdog3682/2024-javascript/js-toolkit/.git/",
        "/home/kdog3682/2024-javascript/my-daily-tracker-website/.git/",
        "/home/kdog3682/2024-javascript/nodekit/.git/",
        "/home/kdog3682/2024-javascript/shapelang/.git/",
        "/home/kdog3682/2024-javascript/staging/.git/",
        "/home/kdog3682/2024-javascript/stdlib/.git/",
        "/home/kdog3682/2024-javascript/tml/.git/",
        "/home/kdog3682/2024-javascript/ttt/.git/",
        "/home/kdog3682/2024-javascript/txflow/.git/",
        "/home/kdog3682/2024-javascript/vuekit/.git/",
        "/home/kdog3682/@bkl/.git/",
        "/home/kdog3682/PYTHON/.git/",
        "/home/kdog3682/archive/2024-python/.git/",
        "/home/kdog3682/archive/2024-typst/.git/",
        "/home/kdog3682/archive/RESOURCES/.git/",
        "/home/kdog3682/kevinlulee/pytypst/.git/",
        "/home/kdog3682/kevinlulee/usefulscripts/.git/",
        "/home/kdog3682/projects/old_projects/MyWebsites/lezer-ast-explorer/.git/",
        "/home/kdog3682/projects/old_projects/MyWebsites/local-file-server/.git/",
        "/home/kdog3682/projects/old_projects/MyWebsites/luli/.git/",
        "/home/kdog3682/projects/old_projects/MyWebsites/react-codemirror-component/.git/",
        "/home/kdog3682/projects/old_projects/MyWebsites/tsx-react-stylex-quickstart/.git/",
        "/home/kdog3682/projects/old_projects/VSCodeExtensions/qwe-jump/.git/",
        "/home/kdog3682/projects/old_projects/appscript/.git/",
        "/home/kdog3682/projects/old_projects/crispy-umbrella/.git/",
        "/home/kdog3682/projects/old_projects/foxscribe/.git/",
        "/home/kdog3682/projects/old_projects/gdpm/.git/",
        "/home/kdog3682/projects/old_projects/greenleaf/.git/",
        "/home/kdog3682/projects/old_projects/hammymath/.git/",
        "/home/kdog3682/projects/old_projects/luli/.git/",
        "/home/kdog3682/projects/old_projects/mmgg/.git/",
        "/home/kdog3682/projects/old_projects/my-vitesse-app/.git/",
        "/home/kdog3682/projects/old_projects/pearbook/.git/",
        "/home/kdog3682/projects/python/kevinlulee/.git/",
        "/home/kdog3682/projects/python/maelstrom/.git/",
        "/home/kdog3682/projects/python/maelstrom2/.git/",
        "/home/kdog3682/projects/python/pytypst/.git/",
        "/home/kdog3682/projects/typst/csg5/.git/",
        "/home/kdog3682/projects/typst/mathbook/.git/",
        "/home/kdog3682/projects/typst/mathematical/.git/",
        "/home/kdog3682/projects/typst/typkit/.git/",
        "/home/kdog3682/documents/.git/",
        "/home/kdog3682/dotfiles/.git/",
]
forms = [

        "/home/kdog3682/projects/python/kevinlulee/.git/",
        "/home/kdog3682/projects/python/maelstrom/.git/",
        "/home/kdog3682/projects/python/maelstrom2/.git/",
        "/home/kdog3682/projects/python/pytypst/.git/",
        "/home/kdog3682/projects/typst/csg5/.git/",
        "/home/kdog3682/projects/typst/mathbook/.git/",
        "/home/kdog3682/projects/typst/mathematical/.git/",
        "/home/kdog3682/projects/typst/typkit/.git/",
        "/home/kdog3682/documents/.git/",
        "/home/kdog3682/dotfiles/.git/",
]

from kevinlulee.git import GitRepo

for form in forms:
    repo = GitRepo(form.replace('.git/', ''))
    repo.add('.')
    repo.commit('safetypush')
    try:
        repo.cmd('push')
        print('success!', form)
    except Exception as e:
        print(e, 'error', form)

