use std::fs::OpenOptions;
use std::os::windows::io::AsRawHandle;
use winapi::um::processenv::SetStdHandle;
use winapi::um::winbase::{STD_OUTPUT_HANDLE, STD_ERROR_HANDLE};

fn block_output() {
    let nul = OpenOptions::new()
        .write(true)
        .open("NUL")
        .unwrap();

    unsafe {
        SetStdHandle(STD_OUTPUT_HANDLE, nul.as_raw_handle());
        SetStdHandle(STD_ERROR_HANDLE, nul.as_raw_handle());
    }
}