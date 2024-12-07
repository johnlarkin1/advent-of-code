use crate::solution::Solution;
use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::Path;

pub struct Day06;

/// Type alias for a tuple representing a 2D grid location.
/// This is useful for improving readability and ensuring consistency.
type Location = (i32, i32);

/// A constant representing a wall or blocker in the map.
const BLOCKER: char = '#';

/// A lazy_static block is used to initialize static data structures.
/// This creates a static, global `HashMap` mapping guard directions to their movement offsets.
/// Rust's `lazy_static` allows safe, lazy initialization of global variables.
lazy_static::lazy_static! {
    static ref GUARD_NEXT_POSITIONS: HashMap<char, Location> = {
        let mut m = HashMap::new();
        m.insert('^', (-1, 0)); // Move up (row decreases)
        m.insert('v', (1, 0));  // Move down (row increases)
        m.insert('<', (0, -1)); // Move left (col decreases)
        m.insert('>', (0, 1));  // Move right (col increases)
        m
    };
}

/// Parses a string input into a 2D vector of characters (Vec<Vec<char>>).
/// This demonstrates Rust's iterator and collection functionality.
fn parse_input_as_matrix(input_str: &str) -> Vec<Vec<char>> {
    input_str
        .lines() // Splits the input into lines (an iterator of &str).
        .map(|line| line.chars().collect()) // Converts each line into a Vec<char>.
        .collect() // Collects all Vec<char> into a Vec<Vec<char>>.
}

/// Finds the starting location and direction of the guard in the map.
/// Demonstrates how to iterate over 2D vectors and use pattern matching.
fn find_guard_starting_loc(matrix: &Vec<Vec<char>>) -> (Location, char) {
    for (row_idx, row) in matrix.iter().enumerate() {
        for (col_idx, &cell) in row.iter().enumerate() {
            // Checks if the current cell matches any guard direction.
            if GUARD_NEXT_POSITIONS.contains_key(&cell) {
                return ((row_idx as i32, col_idx as i32), cell);
            }
        }
    }
    // Default if no guard is found.
    ((-1, -1), '<')
}

/// Turns the guard 90 degrees clockwise.
/// Demonstrates Rust's `match` statement for pattern matching.
fn turn_guard(curr_dir: char) -> char {
    match curr_dir {
        '^' => '>',
        'v' => '<',
        '<' => '^',
        '>' => 'v',
        _ => panic!("Invalid guard direction"), // Panics if input is invalid (used here for simplicity).
    }
}

/// Advances the guard to the next location based on the current direction.
/// Demonstrates tuple destructuring and accessing a static `HashMap`.
fn advance_guard(curr_dir: char, curr_loc: Location) -> Location {
    let (row, col) = curr_loc; // Destructures the tuple into its components.
    let (drow, dcol) = *GUARD_NEXT_POSITIONS.get(&curr_dir).unwrap(); // Accesses the guard direction offsets.
    (row + drow, col + dcol) // Returns the new location as a tuple.
}

/// Checks if the given location is out of bounds in the matrix.
/// Demonstrates tuple destructuring and comparison with boundaries.
fn is_out_of_bounds(next_loc: Location, num_rows: usize, num_cols: usize) -> bool {
    let (row, col) = next_loc; // Destructures the location tuple.
    row < 0 || col < 0 || row >= num_rows as i32 || col >= num_cols as i32
}

/// Checks if the guard is blocked at the given location.
/// Demonstrates indexing a 2D vector with tuple values.
fn is_guard_blocked(next_loc: Location, map: &Vec<Vec<char>>) -> bool {
    let (row, col) = next_loc; // Destructures the location tuple.
    map[row as usize][col as usize] == BLOCKER // Indexes the 2D vector safely.
}

/// Simulates the guard's movement to determine if a loop forms with a blocker.
/// Demonstrates how to use a `HashSet` to track visited states.
fn would_loop_with_blocker(guard_map: &Vec<Vec<char>>) -> bool {
    let num_rows = guard_map.len(); // Length of outer vector (number of rows).
    let num_cols = guard_map[0].len(); // Length of inner vector (number of columns).
    let (mut guard_loc, mut guard_dir) = find_guard_starting_loc(guard_map);
    let mut visited_states = HashSet::new(); // Creates a HashSet to store visited states.

    loop {
        let state = (guard_loc, guard_dir);
        if visited_states.contains(&state) {
            // `HashSet::contains` checks if the state was visited.
            return true; // Loop detected if the state has been visited.
        }
        visited_states.insert(state); // Adds the state to the HashSet.

        let next_loc = advance_guard(guard_dir, guard_loc);
        if is_out_of_bounds(next_loc, num_rows, num_cols) {
            // Checks if the guard has moved out of bounds.
            return false;
        }
        if is_guard_blocked(next_loc, guard_map) {
            // Turns the guard if blocked.
            guard_dir = turn_guard(guard_dir);
        } else {
            guard_loc = next_loc; // Moves the guard to the next location.
        }
    }
}

/// Simulates placing blockers at visited locations to test for potential loop points.
/// Demonstrates cloning vectors and iterating over `HashSet`.
fn simulate_blocker_positions_from_visited_locs(
    guard_map: &Vec<Vec<char>>,
    visited_locations: &HashSet<Location>,
) -> usize {
    let mut num_potential_blocking_spots = 0; // Counter for potential blocking locations.
    let orig_map = guard_map.clone(); // Clones the map (deep copy) for simulation.

    for &(row, col) in visited_locations {
        let mut sim_guard_map = orig_map.clone(); // Clones the original map for each simulation.
        sim_guard_map[row as usize][col as usize] = BLOCKER; // Adds a blocker at the location.

        if would_loop_with_blocker(&sim_guard_map) {
            // Checks if the blocker causes a loop.
            num_potential_blocking_spots += 1;
        }
    }
    num_potential_blocking_spots
}

fn soln(input_file: &Path) -> (i64, i64) {
    let input = fs::read_to_string(input_file).unwrap(); // `.unwrap()` handles potential errors.
    let guard_map = parse_input_as_matrix(&input); // Parses the input into a 2D map.

    let num_rows = guard_map.len();
    let num_cols = guard_map[0].len();

    let (mut guard_loc, mut guard_dir) = find_guard_starting_loc(&guard_map);

    let mut visited_nodes = HashSet::new(); // A HashSet to store all visited locations.
    let mut hit_wall_guard_locations = Vec::new(); // A vector to store locations where the guard hits walls.

    let mut guard_in_map = true; // Tracks if the guard is still within bounds.

    while guard_in_map {
        let next_loc = advance_guard(guard_dir, guard_loc);
        if is_out_of_bounds(next_loc, num_rows, num_cols) {
            // Breaks the loop if the guard goes out of bounds.
            guard_in_map = false;
            break;
        }

        if is_guard_blocked(next_loc, &guard_map) {
            // If blocked, turn the guard and record the location.
            hit_wall_guard_locations.push(guard_loc);
            guard_dir = turn_guard(guard_dir);
        }

        let true_next_loc = advance_guard(guard_dir, guard_loc);
        visited_nodes.insert(true_next_loc); // Adds the location to the visited set.
        guard_loc = true_next_loc; // Updates the guard's location.
    }

    let num_blocking_locations =
        simulate_blocker_positions_from_visited_locs(&guard_map, &visited_nodes);

    (visited_nodes.len() as i64, num_blocking_locations as i64)
}

impl Solution for Day06 {
    fn run() {
        println!("Running solution for Day 6!");
        let input_file = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("inputs/day06.txt");
        let (part1, part2) = soln(&input_file);
        println!("day06 solution (pt1): {}", part1);
        println!("day06 solution (pt2): {}", part2);
    }
}
