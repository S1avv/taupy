use std::thread;
use std::path::PathBuf;
use tiny_http::{Server, Response, Header};
use std::ffi::OsStr;

fn content_type(path: &PathBuf) -> &'static str {
    match path.extension().and_then(OsStr::to_str).unwrap_or_default().to_ascii_lowercase().as_str() {
        "html" => "text/html; charset=utf-8",
        "htm" => "text/html; charset=utf-8",
        "js" | "mjs" => "application/javascript; charset=utf-8",
        "css" => "text/css; charset=utf-8",
        "json" => "application/json; charset=utf-8",
        "svg" => "image/svg+xml",
        "png" => "image/png",
        "jpg" | "jpeg" => "image/jpeg",
        "gif" => "image/gif",
        "webp" => "image/webp",
        _ => "application/octet-stream",
    }
}

pub fn start_http_server(dist_path: PathBuf, port: u16) {
    thread::spawn(move || {
        let Ok(server) = Server::http(format!("0.0.0.0:{}", port)) else {
            eprintln!("Failed to bind HTTP server on port {} (maybe in use).", port);
            return;
        };

        for request in server.incoming_requests() {
            let url = request.url().trim_start_matches('/');

            let mut file_path = dist_path.clone();
            file_path.push(url);

            if url.is_empty() {
                file_path.push("index.html");
            }

            if file_path.exists() {
                let content = std::fs::read(&file_path).unwrap();
                let ct = content_type(&file_path);
                let response = Response::from_data(content)
                    .with_header(Header::from_bytes(&b"Content-Type"[..], ct.as_bytes()).unwrap());
                request.respond(response).unwrap();
            } else {
                request.respond(Response::empty(404)).unwrap();
            }
        }
    });
}
