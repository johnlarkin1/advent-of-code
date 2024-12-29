from collections import defaultdict
from pathlib import Path

ARE_TESTING = False

NetworkType = dict[str, set[str]]
NodeTuple = tuple[str, str, str]


def parse_and_build_network_map(input_file: Path) -> NetworkType:
    """
    Builds out a bidirectional map between the computers
    """
    with open(input_file) as f:
        network_graph = defaultdict(set)
        for line in f.readlines():
            line = line.strip()
            if line:
                src, dst = map(lambda x: x.strip(), line.split("-"))
                network_graph[src].add(dst)
                network_graph[dst].add(src)

    return network_graph


def find_three_connected_nodes_set(network_graph: NetworkType) -> set[NodeTuple]:
    """
    Finds `sets of three computers where each computer in the set is connected to the other two computers.`


    """
    three_connected_nodes = set()
    for node_a, connected_nodes in network_graph.items():
        connected_nodes_list = list(connected_nodes)
        for idx1, node_b in enumerate(connected_nodes_list):
            for node_c in connected_nodes_list[idx1 + 1 :]:
                # So now we need to ensure each computer is connected to the other 2.
                # node c IN (node_b's connections) and node_c IN (node_a's connections)
                # node_b IN (node_c's connections) and node_b IN (node_a's connections)
                # node_a IN (node_b's connections) and node_a IN (node_c's connections)
                # given how we're looping we already know that
                # node_b and node_c are connected to node_a
                if (
                    node_c in network_graph[node_b]
                    and node_b in network_graph[node_c]
                    and node_a in network_graph[node_b]
                    and node_a in network_graph[node_c]
                ):
                    three_connected_nodes.add(tuple(sorted([node_a, node_b, node_c])))

    return three_connected_nodes


# def find_largest_connected_component(network_graph: NetworkType) -> set[str]:
#     def dfs(node: str, visited: set[str], component: set[str]) -> None:
#         visited.add(node)
#         component.add(node)
#         for neighbor in network_graph[node]:
#             if neighbor not in visited:
#                 dfs(neighbor, visited, component)

#     visited: set[str] = set()
#     largest_component: set[str] = set()

#     for node in network_graph:
#         if node not in visited:
#             current_component: set[str] = set()
#             dfs(node, visited, current_component)
#             print(f"Current component: {current_component}")

#             if len(current_component) > len(largest_component):
#                 largest_component = current_component

#     return largest_component


def bron_kerbosch(graph: NetworkType, R: set[str], P: set[str], X: set[str], cliques: list[set[str]]) -> None:
    """
    https://en.wikipedia.org/wiki/Bron%E2%80%93Kerbosch_algorithm

    """
    if not P and not X:
        # Found a maximal clique
        cliques.append(R)
        return
    for node in list(P):
        neighbors = set(graph[node])
        bron_kerbosch(graph, R.union({node}), P.intersection(neighbors), X.intersection(neighbors), cliques)
        P.remove(node)
        X.add(node)


def largest_clique(graph: NetworkType) -> set[str]:
    """
    Finds the largest clique in the graph using the Bron–Kerbosch algorithm.
    """
    cliques = []
    bron_kerbosch(graph, set(), set(graph.keys()), set(), cliques)
    return max(cliques, key=len)


def any_node_starts_with_char(node_tuple: NodeTuple, char: str) -> bool:
    return any(node.startswith(char) for node in node_tuple)


def soln(input_file: Path) -> tuple[int, str]:
    pt1_ans = 0
    pt2_ans = 0
    network_graph = parse_and_build_network_map(input_file)
    three_connected_nodes = find_three_connected_nodes_set(network_graph)
    for node_tuple in three_connected_nodes:
        if any_node_starts_with_char(node_tuple, "t"):
            pt1_ans += 1

    largest_component = largest_clique(network_graph)
    sorted_largest_componet = sorted(largest_component)
    pt2_ans = ",".join(sorted_largest_componet)
    return (pt1_ans, pt2_ans)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    if ARE_TESTING:
        input_file = curr_dir.parent / "inputs" / "day23_small.txt"
    else:
        input_file = curr_dir.parent / "inputs" / "day23.txt"
    print(soln(input_file))
