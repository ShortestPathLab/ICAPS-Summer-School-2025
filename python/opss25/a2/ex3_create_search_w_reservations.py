# ──────────────────────────────────────────────────────────────────────────────
#
# TASK 3: BUILD THE SEARCH ENGINE
#
# Write a search engine that pulls together the expander that we've just created
# along with the other components of the search engine.
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
from .ex1_reservation_table_2d import reservation_table_2d
from .ex2_lorr_expander_w_reservations import lorr_expander_w_reservations
from ..a1.ex2_lorr_heuristics import manhattan_heuristic


def create_search_w_reservations(
    domain: robotrunners, reservation_table: reservation_table_2d
):
    open_list = bin_heap(search_node.compare_node_f)

    # ℹ️ INFO We've done this for you
    expander = lorr_expander_w_reservations(domain, reservation_table)

    # 🏷️ A2 EXERCISE: (OPTIONAL) PLAY WITH HEURISTICS
    # Try changing the heuristic function below and see how it affects the search.
    # Import a heuristic function
    heuristic = manhattan_heuristic
    # region ANSWER A2:
    heuristic = manhattan_heuristic
    # endregion

    return graph_search(open_list, expander, heuristic_function=heuristic)
