#[no_mangle]
pub extern "C" fn protection_init() -> i32 {
    block_output();

    if !args_allowed() {
        std::process::abort();
    }

    if debugger_detected() {
        std::process::abort();
    }

    0
}