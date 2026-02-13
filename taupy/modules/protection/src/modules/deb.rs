use winapi::um::debugapi::IsDebuggerPresent;

fn debugger_detected() -> bool {
    unsafe { IsDebuggerPresent() != 0 }
}
