mod server;
mod window;
mod config;
mod api;

use config::AppConfig;
use std::path::PathBuf;

fn taupy_dist_path(custom: Option<String>) -> PathBuf {
    if let Some(path) = custom {
        return PathBuf::from(path);
    }

    let mut p = std::env::current_dir().unwrap();
    p.push("dist");
    p
}

/// Entry point exposed from the DLL.
#[no_mangle]
pub extern "C" fn LakeEngineRun() {
    let cfg = AppConfig::from_env();

    let dist = taupy_dist_path(cfg.dist.clone());
    if !cfg.external {
        server::start_http_server(dist, cfg.port);
    }

    let _ = window::open_window(&cfg);
}

