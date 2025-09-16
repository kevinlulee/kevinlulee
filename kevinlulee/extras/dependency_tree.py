class DependencyTree:
    def __init__(self, library: dict, getter: callable):
        self.library = library
        self.getter = getter

    def recursively_get_dependencies(self, target: str) -> dict:
        seen = set()

        def runner(key):
            seen.add(key)

            raw = self.getter(key)

            # Filter dependencies directly in this method
            dependencies = (
                [] if not raw else [item for item in raw if item not in seen]
            )

            children = [runner(dep) for dep in dependencies]
            payload = {"name": key}

            if children:
                payload["children"] = children

            return payload

        return runner(target)

    @staticmethod
    def flatten(tree: dict) -> list:
        def runner(node):
            name = node.get("name")
            children = node.get("children", [])

            # Directly flatten the nested results here
            result = [name]
            for child in children:
                result.extend(runner(child))
            return result

        return runner(tree)
