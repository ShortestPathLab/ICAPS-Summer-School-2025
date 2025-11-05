# ──────────────────────────────────────────────────────────────────────────────
#
# TASK 3: BUILD THE SEARCH ENGINE
#
# This is where it all comes together. In this task, you will implement the
# search engine for the robot runners domain, using the expander you implemented
# in the previous task. Try out a few of the heuristics and see how performance
# differs.
#
# Look out for the 🏷️ EXERCISE label in the code below.
# The code sections marked with this label are where you need to implement your
# solution.
#
# ──────────────────────────────────────────────────────────────────────────────

from piglet.lib_piglet.search.graph_search import graph_search
from piglet.lib_piglet.utils.data_structure import bin_heap
from piglet.lib_piglet.search import search_node
from piglet.lib_piglet.domains.robotrunners import robotrunners
from .ex1_lorr_expander import lorr_expander
from .ex2_lorr_heuristics import straight_heuristic, manhattan_heuristic, octile_heuristic, direction_aware_heuristic


def create_search(domain: robotrunners):
    open_list = bin_heap(search_node.compare_node_f)

    # 🏷️ A1 EXERCISE: DEFINE THE EXPANDER
    # Import and initialize the expander
    expander = None
    # region ANSWER A1:
    expander = lorr_expander(domain)
    # endregion

    # 🏷️ A1 EXERCISE: DEFINE THE HEURISTIC
    # Import a heuristic function
    heuristic = None
    # region ANSWER A1:
    heuristic = manhattan_heuristic
    # endregion

    return graph_search(open_list, expander, heuristic_function=heuristic)
