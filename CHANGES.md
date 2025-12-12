# Changelog

## [0.0.2] – 2025-12-12

### Added
- Rust launcher IPC bridge: Python now controls window commands (minimize, maximize/toggle, resize, drag) via stdin/stdout.
- Auto dev/prod switching: `App` selects external HTTP + port 5173 in dev and bundled `dist/` on port 8000 in prod unless overridden by env vars.
- Front-end first build: `taupy build` compiles the React/Vite front-end before bundling the Python backend.

### Fixed
- HMR port freeing skips killing the current process and ignores bogus `netstat` PIDs.
- Launcher HTTP server fails gracefully if the port is already in use.

### Changed
- Window commands always forward through Python to the launcher (stdin) with WebSocket as fallback.
- Custom title bar updated for frameless mode with native actions routed through Python/launcher.
