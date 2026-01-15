import libcst as cst
from pathlib import Path

IMPORT_REWRITES = {
    "mx.command_result": "mx.command_handler",
    "mx.project_manager": "mx.project",
}


class ImportRewriter(cst.CSTTransformer):
    def __init__(self):
        self.changes_made = False

    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> cst.ImportFrom:
        if not isinstance(updated_node.module, cst.Attribute | cst.Name):
            return updated_node

        module_name = self._get_module_name(updated_node.module)

        if module_name in IMPORT_REWRITES:
            self.changes_made = True
            return updated_node.with_changes(
                module=self._build_module(IMPORT_REWRITES[module_name])
            )

        return updated_node

    def _get_module_name(self, node: cst.Attribute | cst.Name) -> str:
        if isinstance(node, cst.Name):
            return node.value
        parts = []
        while isinstance(node, cst.Attribute):
            parts.append(node.attr.value)
            node = node.value
        if isinstance(node, cst.Name):
            parts.append(node.value)
        return ".".join(reversed(parts))

    def _build_module(self, module_path: str) -> cst.Attribute | cst.Name:
        parts = module_path.split(".")
        result = cst.Name(parts[0])
        for part in parts[1:]:
            result = cst.Attribute(value=result, attr=cst.Name(part))
        return result


def rewrite_file(filepath: Path) -> bool:
    source = filepath.read_text()
    
    if not any(old in source for old in IMPORT_REWRITES):
        return False
    
    tree = cst.parse_module(source)
    transformer = ImportRewriter()
    new_tree = tree.visit(transformer)

    if transformer.changes_made:
        code = new_tree.code
        print('____')
        print(str(filepath))
        print(code)
        print('____')
        print()
        print()
        filepath.write_text(code)
        return True
    return False


def run_codemod(files: list[str | Path]) -> dict[str, bool]:
    results = {}
    for f in files:
        path = Path(f)
        if path.exists() and path.suffix == ".py":
            results[str(path)] = rewrite_file(path)
    return results


import tempfile
from pathlib import Path


def gen_test_files() -> list[Path]:
    tmpdir = Path(tempfile.mkdtemp())

    (tmpdir / "commands.py").write_text("""\
from mx.command_result import CommandResult

def run():
    return CommandResult(success=True)
""")

    (tmpdir / "projects.py").write_text("""\
from mx.project_manager import Project, load_project

p = load_project("test")
""")

    return [tmpdir / "commands.py", tmpdir / "projects.py"]

if __name__ == "__main__":
    results = run_codemod(gen_test_files())
    print(results)
