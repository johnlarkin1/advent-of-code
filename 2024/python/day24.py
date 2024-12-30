"""
I feel like this is taking me a fat minute to even grok...

* gates wait for input
* wires need to start with a value
* these are the first section inputs
* second section lists all of the gates and the wires coneected to them
* system produce

I guess my initial thinking is this is basically like building a graph, and then we just apply
all the inputs and propagate through the graph?

But honestly it might be easier to just go from the starting values and go there

Yeah it's like almost a topological sort because it's a dependency graph - directional

---

Ok yay, I'm pretty pleased with my topo-sort type idea for part 1.
nice and fast too.

ok so the second part is pretty interesting. I saw earlier that people were visualizing it manually
and then just detecting which gates were swapped.

I suppose that's an interesting idea given I kind of already have the topological ordering
built out, but I'm guessing the complexity there is that the numbers won't actually add...

So... yeah I guess let's just visualize our graph first and then I can see if we notice anything?
But not exactly sure how I'd determine this programatically.
"""

from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from itertools import combinations
from pathlib import Path
from typing import TypedDict

from graphviz import Digraph

GateGraphType = dict[str, list[str]]
NUM_SWAP_PAIRS = 4


class Testing(Enum):
    SMALL = auto()
    MED = auto()
    LARGE = auto()


TESTING_SCENARIO = Testing.LARGE


class Operation(StrEnum):
    AND = "AND"
    OR = "OR"
    XOR = "XOR"


test_cases = [
    # Simple cases
    (1, 1),
    (3, 5),
    # Powers of 2 at different positions
    (1 << 44, 1),  # Highest bit
    (1 << 43, 1 << 43),  # Two high bits
    (1 << 42, 1 << 41),
    # Numbers with multiple bits set
    (0xF_FFFF_FFFF, 0xF_FFFF_FFFF),  # Many lower bits set
    ((1 << 45) - 1, 1),  # All bits set + 1
    # Original test value
    # Random large 45-bit numbers
    (0x1_FFFF_FFFF, 0x1_0000_0000),
    (0x1_0000_0000, 0x1_0000_0001),
    # Numbers that might affect carry chains
    (0xF_FFFF_FFFF, 1),  # Forces many carries
    ((1 << 44) - 1, 1),  # All bits except highest
]


@dataclass
class WiringRule:
    gate1: str
    op: Operation
    gate2: str
    dst: str

    @staticmethod
    def from_str(line: str) -> "WiringRule":
        part1, part2 = line.strip().split("->")
        part1_list = [part for part in part1.split(" ") if part]
        if len(part1_list) != 3:
            raise AssertionError("parsing error")
        gate1, operand, gate2 = part1_list
        dst = part2.strip()
        return WiringRule(gate1, Operation(operand), gate2, dst)


class GateNode(TypedDict):
    input1: str
    input2: str
    operation: Operation


def parse_input(input_file: Path) -> tuple[dict[str, bool], dict[str, WiringRule], GateGraphType, dict[str, int]]:
    initial_values: dict[str, bool] = {}
    wiring_rules: dict[str, WiringRule] = {}
    # our gate graph goes from input1 -> dst , or input2 -> dst
    # it should be used for finding the next node
    gate_graph_network: dict[str, list[str]] = defaultdict(list)
    indegree_mapping: dict[str, int] = {}

    with open(input_file) as f:
        for line in f:
            if ":" in line:
                wire, value = map(lambda x: x.strip(), line.strip().split(":"))
                initial_values[wire] = True if value == "1" else False
                indegree_mapping[wire] = 0

            if "->" in line:
                wiring_rule = WiringRule.from_str(line)
                wiring_rules[wiring_rule.dst] = wiring_rule

                gate_graph_network[wiring_rule.gate1].append(wiring_rule.dst)
                gate_graph_network[wiring_rule.gate2].append(wiring_rule.dst)

                indegree_mapping[wiring_rule.dst] = 2

    return initial_values, wiring_rules, gate_graph_network, indegree_mapping


def rebuild_gate_graph_and_indegree_mapping(
    initial_values: dict[str, bool], wiring_rules: dict[str, WiringRule]
) -> tuple[GateGraphType, dict[str, int]]:
    gate_graph_network: dict[str, list[str]] = defaultdict(list)
    indegree_mapping: dict[str, int] = {}
    for rule in wiring_rules.values():
        gate_graph_network[rule.gate1].append(rule.dst)
        gate_graph_network[rule.gate2].append(rule.dst)
        indegree_mapping[rule.dst] = 2

    for gate in initial_values:
        indegree_mapping[gate] = 0
    return gate_graph_network, indegree_mapping


def create_gate_visualization(
    initial_values: dict[str, bool], wiring_rules: dict[str, WiringRule], gate_graph_network: dict[str, list[str]]
) -> Digraph:
    dot = Digraph(comment="Gate Network")
    dot.attr(size="14,10")
    dot.attr(dpi="1200")
    dot.attr(rankdir="LR")
    dot.attr(margin="0")

    # Define operation colors
    op_colors = {
        "XOR": "#FF0000",  # Red for XOR
        "AND": "#00AA00",  # Green for AND
        "OR": "#0000FF",  # Blue for OR
    }

    # Create more compact subgraphs
    with dot.subgraph(name="cluster_inputs") as inputs:
        inputs.attr(rank="same")
        for gate in sorted([g for g in initial_values if g.startswith("x")]):
            inputs.node(
                gate,
                gate,
                shape="diamond",
                color="#9B59B6",
                style="filled",
                fillcolor="#E8D5E4",
                width="0.3",
                height="0.2",
                fontsize="8",
            )
        for gate in sorted([g for g in initial_values if g.startswith("y")]):
            inputs.node(
                gate,
                gate,
                shape="diamond",
                color="#F1C40F",
                style="filled",
                fillcolor="#FCF3CF",
                width="0.3",
                height="0.2",
                fontsize="8",
            )

    for dst, rule in wiring_rules.items():
        color = op_colors[rule.op]
        label = f"{dst}" if dst.startswith("z") else f"{dst}\n{rule.op}"

        if dst.startswith("z"):
            shape = "box"
            width = "0.4"
            height = "0.3"
            fontsize = "10"
        else:
            shape = "ellipse"
            width = "0.3"
            height = "0.2"
            fontsize = "8"

        dot.node(
            dst,
            label,
            shape=shape,
            color=color,
            style="filled",
            fillcolor="white",
            width=width,
            height=height,
            fontsize=fontsize,
        )

        dot.edge(rule.gate1, dst, color=color, penwidth="0.5")
        dot.edge(rule.gate2, dst, color=color, penwidth="0.5")

    dot.attr(nodesep="0.12")
    dot.attr(ranksep="0.15")
    dot.attr(overlap="scale")
    dot.attr(splines="polyline")
    dot.attr(pack="true")
    return dot


def create_gate_visualization_take2(
    initial_values: dict[str, bool], wiring_rules: dict[str, WiringRule], gate_graph_network: dict[str, list[str]]
) -> Digraph:
    dot = Digraph(comment="Gate Network")
    dot.attr(size="100,30")
    dot.attr(dpi="1200")
    dot.attr("graph", margin="1")

    dot.attr("graph", rankdir="TB")
    dot.attr("graph", ranksep="1.0")
    dot.attr("graph", nodesep="0.5")

    dot.attr("node", shape="circle")
    dot.attr("node", width="0.6")
    dot.attr("node", height="0.6")
    dot.attr("node", fontsize="14")
    dot.attr("edge", arrowsize="0.6")
    dot.attr("edge", penwidth="2.0")

    flagged_node_set: set[str] = set(["cgm", "gbs", "hwq", "rrq", "thm", "z08", "z22", "z29"])

    with dot.subgraph() as s0:
        s0.attr(rank="same")

        for i in range(45):
            node_name = f"x{i:02d}"
            if node_name in initial_values:
                s0.node(node_name, node_name, style="filled", fillcolor="lightblue")

    with dot.subgraph() as s1:
        s1.attr(rank="same")

        for i in range(45):
            node_name = f"y{i:02d}"
            if node_name in initial_values:
                s1.node(node_name, node_name, style="filled", fillcolor="lightyellow")

    middle_gates = {}
    for dst, rule in wiring_rules.items():
        if not dst.startswith("z"):
            bit_pos = -1

            for i in range(45):
                x_bit = f"x{i:02d}"
                y_bit = f"y{i:02d}"
                if rule.gate1 in [x_bit, y_bit] or rule.gate2 in [x_bit, y_bit]:
                    bit_pos = i
                    break
            if bit_pos != -1:
                middle_gates[bit_pos] = middle_gates.get(bit_pos, []) + [dst]

    print(middle_gates)
    for pos in range(45):
        with dot.subgraph() as sm:
            sm.attr(rank="same")
            if pos in middle_gates:
                for gate in middle_gates[pos]:
                    rule = wiring_rules[gate]
                    fillcolor = "lightgray" if gate not in flagged_node_set else "orange"
                    sm.node(gate, f"{gate}\n{rule.op}", style="filled", fillcolor=fillcolor)

    with dot.subgraph() as s2:
        s2.attr(rank="same")
        for i in range(45):
            node_name = f"z{i:02d}"
            if node_name in wiring_rules:
                fillcolor = "lightgreen" if node_name not in flagged_node_set else "orange"
                s2.node(node_name, node_name, style="filled", fillcolor=fillcolor)

    for dst, rule in wiring_rules.items():
        if not dot.source.count(rule.gate1):
            fillcolor = "lightgray" if rule.gate1 not in flagged_node_set else "orange"
            dot.node(rule.gate1, style="filled", fillcolor=fillcolor)
        if not dot.source.count(rule.gate2):
            fillcolor = "lightgray" if rule.gate2 not in flagged_node_set else "orange"
            dot.node(rule.gate2, style="filled", fillcolor=fillcolor)
        if not dot.source.count(dst):
            fillcolor = "lightgray" if rule.dst not in flagged_node_set else "orange"
            dot.node(dst, style="filled", fillcolor=fillcolor)

        dot.edge(rule.gate1, dst, color="green:invis:green")
        dot.edge(rule.gate2, dst, color="green:invis:green")

        if dst.startswith("z"):
            bit_num = int(dst[1:])
            if bit_num > 0:
                prev_z = f"z{bit_num-1:02d}"
                if prev_z in wiring_rules:
                    dot.edge(prev_z, dst, color="red:invis:red")

    dot.attr("graph", splines="polyline")
    dot.attr("edge", penwidth="0.5")

    return dot


def solve_gate_logic(
    initial_values: dict[str, bool],
    wiring_rules: dict[str, WiringRule],
    gate_graph_network: GateGraphType,
    indegree_mapping: dict[str, int],
) -> dict[str, bool]:
    # z_gate_solved_dict: dict[str, bool] = {gate: False for gate in gate_graph.keys() if gate.startswith("z")}
    values_dict: dict[str, bool] = initial_values.copy()
    # are_all_z_gates_solved = False

    # so if we're approaching it like topo-sort then are initial values are basically going to
    # be our in-degree of 0 ones
    explore_queue: deque[str] = deque([gate for gate, indegree in indegree_mapping.items() if indegree == 0])
    topological_order = []
    while explore_queue:
        current_gate = explore_queue.popleft()
        topological_order.append(current_gate)

        # let's decrease the destination indegree
        neighbors = gate_graph_network.get(current_gate)
        if not neighbors:
            continue

        for neighbor in neighbors:
            indegree_mapping[neighbor] -= 1

            # if the indegree is 0 then we can add it to the queue
            if indegree_mapping[neighbor] == 0:
                # this means we have already solved our previous ones
                # let's get our operation
                wiring_rule = wiring_rules[neighbor]
                operation = wiring_rule.op
                if operation == Operation.AND:
                    values_dict[neighbor] = values_dict[wiring_rule.gate1] & values_dict[wiring_rule.gate2]
                elif operation == Operation.OR:
                    values_dict[neighbor] = values_dict[wiring_rule.gate1] | values_dict[wiring_rule.gate2]
                elif operation == Operation.XOR:
                    values_dict[neighbor] = values_dict[wiring_rule.gate1] ^ values_dict[wiring_rule.gate2]
                else:
                    raise AssertionError("Unknown operation")

                explore_queue.append(neighbor)
    # print("Topological order", topological_order)
    return values_dict


def get_binary_and_int_val(values: dict[str, bool], target_char: str) -> tuple[str, int]:
    z_values = [(key, 1) if value else (key, 0) for key, value in values.items() if key.startswith(target_char)]
    z_values.sort(key=lambda x: x[0])
    binary_string = "".join(map(lambda x: str(x[1]), reversed(z_values)))
    return binary_string, int(binary_string, 2)


def swap_outputs(wiring_rules: dict[str, WiringRule], gates_to_swap: list[tuple[str, str]]) -> dict[str, WiringRule]:
    new_rules = wiring_rules.copy()
    for gate1, gate2 in gates_to_swap:
        new_rules[gate1], new_rules[gate2] = new_rules[gate2], new_rules[gate1]

        new_rules[gate1] = WiringRule(
            gate1=new_rules[gate1].gate1, op=new_rules[gate1].op, gate2=new_rules[gate1].gate2, dst=gate1
        )
        new_rules[gate2] = WiringRule(
            gate1=new_rules[gate2].gate1, op=new_rules[gate2].op, gate2=new_rules[gate2].gate2, dst=gate2
        )
    return new_rules


def find_rule_breaking_gates(wiring_rules: dict[str, WiringRule]) -> tuple[set[str], set[str]]:
    """
    Brutal... logic isn't mine sadly.

    Took inspiration from here: https://www.reddit.com/r/adventofcode/comments/1hla5ql/2024_day_24_part_2_a_guide_on_the_idea_behind_the/
    """
    rule1_breakers = set()
    rule2_breakers = set()

    # Find the highest z-gate number to identify the last bit
    max_z = max((int(dst[1:]) for dst in wiring_rules.keys() if dst.startswith("z")), default=0)

    for dst, rule in wiring_rules.items():
        # Rule 1: z-outputs must be XOR (except last bit)
        if dst.startswith("z") and int(dst[1:]) != max_z:
            if rule.op != Operation.XOR:
                rule1_breakers.add(dst)

        # Rule 2: non-z gates with non-x/y inputs must be AND/OR
        elif not dst.startswith("z"):
            has_internal_inputs = not (
                (rule.gate1.startswith("x") or rule.gate1.startswith("y"))
                and (rule.gate2.startswith("x") or rule.gate2.startswith("y"))
            )
            if has_internal_inputs and rule.op == Operation.XOR:
                rule2_breakers.add(dst)

    return rule1_breakers, rule2_breakers


def find_first_z_output(wiring_rules: dict[str, WiringRule], start_gate: str) -> str | None:
    """
    Recursively finds the first z-output that depends on the given gate.
    Returns the z-output gate name or None if not found.
    """

    def dfs(gate: str, visited: set[str]) -> str | None:
        if gate.startswith("z"):
            return gate
        if gate in visited:
            return None

        visited.add(gate)
        # Find all rules where this gate is an input
        for dst, rule in wiring_rules.items():
            if rule.gate1 == gate or rule.gate2 == gate:
                result = dfs(dst, visited)
                if result:
                    return result
        return None

    return dfs(start_gate, set())


def find_fourth_pair(
    initial_values: dict[str, bool],
    wiring_rules: dict[str, WiringRule],
    gate_graph_network: GateGraphType,
    expected_z_val: int,
    known_pairs: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    possible_gate_fixes = []
    current_rules = wiring_rules.copy()
    for pair in known_pairs:
        current_rules = swap_outputs(current_rules, [pair])

    swapped_gates = set(gate for pair in known_pairs for gate in pair)
    remaining_gates = [
        gate
        for gate in current_rules.keys()
        if not (gate.startswith("x") or gate.startswith("y")) and gate not in swapped_gates
    ]

    print(f"\nTesting combinations from {len(remaining_gates)} remaining gates...")
    # Track best attempt
    best_diff = float("inf")
    best_pair = None

    # Try every possible pair from remaining gates
    tested = 0
    for gate1, gate2 in combinations(remaining_gates, 2):
        tested += 1
        if tested % 1000 == 0:
            print(f"Tested {tested} combinations...")

        # Try swapping this pair
        test_rules = swap_outputs(current_rules, [(gate1, gate2)])
        gate_graph_network, new_indegree = rebuild_gate_graph_and_indegree_mapping(initial_values, test_rules)
        resolved_values = solve_gate_logic(initial_values, test_rules, gate_graph_network, new_indegree)

        try:
            result_bin, result = get_binary_and_int_val(resolved_values, "z")
            diff = abs(result - expected_z_val)

            if diff < best_diff:
                best_diff = diff
                best_pair = (gate1, gate2)
            if result == expected_z_val:
                print(f"\nFound exact match with pair: {gate1},{gate2}")
                possible_gate_fixes.append((gate1, gate2))

        except ValueError:
            continue

    if best_pair:
        print(f"\nBest attempt was {best_pair} (off by {best_diff})")
    return possible_gate_fixes


def find_matching_z_gate(z_gate: str, rule1_breakers: set[str]) -> str | None:
    """
    Find the previous z-gate in rule1_breakers that comes before this one.
    """
    bit_num = int(z_gate[1:])
    # Look for any z-gate with a lower number in our rule1_breakers
    candidates = [gate for gate in rule1_breakers if gate.startswith("z") and int(gate[1:]) < bit_num]
    if candidates:
        # Return the highest numbered z-gate that's less than our current one
        return max(candidates, key=lambda x: int(x[1:]))
    return None


def find_all_swaps(
    wiring_rules: dict[str, WiringRule],
    initial_values: dict[str, bool],
    gate_graph_network: GateGraphType,
    expected_z_val: int,
) -> list[tuple[str, str]]:
    rule1_breakers, rule2_breakers = find_rule_breaking_gates(wiring_rules)
    print("\nRule 1 breakers:", rule1_breakers)
    print("Rule 2 breakers:", rule2_breakers)
    initial_swaps = []

    # First, pair rule1 and rule2 breakers
    for rule2_gate in rule2_breakers:
        z_output = find_first_z_output(wiring_rules, rule2_gate)
        print(f"\nRule 2 breaker: {rule2_gate} -> leads to z-gate: {z_output}")
        if z_output:
            matching_z = find_matching_z_gate(z_output, rule1_breakers)
            print(f"Found matching z-gate: {matching_z}")
            if matching_z:
                initial_swaps.append((rule2_gate, matching_z))
                rule1_breakers.remove(matching_z)  # Don't use this z-gate again

    print("\nInitial swaps:")
    print(initial_swaps)
    final_pair_possibilities = find_fourth_pair(
        initial_values, wiring_rules, gate_graph_network, expected_z_val, initial_swaps
    )
    for possible_gate_pair in final_pair_possibilities:
        test_rules = swap_outputs(wiring_rules, initial_swaps + [possible_gate_pair])
        all_cases_work = True
        for x, y in test_cases:
            if not test_adder_with_values(test_rules, gate_graph_network, x, y):
                print(f"Failed for test case: {x} + {y}")
                all_cases_work = False
                break

        if all_cases_work:
            print(f"Found pair that works for all test cases: {possible_gate_pair}")
            return initial_swaps + [possible_gate_pair]

    return initial_swaps


def test_adder_with_values(
    wiring_rules: dict[str, WiringRule], gate_graph_network: GateGraphType, x: int, y: int
) -> bool:
    """Test adder with specific x,y values."""
    # Set up test values
    test_values = {}
    for i in range(45):  # 45-bit numbers
        x_bit = f"x{i:02d}"
        y_bit = f"y{i:02d}"
        test_values[x_bit] = bool((x >> i) & 1)
        test_values[y_bit] = bool((y >> i) & 1)

    # Run circuit
    gate_graph_network, indegree_mapping = rebuild_gate_graph_and_indegree_mapping(test_values, wiring_rules)
    resolved_values = solve_gate_logic(test_values, wiring_rules, gate_graph_network, indegree_mapping)
    _, result = get_binary_and_int_val(resolved_values, "z")

    return result == (x + y)


def soln(input_file: Path) -> tuple[int, str]:
    part1_soln = 0
    part2_soln = 0
    initial_values, wiring_rules, gate_graph_network, indegree_mapping = parse_input(input_file)

    working_indegree_mapping = indegree_mapping.copy()
    # Part 1
    resolved_values = solve_gate_logic(initial_values, wiring_rules, gate_graph_network, working_indegree_mapping)
    _, part1_soln = get_binary_and_int_val(resolved_values, "z")
    print(f"Part 1: {part1_soln}")

    # Part 2
    x_bin_str, x_val = get_binary_and_int_val(initial_values, "x")
    y_bin_str, y_val = get_binary_and_int_val(initial_values, "y")
    exp_z_val = x_val + y_val
    exp_z_bin_str = bin(exp_z_val)[2:]

    print(f"x_bin: {x_bin_str} x_val: {x_val}")
    print(f"y_bin: {y_bin_str} y_val: {y_val}")
    print(f"Expected z_bin: {exp_z_bin_str} z_val: {exp_z_val}")
    # dot = create_gate_visualization(initial_values, wiring_rules, gate_graph_network)
    # dot.save("gate_network.dot")
    # dot.render("gate_network", format="png", cleanup=True)
    # dot = create_gate_visualization_take2(initial_values, wiring_rules, gate_graph_network)
    # dot.render("gate_network_take2", format="png", cleanup=True)
    # gates_to_swap, result = try_all_gate_combinations(
    #     initial_values, wiring_rules, gate_graph_network, indegree_mapping, exp_z_val
    # )
    # print("Gates to swap", gates_to_swap)
    # print("Result", result)
    swaps = find_all_swaps(wiring_rules, initial_values, gate_graph_network, exp_z_val)
    flat_swaps = [gate for pair in swaps for gate in pair]
    part2_soln = ",".join(sorted(flat_swaps))
    print("swaps", swaps)
    for swap in swaps:
        wiring_rules = swap_outputs(wiring_rules, [swap])

    gate_graph_network, working_indegree_mapping = rebuild_gate_graph_and_indegree_mapping(initial_values, wiring_rules)
    resolved_values = solve_gate_logic(initial_values, wiring_rules, gate_graph_network, working_indegree_mapping)
    _, part2_z_ans = get_binary_and_int_val(resolved_values, "z")
    if part2_z_ans == exp_z_val:
        print("passed")
    else:
        print(f"failed: {part2_z_ans} != {exp_z_val}")

    return (part1_soln, part2_soln)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent

    match TESTING_SCENARIO:
        case Testing.SMALL:
            input_file = curr_dir.parent / "inputs" / "day24_small.txt"
        case Testing.MED:
            input_file = curr_dir.parent / "inputs" / "day24_med.txt"
        case Testing.LARGE:
            input_file = curr_dir.parent / "inputs" / "day24.pt2.txt"
    print(soln(input_file))
