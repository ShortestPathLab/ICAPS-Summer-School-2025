# ──────────────────────────────────────────────────────────────────────────────
#
# TASK 3: BUILD THE SEARCH ENGINE
#
# This is where it all comes together. In this task, you will implement the search
# engine for the robot runners domain, using the expander you implemented in the
# previous task. Try out a few of the heuristics and see how performance differs.
#
# Look out for the 🏷️ EXERCISE label in the code below.
# The code sections marked with this label are where you need to implement your solution.
#
# ──────────────────────────────────────────────────────────────────────────────

from piglet.lib_piglet.domains.gridmap import gridmap
from piglet.lib_piglet.search.graph_search import graph_search
from piglet.lib_piglet.utils.data_structure import bin_heap
from piglet.lib_piglet.search import search_node
from .ex1_robotrunners_expander import robotrunners_expander
from .ex2_robotrunners_heuristic import straight_heuristic


def create_search(domain: gridmap):
    open_list = bin_heap(search_node.compare_node_f)

    # 🏷️ A1 EXERCISE: DEFINE THE EXPANDER
    # Import and initialize the expander
    expander = None
    # region ANSWER A1:
    expander = robotrunners_expander(domain)
    # endregion

    # 🏷️ A1 EXERCISE: DEFINE THE HEURISTIC
    # Import a heuristic function
    heuristic = None
    # region ANSWER A1:
    heuristic = straight_heuristic
    # endregion

    return graph_search(open_list, expander, heuristic_function=heuristic)
