/**
 * CAUTION: I used LLMs to translate this from Python -> Rust
 **/
use crate::solution::Solution;
use std::fs;
use std::path::Path;

pub struct Day09;

const FREE_SPACE_CHAR: char = '.';

type DiskMap = Vec<String>;

// Function to compute the checksum of the disk map
fn compute_checksum(finalized_disk_map: &DiskMap) -> i64 {
    let mut checksum: i64 = 0;

    for (idx, value) in finalized_disk_map.iter().enumerate() {
        if *value == FREE_SPACE_CHAR.to_string() {
            continue;
        }
        if let Ok(num) = value.parse::<i64>() {
            checksum += num * idx as i64;
        }
    }
    checksum
}

fn expand_disk_map(disk_map: &str) -> DiskMap {
    let compressed_disk_map = disk_map.trim();
    let mut expanded_disk_map = Vec::new();
    let mut curr_file_id = 0;

    for (idx, char) in compressed_disk_map.chars().enumerate() {
        if let Some(count) = char.to_digit(10) {
            let count = count as usize;
            if idx % 2 == 0 {
                let file_str = curr_file_id.to_string();
                expanded_disk_map.extend(vec![file_str; count]);
                curr_file_id += 1;
            } else {
                expanded_disk_map.extend(vec![FREE_SPACE_CHAR.to_string(); count]);
            }
        }
    }

    expanded_disk_map
}

// Function to sort the disk map (part 1)
fn sort_disk_map_pt1(mut disk_map: DiskMap) -> DiskMap {
    let mut end_of_disk_map_ptr = disk_map.len() - 1;

    for idx in 0..disk_map.len() {
        if idx >= end_of_disk_map_ptr {
            break;
        }

        if disk_map[idx] == FREE_SPACE_CHAR.to_string() {
            while end_of_disk_map_ptr > idx {
                if disk_map[end_of_disk_map_ptr].parse::<i32>().is_ok() {
                    disk_map.swap(idx, end_of_disk_map_ptr);
                    end_of_disk_map_ptr -= 1;
                    break;
                }
                end_of_disk_map_ptr -= 1;
            }
        }
    }

    disk_map
}

fn soln(input_file: &Path) -> (i64, i64) {
    let compressed_disk_map = fs::read_to_string(input_file).expect("Failed to read input file");
    let expanded_disk_map = expand_disk_map(&compressed_disk_map);
    let expanded_disk_map_copy = expanded_disk_map.clone();

    let sorted_disk_map_pt1 = sort_disk_map_pt1(expanded_disk_map);
    let file_checksum_pt1 = compute_checksum(&sorted_disk_map_pt1);

    // let sorted_disk_map_pt2 = sort_disk_map_pt2(expanded_disk_map_copy);
    // let file_checksum_pt2 = compute_checksum(&sorted_disk_map_pt2);
    let file_checksum_pt2 = 0;

    (file_checksum_pt1, file_checksum_pt2)
}

impl Solution for Day09 {
    fn run() {
        println!("Running solution for Day 9!");
        let input_file = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("inputs/day09.txt");
        let (checksum_pt1, checksum_pt2) = soln(&input_file);
        println!("Part 1: {}", checksum_pt1);
        println!("Part 2: {}", checksum_pt2);
    }
}
