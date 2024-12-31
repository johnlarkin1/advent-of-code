/**
 * CAUTION: I used LLMs to translate this from Python -> Rust
 **/
use crate::solution::Solution;
use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::Path;

type Coordinate = (usize, usize);
type Matrix = Vec<Vec<char>>;

const FREE_SPACE_CHAR: char = '.';

pub struct Day08;

fn is_alphanumeric(c: char) -> bool {
    c.is_alphabetic() || c.is_numeric()
}

fn algo(matrix: &Matrix) -> (usize, usize) {
    let num_rows = matrix.len();
    let num_cols = matrix[0].len();
    let mut antinode_locations_pt1: HashSet<Coordinate> = HashSet::new();
    let mut antinode_locations_pt2: HashSet<Coordinate> = HashSet::new();

    let mut antenna_frequency_to_position: HashMap<char, Vec<Coordinate>> = HashMap::new();

    for (row_idx, row) in matrix.iter().enumerate() {
        for (col_idx, &val) in row.iter().enumerate() {
            if is_alphanumeric(val) {
                antenna_frequency_to_position
                    .entry(val)
                    .or_insert_with(Vec::new)
                    .push((row_idx, col_idx));
            }
        }
    }

    let mut matrix_copy = matrix.clone();

    for (_, positions) in antenna_frequency_to_position {
        if positions.len() < 2 {
            continue;
        }

        for (idx, &p1) in positions.iter().enumerate() {
            for &p2 in positions.iter().skip(idx + 1) {
                let run = (p2.0 as isize) - (p1.0 as isize);
                let rise = (p2.1 as isize) - (p1.1 as isize);

                antinode_locations_pt2.insert(p1);
                antinode_locations_pt2.insert(p2);

                let mut forward_point = p2;
                let mut backward_point = p1;

                let mut is_part1_forward = true;
                let mut is_part1_backward = true;

                loop {
                    let potential_antinode = (
                        (forward_point.0 as isize + run) as usize,
                        (forward_point.1 as isize + rise) as usize,
                    );

                    if potential_antinode.0 >= num_rows || potential_antinode.1 >= num_cols {
                        break;
                    }

                    if is_part1_forward {
                        antinode_locations_pt1.insert(potential_antinode);
                    }

                    if !antinode_locations_pt2.contains(&potential_antinode) {
                        if matrix_copy[potential_antinode.0][potential_antinode.1] == '.' {
                            matrix_copy[potential_antinode.0][potential_antinode.1] = '#';
                        }
                        antinode_locations_pt2.insert(potential_antinode);
                    }

                    forward_point = potential_antinode;
                    is_part1_forward = false;
                }

                loop {
                    let potential_antinode = (
                        (backward_point.0 as isize - run) as usize,
                        (backward_point.1 as isize - rise) as usize,
                    );

                    if potential_antinode.0 >= num_rows || potential_antinode.1 >= num_cols {
                        break;
                    }

                    if is_part1_backward {
                        antinode_locations_pt1.insert(potential_antinode);
                    }

                    if !antinode_locations_pt2.contains(&potential_antinode) {
                        if matrix_copy[potential_antinode.0][potential_antinode.1] == '.' {
                            matrix_copy[potential_antinode.0][potential_antinode.1] = '#';
                        }
                        antinode_locations_pt2.insert(potential_antinode);
                    }

                    backward_point = potential_antinode;
                    is_part1_backward = false;
                }
            }
        }
    }

    (antinode_locations_pt1.len(), antinode_locations_pt2.len())
}

fn parse_input_as_matrix(input: &str) -> Matrix {
    input.lines().map(|line| line.chars().collect()).collect()
}

fn soln(input_file: &Path) -> (usize, usize) {
    let input = fs::read_to_string(input_file).expect("Failed to read input file");
    let input_matrix = parse_input_as_matrix(&input);

    algo(&input_matrix)
}

impl Solution for Day08 {
    fn run() {
        println!("Running solution for Day 8!");
        let input_file = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("inputs/day08.txt");
        let (num_antinodes, num_antinodes_with_resonance) = soln(&input_file);
        println!("Part 1: {}", num_antinodes);
        println!("Part 2: {}", num_antinodes_with_resonance);
    }
}
