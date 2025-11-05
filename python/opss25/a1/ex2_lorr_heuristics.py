# ──────────────────────────────────────────────────────────────────────────────
#
# TASK 2: DEFINE HEURISTICS
#
# Heuristics are super important for the A* search algorithm.
#
# The heuristic functions return a number that estimates the distance between the
# current state and the goal state. The heuristic should be admissible, meaning
# that it should never overestimate the cost to get from the current state to the
# goal state.
#
# Look out for the 🏷️ EXERCISE label in the code below.
# The code sections marked with this label are where you need to implement your
# solution.
#
# ──────────────────────────────────────────────────────────────────────────────


from piglet.lib_piglet.domains.robotrunners import robotrunners, robotrunners_state, Directions
import math


def manhattan_heuristic(
    domain: robotrunners,
    current_state: robotrunners_state,
    goal_state: robotrunners_state,
):

    # 🏷️ A1 EXERCISE: DEFINE THE MANHATTAN HEURISTIC
    #
    # This is the distance between two points on a grid, measured by the number of
    # blocks that separate them.
    #
    # Write and return an expression that computes the manhattan distance.

    # region ANSWER A1:

    return abs(current_state[0] - goal_state[0]) + abs(current_state[1] - goal_state[1])

    # endregion


def octile_heuristic(
    domain: robotrunners,
    current_state: robotrunners_state,
    goal_state: robotrunners_state,
):

    # 🏷️ A1 EXERCISE: DEFINE THE OCTILE HEURISTIC
    #
    # This is the distance between two points on a grid, measured by the cost of
    # diagonal and straight steps that separate them.
    #
    # Write and return an expression that computes the octile distance.

    # region ANSWER A1:
    delta_x = abs(current_state[0] - goal_state[0])
    delta_y = abs(current_state[1] - goal_state[1])
    return round(
        min(delta_x, delta_y) * math.sqrt(2) + max(delta_x, delta_y) - min(delta_x, delta_y),
        5,
    )
    # endregion


def straight_heuristic(
    domain: robotrunners,
    current_state: robotrunners_state,
    goal_state: robotrunners_state,
):

    # 🏷️ A1 EXERCISE: DEFINE THE STRAIGHT HEURISTIC
    #
    # This is the distance between two points on a grid, measured using the
    # Pythagorean theorem.
    #
    # Write and return an expression that computes the straight distance.

    # region ANSWER A1:
    return round(
        (
            (current_state[0] - goal_state[0]) ** 2
            + (current_state[1] - goal_state[1]) ** 2
        )
        ** 0.5,
        5,
    )
    # endregion


def direction_aware_heuristic(
    domain: robotrunners,
    current_state: robotrunners_state,
    goal_state: robotrunners_state,
):
    # This is the distance between two points on a grid, measured by the number of
    # blocks that separate them, and an optimistic number of rotations.
    dx, dy = abs(current_state[0] - goal_state[0]), abs(current_state[1] - goal_state[1])
    is_bend: bool = (dx > 0 and dy > 0) # do we need to turn from x->y, or vice versa?
    init_turns: int = get_init_turns(current_state, goal_state)
    turns_required = is_bend + init_turns
    return dx + dy + turns_required


def get_init_turns(state1, state2):
    dx, dy = state2[0] - state1[0], state2[1] - state1[1]
    curr_dir = state1[2]
    
    # Determine candidate target directions
    possible_targets = []
    if dx > 0:
        possible_targets.append(Directions.EAST)
    elif dx < 0:
        possible_targets.append(Directions.WEST)
    if dy > 0:
        possible_targets.append(Directions.SOUTH)
    elif dy < 0:
        possible_targets.append(Directions.NORTH)

    if not possible_targets:
        return 0  # same cell

    # 🏷️ A1 EXERCISE: CALCULATE THE NUMBER OF INITIAL TURNS REQUIRED
    #                 TO FACE THE NEAREST HEURISTIC-RECOMMENDED DIRECTION.
    min_turns = float("inf")
    for target_dir in possible_targets:

    # region ANSWER A1:
        diff = abs(curr_dir - target_dir)
        turns = min(diff, 4 - diff)  # wrap-around (NORTH↔WEST)
        min_turns = min(min_turns, turns)
    return min_turns
    # endregion