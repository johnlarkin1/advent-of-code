use crate::solution::Solution;
use std::collections::HashMap;
use std::fs;
use std::path::Path;

pub struct Day01;

impl Solution for Day01 {
    fn run() {
        println!("Running solution for Day 1!");
        let mut left: Vec<i32> = Vec::new();
        let mut right: Vec<i32> = Vec::new();

        let input_file = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..") // Move up one directory
            .join("inputs/day01.txt");
        let file_content = fs::read_to_string(input_file).expect("Failed to read input file");

        // preallocation will help with perf
        let mut right_map: HashMap<i32, i32> = HashMap::with_capacity(file_content.lines().count());

        for line in file_content.lines() {
            let mut parts = line.split_whitespace();
            let a: i32 = parts.next().unwrap().parse().unwrap();
            let b: i32 = parts.next().unwrap().parse().unwrap();
            left.push(a);
            right.push(b);
            *right_map.entry(b).or_insert(0) += 1;
        }

        left.sort();
        right.sort();

        let mut list_distance_diff = 0;
        for (l, r) in left.iter().zip(right.iter()) {
            list_distance_diff += (l - r).abs();
        }

        let mut list_similarity_score = 0;
        for l in left.iter() {
            if let Some(&count) = right_map.get(l) {
                list_similarity_score += l * count;
            }
        }

        println!("day01 solution (pt1): {}", list_distance_diff);
        println!("day01 solution (pt2): {}", list_similarity_score);
    }
}
