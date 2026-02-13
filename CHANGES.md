# Changelog

## [0.0.6] - 2026-02-13

- perf: faster window startup by loading `LakeEngine.dll` directly via ctypes instead of spawning a subprocess.
- feat: full build pipeline support for all frontend modes (react, vanilla, python).
- fix: Nuitka onefile build now bundles `base.html` and `client.js` for python frontend mode.
- fix: Nuitka onefile build now bundles native binaries (`taupy.exe`, `WebView2Loader.dll`, `LakeEngine.dll`).
- fix: Nuitka build respects the `onefile` setting from `taupy.toml`.