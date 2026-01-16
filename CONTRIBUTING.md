# Contributing to TauPy

We're thrilled you're interested in contributing to the TauPy project! Your help is invaluable. This guide will help you get started and make your contributions.

## 1. How to Contribute

There are many ways to contribute to TauPy:

*   **Report Bugs**: If you find a bug, please report it.
*   **Suggest Enhancements**: Have an idea for a new feature or improvement? Let us know!
*   **Write Code**: Submit bug fixes, implement new features, or improve existing code.
*   **Improve Documentation**: Help us make the documentation more comprehensive and understandable.
*   **Answer Questions**: Help other users in the community.

## 2. Getting Started

Before you can contribute code, you'll need to set up your development environment.

### Prerequisites

Make sure you have the following installed:
*   **Python 3.10+**
*   **Poetry** (for Python dependency management)
*   **Rust toolchain** (for building the WebView launcher)
*   **Node.js and npm/yarn** (if you're working with the React UI)
*   **WebView2 Runtime** (for Windows)

### Setting up Your Development Environment

1.  **Fork the Repository**: Click the "Fork" button in the top right corner of the GitHub page.
2.  **Clone Your Fork**:
    ```bash
    git clone https://github.com/S1avv/taupy.git
    cd taupy
    ```
3.  **Install Python Dependencies**:
    ```bash
    poetry install
    ```
4.  **Install Rust Dependencies** (if you plan to work with the launcher):
    ```bash
    # Navigate to the launcher directory
    cd launcher
    # Install necessary Rust components
    rustup target add x86_64-pc-windows-msvc # for Windows
    # Return to the root directory
    cd ..
    ```

## 3. Reporting Bugs

If you find a bug, please open a [GitHub Issue](https://github.com/S1avv/TauPy/issues). When creating a bug report, please include the following information:

*   **A clear and concise description of the bug.**
*   **Steps to reproduce**: How can we reproduce the bug?
*   **Expected behavior**: What did you expect to happen?
*   **Actual behavior**: What actually happened?
*   **Screenshots or videos** (if applicable).
*   **Your environment**:
    *   TauPy version
    *   Python version
    *   Operating system
    *   Any other relevant details.

## 4. Suggesting Enhancements

Have an idea for a new feature or improvement? Open a [GitHub Issue](https://github.com/S1avv/TauPy/issues) and use the "Feature request" template. Please describe:

*   **The problem you're trying to solve.**
*   **Your proposed solution.**
*   **Examples of usage** (if applicable).
*   **Alternative solutions** you've considered.

## 5. Your First Code Contribution

If you're new to the project, consider looking for tasks labeled `good first issue` or `help wanted` in the [Issue Tracker](https://github.com/S1avv/TauPy/issues).

## 6. Pull Request Guidelines

1.  **Create a new branch**:
    ```bash
    git checkout -b feature/your-feature-name
    # or
    git checkout -b bugfix/description-of-fix
    ```
2.  **Make your changes**: Write code, add tests, and update documentation.
3.  **Validate your code**: Ensure your code adheres to the project's style and all tests pass.
4.  **Commit your changes**: Write clear and descriptive commit messages.
5.  **Push your changes to your fork**:
    ```bash
    git push origin feature/your-feature-name
    ```
6.  **Open a Pull Request**: Go to your fork's GitHub page and click the "New pull request" button.

When creating a Pull Request, please include:

*   **A clear description of the changes.**
*   **Links to relevant Issues** (e.g., `Fixes #123`).
*   **Test results.**
*   **Screenshots or GIFs** (if the changes affect the UI).

## 7. Development Setup

### Running the Application in Development Mode

```bash
poetry run taupy dev
```

### Building the Launcher (Rust)

```bash
cd launcher
cargo build --release
```

### Building the Application (Nuitka)

```bash
poetry run taupy build
```

## 8. Testing

We use `pytest` for testing. To run tests:

```bash
poetry run pytest
```

Please ensure all tests pass before submitting a Pull Request. If you're adding a new feature or fixing a bug, please write corresponding tests.

## 9. Coding Style

*   **Python**: We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/). Use `black` for formatting and `flake8` for linting.
    ```bash
    poetry run black .
    poetry run flake8 .
    ```
*   **Rust**: We follow standard Rust guidelines. Use `rustfmt` for formatting.
    ```bash
    cargo fmt
    ```
*   **JavaScript/TypeScript**: We follow standard guidelines. Use `prettier` and `eslint`.

## 10. Commit Messages

Please write clear and descriptive commit messages. We recommend using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for consistency.

Examples:
*   `feat: add new feature X`
*   `fix: fix bug in component Y`
*   `docs: update documentation for Z`
*   `refactor: refactor module A`
*   `test: add tests for B`

Thank you for your contribution!
