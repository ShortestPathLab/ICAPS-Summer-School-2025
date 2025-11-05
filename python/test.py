import os

import piglet.lib_piglet.search.search_node as sn
from piglet.lib_piglet.cli.cli_tool import parse_problem
from opss25.a3.ex2_reservation_table_3d import (
    robotrunners_reservation_table,
)
from piglet.lib_piglet.domains import robotrunners
from piglet.lib_piglet.domains.robotrunners import Directions
from piglet.lib_piglet.logging.search_logger import bind, search_logger
from piglet.lib_piglet.output.trace_output import trace_output
from piglet.lib_piglet.search import (
    graph_search,
)
from piglet.lib_piglet.utils.data_structure import bin_heap

import python.opss25.a2.ex2_lorr_expander_w_reservations

MAP_PATH_ABSOLUTE = "example_problems/random/maps/random-32-32-20.map"
SCEN_PATH_ABSOLUTE = "example_problems/random/random-32-32-10.scen"

current_dir = os.path.dirname(os.path.abspath(__file__))

print("Looking for:", MAP_PATH_ABSOLUTE)
map_fo = open(MAP_PATH_ABSOLUTE, "r")

print("Looking for:", SCEN_PATH_ABSOLUTE)
scen_fo = open(SCEN_PATH_ABSOLUTE, "r")

scens = [line.split() for line in scen_fo.readlines()[1:]]  # Remove first line

print(map_fo.readlines())

logger = search_logger(logger=trace_output(file="test.trace.yaml"))

task = parse_problem(scens[0], 0)  # 0 for gridmap

# int orientation;  // 0:east, 1:south, 2:west, 3:north
default_res_table = robotrunners_reservation_table(32, 32)

dm = robotrunners.robotrunners(MAP_PATH_ABSOLUTE)

expander = (
    python.opss25.a2.ex2_lorr_expander_w_reservations.lorr_expander_w_reservations(
        dm, reservation_table=default_res_table
    )
)
heuristic_function = opss25.a1.ex2_heuristic.straight_heuristic
open_list = bin_heap(sn.compare_node_f)
engine = graph_search.graph_search
search_engine = engine(open_list, expander, heuristic_function=heuristic_function)

bind(search_engine, logger).head()

# solution = search_engine.get_path((1,2,Directions.NORTH,0),(2,1,Directions.NONE,-1))
solution = search_engine.get_path(
    (*task.start_state, Directions.EAST, 0), (*task.goal_state, Directions.NONE, -1)
)

print(solution)
