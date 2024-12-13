"""
Ohhh this reminds me so much of this interview problem
I got at Google when I was a senior in college.

It's a little different because there's almost
two targets and we were more constrained to seeing if a
set of numbers could perfectly hit a target and in how many ways.

There's definitely some easy things that we can do.

OK so this basically appears like a kind of Diophantine problem.
See more here:
https://en.wikipedia.org/wiki/Diophantine_equation#:~:text=In%20mathematics%2C%20a%20Diophantine%20equation,integer%20solutions%20are%20of%20interest.

So we can pretty easily reject solutions where no multiples
of each X can hit the target X and each Y can hit the target Y.

Ah and then ok to find the actual multiples we can use the Eucledian
algorithm to find the greatest common divisor of the target.

I actually wrote a small blog post about the Euclidean algorithm
here!https://johnlarkin1.github.io/2017/euclidean-algo/

So now we want to use the extended one:
https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm


"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np

BUTTON_PUSH_A_TOKEN_COST = 3
BUTTON_PUSH_B_TOKEN_COST = 1
MAX_SINGLE_BUTTON_PUSH = 100
PT2_OFFSET = 10000000000000


@dataclass
class ButtonRule:
    x_move: int
    y_move: int
    push_cost: int

    def __repr__(self):
        return f"Rule: X+{self.x_move}, Y+{self.y_move}, cost: {self.push_cost}"


@dataclass
class Prize:
    x_target: int
    y_target: int

    def __repr__(self):
        return f"Prize: X={self.x_target}, Y={self.y_target}"


@dataclass
class ClawMachineInfo:
    a_rule: ButtonRule
    b_rule: ButtonRule
    prize: Prize

    def __repr__(self):
        return f"{self.a_rule}\n{self.b_rule}\n{self.prize}"

    def unpack(self) -> Tuple[ButtonRule, ButtonRule, Prize]:
        return self.a_rule, self.b_rule, self.prize


def can_hit_target(val_a: int, val_b: int, target: int) -> bool:
    greatest_common_divisor = math.gcd(val_a, val_b)
    return target % greatest_common_divisor == 0


def is_in_button_press_range(num_button_a_presses: int, num_button_b_presses: int, with_max_check: bool = True) -> bool:
    if with_max_check:
        return (
            num_button_a_presses <= MAX_SINGLE_BUTTON_PUSH
            and num_button_a_presses >= 0
            and num_button_b_presses <= MAX_SINGLE_BUTTON_PUSH
            and num_button_b_presses >= 0
        )
    return num_button_a_presses >= 0 and num_button_b_presses >= 0


def find_possible_solutions(a_rule: ButtonRule, b_rule: ButtonRule, prize: Prize) -> list[Tuple[int, int]]:
    """
    I really want this to basically solve this system:
    for example, if we have:

    Button A: X+94, Y+34
    Button B: X+22, Y+67
    Prize: X=8400, Y=5400

    then we basically have this system of equations:
    94a + 22b = 8400
    34a + 67b = 5400

    and then we could solve that...

    Ok after a bit of looking around, we can do basically this:

    [94 22] [a] = [8400]
    [34 67] [b]   [5400]
    this is going to be A * x = B
    """

    try:
        A_matrix = np.array([[a_rule.x_move, b_rule.x_move], [a_rule.y_move, b_rule.y_move]], dtype=np.int64)
        B_target = np.array([prize.x_target, prize.y_target], dtype=np.int64)

        # let's see if there are infinite solutions more or less
        if np.linalg.det(A_matrix) == 0:
            solution, residuals, rank, singular_values = np.linalg.lstsq(A_matrix, B_target, rcond=None)
            print(
                f"Infinite solutions exist. Example solution:"
                f"{solution}, residuals: {residuals}, rank: {rank}, "
                f"singular values: {singular_values}"
            )
        solution = np.linalg.solve(A_matrix, B_target)
        rounded_solution = np.round(solution).astype(np.int64)

        # Validate the rounded solution satisfies the original equations
        validation_product = np.dot(A_matrix, rounded_solution).astype(np.int64)
        if np.array_equal(validation_product, B_target):
            return [tuple(rounded_solution)]
        else:
            return []

        # wow I got burned good on this for awhile
        # basically [91. 10.]
        # is not the same as [91, 10]
        # and was being returned as [91, 9]
        # def cleanup_float(f: float) -> int:
        # return int(round(f))

        # return [(cleanup_float(solution[0]), cleanup_float(solution[1]))]
    except np.linalg.LinAlgError as e:
        print("no solution found")
        raise AssertionError("No solution found") from e
    return []


def parse_input(input_file: Path) -> list[ClawMachineInfo]:
    def parse_button_rule(line: str, cost: int) -> ButtonRule:
        rule_info = line.split(":")[1].strip()
        x_info, y_info = rule_info.split(",")
        x_move, y_move = x_info.split("+")[1], y_info.split("+")[1]
        return ButtonRule(
            int(x_move),
            int(y_move),
            cost,
        )

    def parse_prize_rule(line: str) -> Prize:
        prize_info = line.split(":")[1].strip()
        x_target, y_target = prize_info.split(",")
        x_target, y_target = int(x_target.split("=")[1]), int(y_target.split("=")[1])
        return Prize(x_target, y_target)

    claw_machine_infos: list[ClawMachineInfo] = []
    with open(input_file) as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        for i in range(0, len(lines), 3):
            button_a_line = lines[i]
            button_b_line = lines[i + 1]
            prize_line = lines[i + 2]

            if "Button A" not in button_a_line or "Button B" not in button_b_line or "Prize" not in prize_line:
                raise AssertionError("Something went wrong with parsing input")

            a_rule = parse_button_rule(lines[i], BUTTON_PUSH_A_TOKEN_COST)
            b_rule = parse_button_rule(lines[i + 1], BUTTON_PUSH_B_TOKEN_COST)
            prize_rule = parse_prize_rule(lines[i + 2])
            claw_machine_infos.append(ClawMachineInfo(a_rule, b_rule, prize_rule))

    return claw_machine_infos


def soln(input_file: Path) -> tuple[int, int]:
    claw_machine_info_list = parse_input(input_file)
    total_token_cost_pt_1 = 0
    total_token_cost_pt_2 = 0
    for claw_machine_info in claw_machine_info_list:
        # Part 1
        a_rule, b_rule, prize = claw_machine_info.unpack()
        if not can_hit_target(a_rule.x_move, b_rule.x_move, prize.x_target):
            pass
        elif not can_hit_target(a_rule.y_move, b_rule.y_move, prize.y_target):
            pass
        else:
            possible_solutions = find_possible_solutions(a_rule, b_rule, prize)
            for solution in possible_solutions:
                num_button_a_presses, num_button_b_presses = solution
                if not is_in_button_press_range(num_button_a_presses, num_button_b_presses):
                    continue
                total_token_cost_pt_1 += (
                    num_button_a_presses * a_rule.push_cost + num_button_b_presses * b_rule.push_cost
                )

        # Part 2
        prize.x_target += PT2_OFFSET
        prize.y_target += PT2_OFFSET
        if not can_hit_target(a_rule.x_move, b_rule.x_move, prize.x_target):
            pass
        elif not can_hit_target(a_rule.y_move, b_rule.y_move, prize.y_target):
            pass
        else:
            possible_solutions = find_possible_solutions(a_rule, b_rule, prize)
            if not possible_solutions:
                continue

            for solution in possible_solutions:
                num_button_a_presses, num_button_b_presses = solution
                if not is_in_button_press_range(num_button_a_presses, num_button_b_presses, with_max_check=False):
                    continue
                total_token_cost_pt_2 += (
                    num_button_a_presses * a_rule.push_cost + num_button_b_presses * b_rule.push_cost
                )

    return (int(total_token_cost_pt_1), int(total_token_cost_pt_2))


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    # input_file = curr_dir.parent / "inputs" / "day13_very_small.txt"
    # input_file = curr_dir.parent / "inputs" / "day13_small_pt2.txt"
    # input_file = curr_dir.parent / "inputs" / "day13_small.txt"
    input_file = curr_dir.parent / "inputs" / "day13.txt"
    print(soln(input_file))
