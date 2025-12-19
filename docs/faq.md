# FAQ

## Does TauPy require a Rust toolchain?
No. Prebuilt launchers are shipped for all major platforms. You only need Rust if you plan to contribute to the core or build the launcher yourself.

## Which Python versions are supported?
Python 3.10 and 3.11 are supported. Python 3.12 will be added once dependencies (e.g. Nuitka) are verified.

## Can I build a single-file executable?
Yes. Run `taupy build` in your project. The output binary bundles Python, your code, and the launcher, so end users do not need Python installed.

## How do I enable hot reload?
Use `taupy dev`. The backend watches your Python files, and the frontend reloads automatically when files change.

## Where do logs go?
CLI output goes to the terminal. For the embedded window, stdout/stderr is streamed back to the backend and printed there as well.

## Something went wrong. How can I get help?
Open an issue on GitHub with your OS, Python version, and reproduction steps: https://github.com/S1avv/taupy
