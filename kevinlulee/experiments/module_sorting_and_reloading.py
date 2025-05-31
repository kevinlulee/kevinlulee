import importlib
import sys
from modulefinder import ModuleFinder
# import networkx as nx

def build_dependency_graph(entry_script):
    finder = ModuleFinder()
    finder.run_script(entry_script)

    G = nx.DiGraph()

    for name, mod in finder.modules.items():
        if name not in sys.modules:
            continue
        for imported_name in mod.globalnames:
            if imported_name in finder.modules and imported_name in sys.modules:
                G.add_edge(imported_name, name)  # reverse: imported first

    return G

def reload_modules_in_order(G):
    try:
        order = list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        print("Circular imports detected. Partial reload might occur.")
        order = list(G.nodes)

    for name in order:
        if name in sys.modules:
            print(f"Reloading: {name}")
            importlib.reload(sys.modules[name])

def auto_reload(entry_script):
    G = build_dependency_graph(entry_script)
    reload_modules_in_order(G)


# auto_reload('/home/kdog3682/projects/python/kevinlulee/kevinlulee/experiments/module_sorting_and_reloading.py')

#--1  
