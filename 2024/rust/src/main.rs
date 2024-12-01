use std::env;
use std::time::Instant;

mod day01;
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
        _ => eprintln!("Day not implemented!"),
    }
}
