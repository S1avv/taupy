#![cfg_attr(target_os = "windows", windows_subsystem = "windows")]

mod server;
mod window;
mod config;
mod api;

use clap::Parser;
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

fn main() -> wry::Result<()> {
    let cfg = AppConfig::parse();

    let dist = taupy_dist_path(cfg.dist.clone());
    if !cfg.external {
        server::start_http_server(dist, cfg.port);
    }

    window::open_window(&cfg)?;

    Ok(())
}
