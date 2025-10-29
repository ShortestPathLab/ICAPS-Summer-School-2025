import os,sys
from lib_piglet.domains import robotrunners
from lib_piglet.expanders.robotrunners_expander import robotrunners_expander
from lib_piglet.heuristics import gridmap_h
from lib_piglet.search import (
    tree_search,
    graph_search,
    base_search,
    search_node,
    iterative_deepening,
    graph_search_anytime,
)
import lib_piglet.search.search_node as sn
from lib_piglet.utils.data_structure import bin_heap
from lib_piglet.domains.robotrunners import Directions
from lib_piglet.heuristics import gridmap_h
from lib_piglet.constraints.robotrunners_constraints import robotrunners_reservation_table
current_dir = os.path.dirname(os.path.abspath(__file__))
mapfile = os.path.join(current_dir, "example", "gridmap", "random-32-32-20.map")

print("Looking for:", mapfile)
map_fo = open(mapfile, "r")
print(map_fo.readlines())



		# int orientation;  // 0:east, 1:south, 2:west, 3:north
default_res_table = robotrunners_reservation_table(32,32)

dm = robotrunners.robotrunners(mapfile)
expander = robotrunners_expander(dm,default_res_table)    
heuristic_function = gridmap_h.piglet_heuristic
open_list = bin_heap(sn.compare_node_f)
engine = graph_search.graph_search
search_engine = engine(open_list, expander, heuristic_function=heuristic_function)
# solution = search_engine.get_path((1,2,Directions.NORTH,0),(2,1,Directions.NONE,-1))
solution = search_engine.get_path((11,8,Directions.EAST,0),(10,9,Directions.NONE,-1))


# print solution
print(solution)