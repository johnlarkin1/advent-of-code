Matrix = list[list[str]]
Coordinate = tuple[int, int]


def parse_input_as_matrix(input_str: str) -> Matrix:
    return [list(line) for line in input_str.split("\n") if line]


def matrix_to_string(matrix: Matrix) -> str:
    return "\n".join("".join(row) for row in matrix)
