"""
ok almost done
"""

from pathlib import Path
from typing import Literal, Tuple

from input_util import MatrixStr, matrix_to_string, parse_input_as_matrix

ARE_TESTING = False


class DiagramBase:
    diagram: MatrixStr

    def __init__(self, diagram: MatrixStr) -> None:
        self.diagram = diagram

    def __str__(self) -> str:
        return matrix_to_string(self.diagram)

    def __repr__(self) -> str:
        return matrix_to_string(self.diagram)

    @property
    def free_space(self) -> int:
        return self.num_rows - 2

    @property
    def num_rows(self) -> int:
        return len(self.diagram)

    @property
    def num_cols(self) -> int:
        return len(self.diagram[0])

    def _get_heights_base(self, top_down: bool) -> list[int]:
        heights = [0] * self.num_cols
        rows = self.diagram if top_down else list(reversed(self.diagram))
        for row_idx, row in enumerate(rows):
            if row_idx == 0:
                continue
            at_least_one_target = False
            for col, cell in enumerate(row):
                if cell == "#":
                    at_least_one_target = True
                    heights[col] += 1

            if not at_least_one_target:
                break

        return heights


class Lock(DiagramBase):
    def get_heights(self) -> list[int]:
        """Top-down number of # consecutively in each column."""
        return self._get_heights_base(top_down=True)


class Key(DiagramBase):
    def get_heights(self) -> list[int]:
        """Bottom-up number of # consecutively in each column."""
        return self._get_heights_base(top_down=False)


LockKeyReturn = Tuple[Literal[True], Lock] | Tuple[Literal[False], Key]


def parse_lock_or_key(lock_or_key_matrix: MatrixStr) -> LockKeyReturn:
    """Returns a bool and a Lock or Key object.
    if the bool is True, then the object is a Lock."""
    num_rows = len(lock_or_key_matrix)
    if all(cell == "#" for cell in lock_or_key_matrix[0]):
        return (True, Lock(lock_or_key_matrix))
    elif all(cell == "#" for cell in lock_or_key_matrix[num_rows - 1]):
        return (False, Key(lock_or_key_matrix))
    else:
        raise ValueError("Not a valid lock or key")


def parse_input(input_file: Path) -> Tuple[list[Lock], list[Key]]:
    input_text = input_file.read_text().strip()
    lock_and_key_schematics = input_text.split("\n\n")
    locks: list[Lock] = []
    keys: list[Key] = []
    for lock_or_key in lock_and_key_schematics:
        lock_or_key_matrix = parse_input_as_matrix(lock_or_key, "str")
        is_lock, lock_or_key_obj = parse_lock_or_key(lock_or_key_matrix)
        if is_lock:
            lock = lock_or_key_obj
            assert isinstance(lock, Lock)
            locks.append(lock)
        else:
            key = lock_or_key_obj
            assert isinstance(key, Key)
            keys.append(key)
    return locks, keys


def calculate_unique_lock_key_pairs(locks: list[Lock], keys: list[Key]) -> int:
    num_pairs = 0
    for lock in locks:
        for key in keys:
            lock_heights = lock.get_heights()
            key_heights = key.get_heights()
            sum_heights = [l + k for l, k in zip(lock_heights, key_heights)]
            if any(height > key.free_space for height in sum_heights):
                continue
            num_pairs += 1
    return num_pairs


def soln(input_file: Path) -> tuple[int, int]:
    pt1_soln = 0
    pt2_soln = 0
    locks, keys = parse_input(input_file)
    pt1_soln = calculate_unique_lock_key_pairs(locks, keys)
    return (pt1_soln, pt2_soln)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    if ARE_TESTING:
        input_file = curr_dir.parent / "inputs" / "day25_small.txt"
    else:
        input_file = curr_dir.parent / "inputs" / "day25.txt"
    print(soln(input_file))
