import os
import sys

import piglet.lib_piglet.search.search_node as sn
from piglet.lib_piglet.constraints.robotrunners_constraints import (
    robotrunners_reservation_table,
)
from piglet.lib_piglet.domains import robotrunners
from piglet.lib_piglet.domains.robotrunners import Directions
import opss25.a2.ex1_robotrunners_expander_with_wait
import opss25.a1.ex2_robotrunners_heuristic
from piglet.lib_piglet.heuristics import gridmap_h
from piglet.lib_piglet.search import (
    base_search,
    graph_search,
    graph_search_anytime,
    iterative_deepening,
    search_node,
    tree_search,
)
from piglet.lib_piglet.logging.search_logger import search_logger, bind
from piglet.lib_piglet.output.trace_output import trace_output

from piglet.lib_piglet.utils.data_structure import bin_heap

MAP_PATH_ABSOLUTE = "/home/spaaaacccee/projects/opss25-startkit/example_problems/random/maps/random-32-32-20.map"

current_dir = os.path.dirname(os.path.abspath(__file__))

print("Looking for:", MAP_PATH_ABSOLUTE)
map_fo = open(MAP_PATH_ABSOLUTE, "r")

print(map_fo.readlines())

logger = search_logger(logger=trace_output(file="test.trace.yaml"))

# int orientation;  // 0:east, 1:south, 2:west, 3:north
default_res_table = robotrunners_reservation_table(32, 32)

dm = robotrunners.robotrunners(MAP_PATH_ABSOLUTE)

expander = (
    opss25.a2.ex1_robotrunners_expander_with_wait.robotrunners_expander_with_wait(
        dm, reservation_table=default_res_table
    )
)
heuristic_function = opss25.a1.ex2_robotrunners_heuristic.straight_heuristic
open_list = bin_heap(sn.compare_node_f)
engine = graph_search.graph_search
search_engine = engine(open_list, expander, heuristic_function=heuristic_function)

bind(search_engine, logger).head()

# solution = search_engine.get_path((1,2,Directions.NORTH,0),(2,1,Directions.NONE,-1))
solution = search_engine.get_path(
    (0, 2, Directions.EAST, 0), (10, 7, Directions.NONE, -1)
)

# (20, 31, EAST, 0)
# (14, 24, NONE, -1)
# piglet_path = self.get_TXAstar_path(
#             671,
#             0,
#             0,
#             472
#         )
# print solution
print(solution)
