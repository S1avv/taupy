fn args_allowed() -> bool {
    let args: Vec<String> = env::args().collect();

    args.len() == 1
}