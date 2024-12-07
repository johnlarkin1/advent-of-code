use crate::solution::Solution;
use itertools::Itertools;
use std::collections::HashSet;
use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

pub struct Day07;

// clone and copy are used to make sure that the enum is copied and not moved
#[derive(Clone, Copy, Debug)]
enum Operation {
    Add,
    Multiply,
    Concatenate,
}

// &[i64] is a slice of i64
// &[Operation] is a slice of Operation
// i64 is the return type
fn left_to_right_eval(nums: &[i64], ops: &[Operation], target: i64) -> i64 {
    let mut result = nums[0];
    for (idx, &num) in nums.iter().enumerate().skip(1) {
        match ops[idx - 1] {
            Operation::Add => result += num,
            Operation::Multiply => result *= num,
            Operation::Concatenate => {
                let concatenated = format!("{}{}", result, num);
                result = concatenated.parse::<i64>().unwrap();
            }
        }
        if result > target {
            return result;
        }
    }
    result
}

fn can_find_equalizer(target: i64, nums: &[i64]) -> bool {
    let num_operators_needed = nums.len() - 1;
    let operations = vec![Operation::Add, Operation::Multiply, Operation::Concatenate];

    // Generate `num_operators_needed` copies of the operations iterator
    let iter = std::iter::repeat(operations).take(num_operators_needed);

    // Use `multi_cartesian_product` to generate combinations
    for ops_combination in iter.multi_cartesian_product() {
        if left_to_right_eval(nums, &ops_combination, target) == target {
            return true;
        }
    }
    false
}

fn can_find_equalizer_cache(
    target: i64,
    nums: &[i64],
    cache: &mut HashSet<(i64, Vec<i64>)>,
) -> bool {
    if cache.contains(&(target, nums.to_vec())) {
        return false;
    }
    let result = can_find_equalizer(target, nums);
    if !result {
        cache.insert((target, nums.to_vec()));
    }
    result
}

fn soln(input_file: &Path) -> (i64, i64) {
    let mut sum_of_valid_targets = 0;
    let file = File::open(input_file).expect("Unable to open file");
    let reader = io::BufReader::new(file);

    let mut cache = HashSet::new();

    for line in reader.lines() {
        let line = line.expect("Unable to read line");
        let cleansed_line = line.trim();
        let parts: Vec<&str> = cleansed_line.split(':').collect();
        let target: i64 = parts[0].parse().unwrap();
        let nums: Vec<i64> = parts[1]
            .split_whitespace()
            .map(|x| x.parse().unwrap())
            .collect();

        if can_find_equalizer_cache(target, &nums, &mut cache) {
            sum_of_valid_targets += target;
        }
    }

    (sum_of_valid_targets, 0)
}

impl Solution for Day07 {
    fn run() {
        println!("Running solution for Day 7!");
        let input_file = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("inputs/day07.txt");
        let (part1, part2) = soln(&input_file);
        println!("solution: {}", part1);
    }
}
