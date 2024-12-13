from typing import Tuple

import numpy as np


def find_solution(
    a_rule_x_move: int,
    a_rule_y_move: int,
    b_rule_x_move: int,
    b_rule_y_move: int,
    prize_x_target: int,
    prize_y_target: int,
) -> Tuple[int, int]:
    A_matrix = np.array([[a_rule_x_move, b_rule_x_move], [a_rule_y_move, b_rule_y_move]], dtype=float)
    B_target = np.array([prize_x_target, prize_y_target], dtype=float)
    solution = np.linalg.solve(A_matrix, B_target)
    print("solution", solution)

    def cleanup_float(f: float) -> int:
        return int(round(f))

    return (cleanup_float(solution[0]), cleanup_float(solution[1]))


if __name__ == "__main__":
    print(find_solution(91, 21, 53, 85, 8811, 2761))

    x_validation = 91 * 91
    assert 91 * 91 + 10 * 53 == 8811
    assert 21 * 91 + 10 * 85 == 2761
