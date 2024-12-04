use crate::solution::Solution;

use std::fs;
use std::path::Path;

const TARGET: &str = "XMAS";
const TARGET_REVERSE: &str = "SAMX";
const TARGET_PT2: &str = "MAS";
const TARGET_PT2_REVERSE: &str = "SAM";

const LEN_TARGET: usize = 4;
const LEN_TARGET_PT2: usize = 3;

type Matrix = Vec<Vec<char>>;

pub struct Day04;

fn parse_input_as_matrix(input: &str) -> Matrix {
    input.lines().map(|line| line.chars().collect()).collect()
}

fn is_target(s: &str, target: &str, target_reverse: &str) -> bool {
    s == target || s == target_reverse
}

fn count_xmas_horizontal(row: usize, col: usize, matrix: &Matrix) -> usize {
    if col + LEN_TARGET > matrix[row].len() {
        return 0;
    }
    let substring: String = matrix[row][col..col + LEN_TARGET].iter().collect();
    is_target(&substring, TARGET, TARGET_REVERSE) as usize
}

fn count_xmas_vertical(row: usize, col: usize, matrix: &Matrix) -> usize {
    if row + LEN_TARGET > matrix.len() {
        return 0;
    }
    let substring: String = matrix[row..row + LEN_TARGET]
        .iter()
        .map(|r| r[col])
        .collect();
    is_target(&substring, TARGET, TARGET_REVERSE) as usize
}

fn count_xmas_diagonal(row: usize, col: usize, matrix: &Matrix) -> usize {
    let mut xmas_count = 0;

    // Forward diagonal
    if row + LEN_TARGET <= matrix.len() && col + LEN_TARGET <= matrix[row].len() {
        let forward_diagonal: String = (0..LEN_TARGET).map(|i| matrix[row + i][col + i]).collect();
        if is_target(&forward_diagonal, TARGET, TARGET_REVERSE) {
            xmas_count += 1;
        }
    }

    // Backward diagonal
    if row + LEN_TARGET <= matrix.len() && col >= LEN_TARGET - 1 {
        let backward_diagonal: String = (0..LEN_TARGET).map(|i| matrix[row + i][col - i]).collect();
        if is_target(&backward_diagonal, TARGET, TARGET_REVERSE) {
            xmas_count += 1;
        }
    }

    xmas_count
}

fn check_x_mas_x_shape(row: usize, col: usize, matrix: &Matrix) -> usize {
    let mut xmas_count = 0;
    let curr_val = matrix[row][col];

    if curr_val != 'A' {
        return 0;
    }

    if !(row > 0 && row + 1 < matrix.len() && col > 0 && col + 1 < matrix[row].len()) {
        return 0;
    }

    let mut should_proceed = false;
    let top_left_to_bottom_right_diag = format!(
        "{}{}{}",
        matrix[row - 1][col - 1],
        matrix[row][col],
        matrix[row + 1][col + 1]
    );

    let top_right_to_bottom_left_diag = format!(
        "{}{}{}",
        matrix[row - 1][col + 1],
        matrix[row][col],
        matrix[row + 1][col - 1]
    );

    if (top_left_to_bottom_right_diag == TARGET_PT2
        || top_left_to_bottom_right_diag == TARGET_PT2_REVERSE)
        && (top_right_to_bottom_left_diag == TARGET_PT2
            || top_right_to_bottom_left_diag == TARGET_PT2_REVERSE)
    {
        xmas_count += 1;
    }

    xmas_count
}

fn soln(matrix: &Matrix) -> (usize, usize) {
    let mut total_xmas_count = 0;
    let mut total_xmas_xshape_count = 0;
    for row in 0..matrix.len() {
        for col in 0..matrix[row].len() {
            total_xmas_count += count_xmas_horizontal(row, col, &matrix);
            total_xmas_count += count_xmas_vertical(row, col, &matrix);
            total_xmas_count += count_xmas_diagonal(row, col, &matrix);
            total_xmas_xshape_count += check_x_mas_x_shape(row, col, &matrix);
        }
    }
    (total_xmas_count, total_xmas_xshape_count)
}

impl Solution for Day04 {
    fn run() {
        println!("Running solution for Day 4!");
        let input_file = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("inputs/day04.txt");

        let file_content = fs::read_to_string(input_file).expect("Failed to read input file");
        let matrix = parse_input_as_matrix(&file_content);
        let (pt1, pt2) = soln(&matrix);

        println!("day04 solution (pt1): {}", pt1);
        println!("day04 solution (pt2): {}", pt2);
    }
}
