"""
Ok we're getting into the hard part with part 2.

This is called a quine:
https://en.wikipedia.org/wiki/Quine_(computing)

So the idea is that we want a program that's going to return the same thing.

It's actually a super fascinating wikipedia article.

I actualyl wasn't sure outside of brute forcing the best way around this, but the general online consensus seems to be z3.

* https://github.com/Z3Prover/z3
*https://github.com/Z3Prover/z3/wiki#background

Part 2 requires us to basically brute force it, but we're going to solve it ideally using a Z3 solver, which I'm
excited to learn more about.... but let's start with the brute force.

....

Nope that is going to take too long! So let's use some of this
https://ericpony.github.io/z3py-tutorial/guide-examples.htm
specifically the BitVec portion.


Ok yet another approach. we can basically distill this problem out into these steps:


"""

from pathlib import Path
from typing import Callable, Literal

from z3 import BitVec, Optimize, sat

RegisterKeyType = Literal["A", "B", "C"]
RegisterType = dict[RegisterKeyType, int]


def literal_operand(operand: int) -> int:
    return operand


def combo_operand(operand: int, register_map: RegisterType) -> int:
    """
    Combo operands 0 through 3 represent literal values 0 through 3.
    Combo operand 4 represents the value of register A.
    Combo operand 5 represents the value of register B.
    Combo operand 6 represents the value of register C.
    Combo operand 7 is reserved and will not appear in valid programs.
    """
    if operand == 4:
        return register_map["A"]
    elif operand == 5:
        return register_map["B"]
    elif operand == 6:
        return register_map["C"]
    elif operand == 7:
        raise ValueError("Invalid operand")
    return operand


def adv(operand: int, register_map: RegisterType, instruction_pointer: int, output: list[int]) -> tuple[list[int], int]:
    numerator = register_map["A"]
    denominator = combo_operand(operand, register_map)
    register_map["A"] = numerator // 2**denominator
    instruction_pointer += 2
    return output, instruction_pointer


def bxl(operand: int, register_map: RegisterType, instruction_pointer: int, output: list[int]) -> tuple[list[int], int]:
    """
    Calculates the bitwise XOR of register B and
    the instruction's literal operand, then stores
    the result in register B.
    """
    register_map["B"] ^= literal_operand(operand)
    instruction_pointer += 2
    return output, instruction_pointer


def bst(operand: int, register_map: RegisterType, instruction_pointer: int, output: list[int]) -> tuple[list[int], int]:
    """combo operand mod 8"""
    register_map["B"] = combo_operand(operand, register_map) % 8
    instruction_pointer += 2
    return output, instruction_pointer


def jnz(operand: int, register_map: RegisterType, instruction_pointer: int, output: list[int]) -> tuple[list[int], int]:
    a_register_val = register_map["A"]
    if a_register_val != 0:
        instruction_pointer = literal_operand(operand)
    else:
        instruction_pointer += 2
    return output, instruction_pointer


def bxc(operand: int, register_map: RegisterType, instruction_pointer: int, output: list[int]) -> tuple[list[int], int]:
    """
    calculates the bitwise XOR of register B and register C, then stores the result in register B
    """
    register_map["B"] ^= register_map["C"]
    instruction_pointer += 2
    return output, instruction_pointer


def out(operand: int, register_map: RegisterType, instruction_pointer: int, output: list[int]) -> tuple[list[int], int]:
    """calculates the value of its combo operand modulo 8, then outputs that value"""
    output.append(combo_operand(operand, register_map) % 8)

    instruction_pointer += 2
    return output, instruction_pointer


def bdv(operand: int, register_map: RegisterType, instruction_pointer: int, output: list[int]) -> tuple[list[int], int]:
    numerator = register_map["A"]
    denominator = combo_operand(operand, register_map)
    register_map["B"] = numerator // 2**denominator

    instruction_pointer += 2
    return output, instruction_pointer


def cdv(operand: int, register_map: RegisterType, instruction_pointer: int, output: list[int]) -> tuple[list[int], int]:
    numerator = register_map["A"]
    denominator = combo_operand(operand, register_map)
    register_map["C"] = numerator // 2**denominator

    instruction_pointer += 2
    return output, instruction_pointer


def get_operand_func(opcode: int) -> Callable[[int, RegisterType, int, list[int]], tuple[list[int], int]]:
    mapping = {
        0: adv,
        1: bxl,
        2: bst,
        3: jnz,
        4: bxc,
        5: out,
        6: bdv,
        7: cdv,
    }

    return mapping[opcode]


def parse_input(input_file: Path) -> tuple[RegisterType, list[int]]:
    register_map: RegisterType = {"A": 0, "B": 0, "C": 0}
    program_instructions: list[int] = []
    for line in input_file.read_text().splitlines():
        if "Register A" in line:
            register_map["A"] = int(line.split(":")[-1])
        elif "Register B" in line:
            register_map["B"] = int(line.split(":")[-1])
        elif "Register C" in line:
            register_map["C"] = int(line.split(":")[-1])

        if "Program" in line:
            program_instructions = list(map(int, line.split(":")[-1].split(",")))
    return register_map, program_instructions


def process_instructions(register_map: RegisterType, program_instructions: list[int]) -> list[int]:
    instruction_pointer = 0
    output = []
    while instruction_pointer < len(program_instructions) - 1:
        opcode = program_instructions[instruction_pointer]
        operand = program_instructions[instruction_pointer + 1]

        # two types of operands
        # each instruction is specific to the type of its operand
        operand_func = get_operand_func(opcode)
        output, instruction_pointer = operand_func(operand, register_map, instruction_pointer, output)
    return output


def find_initial_value_for_quine_solve(program_instructions: list[int]) -> None:
    a = BitVec("A", 51)
    opt = Optimize()
    for out in program_instructions:
        b = a & 7
        b ^= 2
        c = a >> b
        b ^= c
        b ^= 3
        opt.add(b & 7 == out)
        a >>= 3
    opt.add(a == 0)
    opt.minimize(a)
    result = opt.check()
    if result == sat:
        print("Model:", opt.model())
        # print("Min A:", opt.model()[a], "=", opt.lower(h))
    else:
        print("No solution found")
    # brute force method below
    # for initial_a in range(1, 100_000_000):  # Arbitrarily high upper limit
    #     register_map: dict[RegisterKeyType, int] = {"A": initial_a, "B": 0, "C": 0}
    #     output = process_instructions(register_map, program_instructions)
    #     if output == program_instructions:
    #         print(f"Found matching value for A: {initial_a}")
    #         return initial_a  # Return the value of A that works

    # raise ValueError("No valid value for A found within the given range")


def soln(input_file: Path) -> tuple[str, int]:
    register_map, program_instructions = parse_input(input_file)
    original_program_instructions = program_instructions.copy()
    print(f"Register map: {register_map}")
    print(f"Program Instructions: {program_instructions}")
    output = process_instructions(register_map, program_instructions)
    print("Part 1:")
    answer_pt1 = ",".join(map(str, output))
    print(",".join(map(str, output)))
    print("Register map:")
    print(register_map)
    print("original_program_instructions", original_program_instructions)
    find_initial_value_for_quine_solve(original_program_instructions)
    return (answer_pt1, 0)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    # input_file = curr_dir.parent / "inputs" / "day17_small.txt"
    input_file = curr_dir.parent / "inputs" / "day17.txt"
    # input_file = curr_dir.parent / "inputs" / "day17_small_pt2.txt"
    are_testing = False
    if are_testing:
        # register_map: dict[RegisterKeyType, int] = {"A": 0, "B": 0, "C": 9}
        # output = process_instructions(register_map=register_map, program_instructions=[2, 6])
        # print("Test 1")
        # print(output)
        # print(register_map)

        # register_map: dict[RegisterKeyType, int] = {"A": 10, "B": 0, "C": 0}
        # output = process_instructions(register_map=register_map, program_instructions=[5, 0, 5, 1, 5, 4])
        # print("Test 2")
        # print(output)
        # print(register_map)

        # New test scenarios
        register_map: dict[RegisterKeyType, int] = {"A": 2024, "B": 0, "C": 0}
        output = process_instructions(register_map=register_map, program_instructions=[0, 1, 5, 4, 3, 0])
        print("Test 3")
        print(output)  # Expected output: 4,2,5,6,7,7,7,7,3,1,0
        print(register_map)  # Expected register A: 0

        # register_map: dict[RegisterKeyType, int] = {"A": 10, "B": 29, "C": 0}
        # output = process_instructions(register_map=register_map, program_instructions=[1, 7])
        # print("Test 4")
        # print(output)  # Expected output: []
        # print(register_map)  # Expected register B: 26

        # register_map: dict[RegisterKeyType, int] = {"A": 0, "B": 2024, "C": 43690}
        # output = process_instructions(register_map=register_map, program_instructions=[4, 0])
        # print("Test 5")
        # print(output)  # Expected output: []
        # print(register_map)  # Expected register B: 44354

    else:
        print(soln(input_file))
