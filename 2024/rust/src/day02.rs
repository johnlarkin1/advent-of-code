use crate::solution::Solution;
use std::fs;
use std::path::Path;

pub struct Day02;

fn is_report_safe(report: &Vec<i32>) -> bool {
    let is_increasing: bool = report[0] < report[1];
    let is_decreasing: bool = report[0] > report[1];
    if !(is_increasing || is_decreasing) {
        return false;
    }

    if report.len() < 2 {
        return false;
    }

    let min_tol = 1;
    let max_tol = 3;

    for i in 0..report.len() - 1 {
        let diff = (report[i + 1] - report[i]).abs();
        if is_increasing && report[i + 1] < report[i] {
            return false;
        }
        if is_decreasing && report[i + 1] > report[i] {
            return false;
        }
        if diff < min_tol {
            return false;
        }
        if diff > max_tol {
            return false;
        }
    }
    return true;
}

fn is_report_safe_with_one_allowed(report: Vec<i32>) -> bool {
    if is_report_safe(&report) {
        return true;
    }

    for i in 0..report.len() {
        let mut report_copy = report.clone();
        report_copy.remove(i);
        if is_report_safe(&report_copy) {
            return true;
        }
    }
    return false;
}

impl Solution for Day02 {
    fn run() {
        println!("Running solution for Day 2!");
        let input_file = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("inputs/day02.txt");

        let file_content = fs::read_to_string(input_file).expect("Failed to read input file");

        let mut safe_reports = 0;
        let mut safe_reports_with_one_allowed = 0;

        for line in file_content.lines() {
            let report: Vec<i32> = line
                .split_whitespace()
                .filter_map(|part| part.parse::<i32>().ok())
                .collect();

            if is_report_safe(&report) {
                safe_reports += 1;
            }

            if is_report_safe_with_one_allowed(report) {
                safe_reports_with_one_allowed += 1;
            }
        }

        println!("day02 solution (pt1): {}", safe_reports);
        println!("day02 solution (pt2): {}", safe_reports_with_one_allowed);
    }
}
