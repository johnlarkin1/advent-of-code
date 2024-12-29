"""
Ok should be a fun one with the monkey madness.

---

ok so for part 2, we're going to keep track of every sequence across every
monkey generation.

and then we're going to store how many bananas they would get with that sequence
and then w'ell just sort and find the max one.
"""

from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Generator, NamedTuple

ARE_TESTING = False
PRUNE_NUMBER = 16777216
SIMS_TO_RUN = 2000


class Sequence(NamedTuple):
    delta1: int
    delta2: int
    delta3: int
    delta4: int

    def update_with_new_delta(self, new_delta: int) -> "Sequence":
        return Sequence(self.delta2, self.delta3, self.delta4, new_delta)


def mix(secret_number: int, value: int) -> int:
    """
    To mix a value into the secret number, calculate the bitwise XOR
    of the given value and the secret number. Then, the secret number
    becomes the result of that operation.

    (If the secret number is 42 and you were to mix 15 into the secret number,
    the secret number would become 37.)
    """  # noqa: E501
    return secret_number ^ value


def prune(secret_number: int) -> int:
    """
    To prune the secret number, calculate the value of the secret number
    modulo 16777216. Then, the secret number becomes the result of that
    operation. (If the secret number is 100000000 and you were to prune
    the secret number, the secret number would become 16113920.)
    """  # noqa: E501
    return secret_number % PRUNE_NUMBER


@lru_cache(maxsize=None)
def evolve_secret_number(secret_number: int) -> int:
    """
    - Calculate the result of multiplying the secret number by 64.
    - Then, mix this result into the secret number.
    - Finally, prune the secret number.

    - Calculate the result of dividing the secret number by 32.
    - Round the result down to the nearest integer.
    - Then, mix this result into the secret number.
    - Finally, prune the secret number.

    - Calculate the result of multiplying the secret number by 2048.
    - Then, mix this result into the secret number.
    - Finally, prune the secret number.
    """

    # step1
    # secret_number = prune(mix(secret_number, secret_number * 64))
    # secret_number = prune(mix(secret_number, secret_number << 6))
    secret_number = (secret_number ^ (secret_number << 6)) % PRUNE_NUMBER

    # step2
    # secret_number = prune(mix(secret_number, secret_number // 32))
    # secret_number = prune(mix(secret_number, secret_number >> 5))
    secret_number = (secret_number ^ (secret_number >> 5)) % PRUNE_NUMBER

    # step3
    # secret_number = prune(mix(secret_number, secret_number * 2048))
    # secret_number = prune(mix(secret_number, secret_number << 11))
    secret_number = (secret_number ^ (secret_number << 11)) % PRUNE_NUMBER

    # result
    return secret_number


def evolve_secret_number_n_times(secret_number: int, n: int, optimization_dict: dict[Sequence, int]) -> int:
    prev_banana_count: int = secret_number % 10
    banana_deltas: list[int] = []
    prev_banana_count = secret_number % 10
    seen_sequences: set[Sequence] = set()

    for idx in range(n):
        secret_number = evolve_secret_number(secret_number)
        banana_count = secret_number % 10
        banana_deltas.append(banana_count - prev_banana_count)
        prev_banana_count = banana_count

        if idx >= 3:
            running_sequence = Sequence(
                delta1=banana_deltas[-4],
                delta2=banana_deltas[-3],
                delta3=banana_deltas[-2],
                delta4=banana_deltas[-1],
            )
            if running_sequence not in seen_sequences:
                optimization_dict[running_sequence] += banana_count
                seen_sequences.add(running_sequence)
    return secret_number


def generate_banana_deltas(secret_number: int, n: int) -> Generator[int, None, None]:
    prev_banana_count = secret_number % 10
    for _ in range(n):
        secret_number = evolve_secret_number(secret_number)
        banana_count = secret_number % 10
        yield banana_count - prev_banana_count
        prev_banana_count = banana_count


def evolve_secret_number_n_times_opt(secret_number: int, n: int, optimization_dict: dict[Sequence, int]) -> int:
    prev_banana_count = secret_number % 10
    recent_deltas = []
    local_counts = Counter()

    for delta in generate_banana_deltas(secret_number, n):
        recent_deltas.append(delta)
        if len(recent_deltas) > 4:
            recent_deltas.pop(0)

        if len(recent_deltas) == 4:
            running_sequence = Sequence(*recent_deltas)
            local_counts[running_sequence] += prev_banana_count

    optimization_dict.update(local_counts)
    return secret_number


def soln(input_file: Path) -> tuple[int, int]:
    pt1_ans = 0
    pt2_ans = 0
    banana_optimization_dict: dict[Sequence, int] = defaultdict(int)

    with open(input_file) as f:
        for line in f:
            secret_number = int(line.strip())
            pt1_ans_partial = evolve_secret_number_n_times_opt(secret_number, SIMS_TO_RUN, banana_optimization_dict)
            pt1_ans += pt1_ans_partial

    # Now we do part 2 where we analyze our optimization dict and which sequence results in
    # the max
    max_sequence, max_bananas_acquired = max(banana_optimization_dict.items(), key=lambda item: item[1])
    pt2_ans = max_bananas_acquired
    print(f"The best banana sequence is {max_sequence} with {max_bananas_acquired} bananas acquired")
    return (pt1_ans, pt2_ans)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    if ARE_TESTING:
        input_file = curr_dir.parent / "inputs" / "day22_small.txt"
    else:
        input_file = curr_dir.parent / "inputs" / "day22.txt"
    print(soln(input_file))
