use crate::solution::Solution;
use regex::Regex;
use std::fs;
use std::path::Path;

pub struct Day03;

fn extract_and_multiple_pt1_iter(entire_input: &str) -> i32 {
    let mut total = 0;
    for i in 0..entire_input.len() - 3 {
        if &entire_input[i..i + 3] == "mul" {
            let x_start = i + 4;
            let x_end = x_start + entire_input[x_start..].find(',').unwrap();
            let x = entire_input[x_start..x_end].parse::<i32>();

            let y_start = x_end + 1;
            let y_end = y_start + entire_input[y_start..].find(')').unwrap();
            let y = entire_input[y_start..y_end].parse::<i32>();

            if x.is_err() || y.is_err() {
                continue;
            }

            total += x.unwrap() * y.unwrap();
        }
    }
    total
}

fn extract_and_multiple_pt2_iter(entire_input: &str) -> i32 {
    let mut are_we_live = true;
    let mut total = 0;
    for i in 0..entire_input.len() - 3 {
        if &entire_input[i..i + 3] == "do(" {
            are_we_live = true;
        } else if &entire_input[i..i + 3] == "don" {
            are_we_live = false;
        } else if &entire_input[i..i + 3] == "mul" && are_we_live {
            let x_start = i + 4;
            let x_end = x_start + entire_input[x_start..].find(',').unwrap();
            let maybe_x = entire_input[x_start..x_end].parse::<i32>();

            let y_start = x_end + 1;
            let y_end = y_start + entire_input[y_start..].find(')').unwrap();
            let maybe_y = entire_input[y_start..y_end].parse::<i32>();

            if let (Ok(x), Ok(y)) = (maybe_x, maybe_y) {
                total += x * y;
            }
        }
    }
    total
}

fn extract_and_multiple_pt1_regex(entire_input: &str) -> i32 {
    let mut total = 0;
    let re = regex::Regex::new(r"mul\((\d{1,3}),(\d{1,3})\)").unwrap();

    for cap in re.captures_iter(entire_input) {
        let x = cap[1].parse::<i32>().unwrap();
        let y = cap[2].parse::<i32>().unwrap();
        total += x * y;
    }
    total
}

fn extract_and_multiple_pt2_regex(entire_input: &str) -> i32 {
    let mut total = 0;
    let mut are_we_live = true;

    let re = regex::Regex::new(r"(do\(\)|don't\(\)|mul\((\d{1,3}),(\d{1,3})\))").unwrap();

    for cap in re.captures_iter(entire_input) {
        let full_match = &cap[1];
        if full_match == "do()" {
            are_we_live = true;
        } else if full_match == "don't()" {
            are_we_live = false;
        } else if are_we_live {
            if let (Some(x_match), Some(y_match)) = (cap.get(2), cap.get(3)) {
                let x = x_match.as_str().parse::<i32>().unwrap();
                let y = y_match.as_str().parse::<i32>().unwrap();
                total += x * y;
            }
        }
    }
    total
}

impl Solution for Day03 {
    fn run() {
        println!("Running solution for Day 3!");
        let input_file = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("inputs/day03.txt");

        let file_content = fs::read_to_string(input_file).expect("Failed to read input file");

        let rez = extract_and_multiple_pt1_iter(&file_content);
        let rez2 = extract_and_multiple_pt2_iter(&file_content);
        println!("day03 solution (pt1): {}", rez);
        println!("day03 solution (pt2): {}", rez2);
    }
}
