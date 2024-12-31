#[macro_use]
extern crate lazy_static;

use std::env;
use std::time::Instant;

mod day01;
mod day02;
mod day03;
mod day04;
mod day05;
mod day06;
mod day07;
mod day08;
mod day09;
mod solution;

use crate::solution::Solution;

fn run_with_timing<T: Solution>(day: &str) {
    let start = Instant::now();
    T::run();
    let duration = start.elapsed();
    println!("{}: {:?}", day, duration);
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: cargo run -- <day>");
        return;
    }

    match args[1].as_str() {
        "day01" => run_with_timing::<day01::Day01>("day01"),
        "day02" => run_with_timing::<day02::Day02>("day02"),
        "day03" => run_with_timing::<day03::Day03>("day03"),
        "day04" => run_with_timing::<day04::Day04>("day04"),
        "day05" => run_with_timing::<day05::Day05>("day05"),
        "day06" => run_with_timing::<day06::Day06>("day06"),
        "day07" => run_with_timing::<day07::Day07>("day07"),
        "day08" => run_with_timing::<day08::Day08>("day08"),
        "day09" => run_with_timing::<day09::Day09>("day09"),
        _ => eprintln!("Day not implemented!"),
    }
}
