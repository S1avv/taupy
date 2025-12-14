# Installation

TauPy is distributed on PyPI and can be installed in seconds. Most users only need Python 3.9+ and `pip`. No Rust tool-chain is required unless you plan to contribute to the core.

## 1. Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python      | **3.9 - 3.12** | CPython or PyPy |
| pip / venv  | latest  | Recommended: `python -m pip install --upgrade pip` |
| Node & npm  | optional | Only if you want to use the React template |

> **TIP**  
> On Windows, enable long paths (`git config --system core.longpaths true`) to avoid rare build problems.

## 2. Stable release from PyPI

```bash
python -m pip install --upgrade taupy-framework
```

This installs:

* `taupy` - the Python API
* Pre-built native launcher binaries for your platform (≈5 MB)
* Command-line tool `taupy`

Verify the installation:

```bash
$ taupy --version
TauPy 0.4.0  # example
```

## 3. Install the development version (from GitHub)

If you need unreleased features:

```bash
git clone https://github.com/S1avv/taupy.git
cd taupy
python -m pip install -e .[dev]
```

## 4. Upgrading

TauPy follows semantic versioning. To upgrade to the latest compatible version:

```bash
python -m pip install --upgrade taupy-framework
```

## 5. Optional components

### React/Vite template

To scaffold a project with a React front-end you need Node >= 18 and npm >= 9:

```bash
node -v  # v20.x recommended
npm  -v  # 10.x
```

Then:

```bash
taupy new my_app --template react
cd my_app
npm install        # install front-end deps
```

### Building from source (contributors only)

The pre-built launcher is enough for application developers. If you want to hack on the Rust core:

1. Install Rust (1.74+) via [rustup](https://rustup.rs/).
2. Ensure a C tool-chain is available (e.g. `build-essential` on Linux, Xcode CLT on macOS, `msvc` on Windows).
3. From the repo root run:

   ```bash
   cargo build --release
   ```

The resulting binary will be placed in `target/release/launcher/`.

---

Having trouble? Check the [FAQ](./faq.md) or open an issue on GitHub - we are happy to help!
