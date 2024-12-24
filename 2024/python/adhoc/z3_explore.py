from z3 import Reals, set_option, solve

print("\n\n === Problem 1 ===")
d, a, t, v_i, v_f = Reals("d a t v__i v__f")

equations = [
    d == v_i * t + (a * t**2) / 2,
    v_f == v_i + a * t,
]

# Given v_i, t and a, find d
problem = [v_i == 0, t == 4.10, a == 6]

solve(equations + problem)

# Display rationals in decimal notation
set_option(rational_to_decimal=True)

solve(equations + problem)


print("\n\n === Problem 2 ===")
d, a, t, v_i, v_f = Reals("d a t v__i v__f")

equations = [
    d == v_i * t + (a * t**2) / 2,
    v_f == v_i + a * t,
]
print("Kinematic equations:")
print(equations)

# Given v_i, v_f and a, find d
problem = [v_i == 30, v_f == 0, a == -8]
print("Problem:")
print(problem)

print("Solution:")
solve(equations + problem)
