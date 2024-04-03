from collections import deque
from typing import Iterable, List

State = Iterable[Iterable[int]]
SymmetryGroup = List[State]
GroupId = int


class Node(object):
    def __init__(self, val: GroupId = None, successors: List[GroupId] = None):
        self.val = val
        self.successors = successors or []


def state_str(st: State) -> str:
    def row_to_str(row: Iterable[int]):
        row = [str(num) for num in row]
        return "".join(row)

    return "\n".join(row_to_str(row) for row in st)


def print_state(st: State) -> None:
    print(state_str(st))


def print_states(states: Iterable[State]):
    for st in states:
        print_state(st)
        print()


def get_symmetries(st: State) -> SymmetryGroup:
    def get_vertical_mirror(st: State) -> State:
        return tuple(reversed(st))

    def get_rotations(st: State) -> List[State]:
        ((a, b, c), (d, e, f), (g, h, i)) = st
        rot1 = ((g, d, a), (h, e, b), (i, f, c))
        rot2 = ((i, h, g), (f, e, d), (c, b, a))
        rot3 = ((c, f, i), (b, e, h), (a, d, g))
        return [st, rot1, rot2, rot3]

    def apply_all_symmetry_operations(st: State) -> List[State]:
        mir = get_vertical_mirror(st)
        return get_rotations(st) + get_rotations(mir)

    all_symmetries = apply_all_symmetry_operations(st)
    duplicates_removed = list(dict.fromkeys(all_symmetries))
    return duplicates_removed


def is_end(st: State) -> bool:
    def are_same(triplet):
        a, b, c = triplet
        return a == b == c != 0

    horizontals = [[st[ix][0], st[ix][1], st[ix][2]] for ix in range(3)]
    verticals = [[st[0][ix], st[1][ix], st[2][ix]] for ix in range(3)]
    diag1 = [st[0][0], st[1][1], st[2][2]]
    diag2 = [st[2][0], st[1][1], st[0][2]]
    lines = horizontals + verticals + [diag1, diag2]

    return any(are_same(line) for line in lines)

def make_move(st: State, row: int, col: int, val: int) -> State:
    if isinstance(st, int):
        # Convert single move representation to a 3x3 board
        st = [[0] * 3 for _ in range(3)]
        st[row][col] = val
    else:
        # Mutate the current board state
        mutable_st = [list(r) for r in st]
        mutable_st[row][col] = val
        st = tuple(tuple(r) for r in mutable_st)
    return st

def get_next_states_raw(st: State, step: int) -> List[State]:
    next_states = []
    if is_end(st):
        return []
    new_val = step % 2 + 1
    for row in range(3):
        for col in range(3):
            val = st[row][col]
            if val == 0:
                new_st = make_move(st, row, col, new_val)
                next_states.append(new_st)
    return next_states


def add_symmetry_group(st: State, gid: GroupId, states, groups) -> None:
    print(f"Adding symmetry group with ID {gid}")
    print(f"Current groups: {groups}")
    assert gid not in groups
    symmetry_group = get_symmetries(st)
    groups[gid] = symmetry_group
    states.update({st: gid for st in symmetry_group})
    print(f"Updated groups: {groups}")
