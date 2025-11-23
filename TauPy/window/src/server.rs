use std::thread;
use std::path::PathBuf;
use tiny_http::{Server, Response};

pub fn start_http_server(dist_path: PathBuf, port: u16) {
    thread::spawn(move || {
        let server = Server::http(format!("0.0.0.0:{}", port)).unwrap();

        for request in server.incoming_requests() {
            let url = request.url().trim_start_matches('/');

            let mut file_path = dist_path.clone();
            file_path.push(url);

            if url.is_empty() {
                file_path.push("index.html");
            }

            if file_path.exists() {
                let content = std::fs::read(&file_path).unwrap();
                let response = Response::from_data(content);
                request.respond(response).unwrap();
            } else {
                request.respond(Response::empty(404)).unwrap();
            }
        }
    });
}
