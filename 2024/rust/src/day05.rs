use crate::solution::Solution;
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

pub struct Day05;

fn fix_broken_printer_update_bubble_up(
    printer_update_list: &Vec<i32>,
    not_allowed_rules: &HashMap<i32, HashSet<i32>>,
) -> Vec<i32> {
    let mut sorted_printer_updates = Vec::new();

    for &page in printer_update_list {
        let mut inserted = false;

        for idx in 0..sorted_printer_updates.len() {
            if let Some(not_allowed_set) = not_allowed_rules.get(&sorted_printer_updates[idx]) {
                if not_allowed_set.contains(&page) {
                    sorted_printer_updates.insert(idx, page);
                    inserted = true;
                    break;
                }
            }
        }

        if !inserted {
            sorted_printer_updates.push(page);
        }
    }

    sorted_printer_updates
}

fn process_file(input_file: &Path) -> (i32, i32) {
    let mut sum_of_middle_num_for_valid_page_updates = 0;
    let mut sum_of_middle_num_for_fixed_pages = 0;
    let mut page_to_not_allowed_before_pages: HashMap<i32, HashSet<i32>> = HashMap::new();
    let file = File::open(input_file).expect("Unable to open file");
    let reader = io::BufReader::new(file);

    for line in reader.lines() {
        let line = line.unwrap();

        if line.contains('|') {
            let parts: Vec<&str> = line.split('|').collect();
            let rule = parts[0].trim().parse::<i32>().unwrap();
            let page = parts[1].trim().parse::<i32>().unwrap();

            page_to_not_allowed_before_pages
                .entry(rule)
                .or_insert_with(HashSet::new)
                .insert(page);
        } else if line.contains(',') {
            let pages_to_process: Vec<i32> = line
                .split(',')
                .map(|num| num.trim().parse::<i32>().unwrap())
                .collect();

            let length_of_update = pages_to_process.len();
            let mut seen_pages = HashSet::new();
            let mut valid_page = true;

            for &page in &pages_to_process {
                if let Some(not_allowed_pages) = page_to_not_allowed_before_pages.get(&page) {
                    if seen_pages.intersection(not_allowed_pages).next().is_some() {
                        valid_page = false;
                        break;
                    }
                }

                if !valid_page {
                    break;
                }

                seen_pages.insert(page);
            }

            if valid_page {
                sum_of_middle_num_for_valid_page_updates += pages_to_process[length_of_update / 2];
            } else {
                let corrected_list = fix_broken_printer_update_bubble_up(
                    &pages_to_process,
                    &page_to_not_allowed_before_pages,
                );
                sum_of_middle_num_for_fixed_pages += corrected_list[length_of_update / 2];
            }
        }
    }

    (
        sum_of_middle_num_for_valid_page_updates,
        sum_of_middle_num_for_fixed_pages,
    )
}

impl Solution for Day05 {
    fn run() {
        println!("Running solution for Day 5!");
        let input_file = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("inputs/day05.txt");
        let (part1, part2) = process_file(&input_file);
        println!("Sum of middle numbers for valid page updates: {}", part1);
        println!("Sum of middle numbers for fixed page updates: {}", part2);
    }
}
