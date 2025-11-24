# 📦 Changelog

## [0.0.2] — 2025-11-24

### ✨ Features

#### added hot reload support and improved dev experience

- Added full **Hot Module Reloading (HMR)** powered by `watchfiles`
- Implemented **automatic backend restart** on file changes
- Added **client-side reload event** and **error overlay** support
- Introduced `--no-window` flag for faster backend-only reload cycles

#### added DevUI

- New **DevUI banner** with clean startup output  
- Modern, human-friendly style
- Consistent formatting for:
  - App name  
  - Mode  
  - Frontend URL  
  - HMR status  

---

### 🛠️ Improvements

- Introduced the unified development workflow via `taupy dev`
- Removed the deprecated `run` command
- Improved process lifecycle and stability:
  - Added graceful shutdown on **Ctrl+C**
  - Prevented zombie WebView processes
  - Ensured clean reload flow during HMR restarts

---