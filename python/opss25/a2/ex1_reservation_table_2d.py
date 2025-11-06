from piglet.lib_piglet.domains.robotrunners import robotrunners_state

# ──────────────────────────────────────────────────────────────────────────────
#
# TASK 1: BUILD A RESERVATION TABLE
#
# Welp, you've seen that running A* blindly without any coordination wouldn't
# work out for more than one agent. Who would've guessed? Let's try some
# techniques to get around this problem.
#
# In this task, you will implement a planner that uses a reservation table to
# ensure that agents don't bump into each other. Try experimenting with
# different ways to use the reservation table and see how it affects the search.
#
# To get started, let's create a super simple reservation table.
#
# Look out for the 🏷️ EXERCISE label in the code below.
# The code sections marked with this label are where you need to implement your
# solution.
#
# ──────────────────────────────────────────────────────────────────────────────


class reservation_table_2d:
    """
    This is a super simple reservation table. It's a wrapper
    around a list of list of booleans.
    It only stores whether or not a tile is blocked,
    but not which agent is using it. It also doesn't know
    anything about time.
    This table doesn't even have an un-reserve method, but it'll
    serve its purpose for this assignment.
    """

    width: int
    height: int
    # True means blocked
    vertex_table: list[list[bool]]

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clear()

    def clear(self):
        self.vertex_table = [[False] * self.width for _ in range(self.height)]

    def reserve(self, *states: list[robotrunners_state]):
        # 🏷️ A2 EXERCISE: IMPLEMENT RESERVE
        # This function should mark the tiles
        # in states as reserved.
        pass

    def is_reserved(self, state: robotrunners_state):
        # 🏷️ A2 EXERCISE: IMPLEMENT IS_RESERVED
        # This function should return True if the tile
        # at state is reserved.
        pass
