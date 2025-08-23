import nvim
import kevinlulee as kx
from treebloom.utils.node_ops import get_syntax_tree, node_to_dict, node_to_txflow

SRC_PATH = "~/data/treebloom/corpus/sample.py"

def process_language(lang: str):
    root = kx.os.path.expanduser("~/data/treebloom/corpus/")
    ext = kx.get_extension_from_filetype(lang)
    outdir = kx.os.path.expanduser(f"~/data/treebloom/corpus/{lang}")
    SRC_PATH = kx.os.path.join(root, kx.add_extension_if_not_present('sample', ext))
    content = kx.readfile(SRC_PATH)
    assert content
    tree = get_syntax_tree(content, lang)
    tx = node_to_txflow(tree.root_node)
    ast = node_to_dict(tree.root_node)

    # Write outputs
    kx.writefile(f"{outdir}/repr.txt", tx)
    kx.writefile(f"{outdir}/ast.json", ast)
    kx.mvfile(SRC_PATH, outdir)

if __name__ == "__main__":
    # process_language('python') # done the file doesnt exist anymore ...
    process_language('typst')
