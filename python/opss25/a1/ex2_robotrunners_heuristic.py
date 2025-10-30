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
# The code sections marked with this label are where you need to implement your solution.
#
# ──────────────────────────────────────────────────────────────────────────────


def manhattan_heuristic(current_state, goal_state):

    # 🏷️ EXERCISE: DEFINE THE MANHATTAN HEURISTIC
    #
    # This is the distance between two points on a grid, measured by the number of
    # blocks that separate them.
    #
    # Write and return an expression that computes the manhattan distance.

    # region ANSWER A1:

    return abs(current_state[0] - goal_state[0]) + abs(current_state[1] - goal_state[1])

    # endregion


def straight_heuristic(current_state, goal_state):

    # 🏷️ EXERCISE: DEFINE THE STRAIGHT HEURISTIC
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
