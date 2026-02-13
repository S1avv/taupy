use wry::{
    application::{
        event::{Event, StartCause, WindowEvent},
        event_loop::{ControlFlow, EventLoopBuilder, EventLoopProxy},
        platform::windows::EventLoopBuilderExtWindows,
        window::WindowBuilder,
    },
    webview::WebViewBuilder,
};
use crate::config::AppConfig;
use crate::api::{handle_ipc_command, WindowCommand};
use serde_json::json;
use std::fs::OpenOptions;
use std::io::{BufRead, BufReader, Write};
use std::thread;

#[derive(Debug, Clone)]
enum UserEvent {
    Ipc(WindowCommand),
}

struct Logger {
    file: Option<std::fs::File>,
}

impl Logger {
    fn new() -> Self {
        if std::env::var_os("TAUPY_WINDOW_LOG").is_none() {
            return Logger { file: None };
        }

        let path = std::env::current_dir()
            .unwrap_or_else(|_| std::path::PathBuf::from("."))
            .join("LakeEngine.log");

        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)
            .ok();

        Logger { file }
    }

    fn log(&mut self, message: impl AsRef<str>) {
        if let Some(file) = self.file.as_mut() {
            let _ = writeln!(file, "{}", message.as_ref());
            let _ = file.flush();
        }
    }
}

pub fn open_window(cfg: &AppConfig) -> wry::Result<()> {
    let event_loop = EventLoopBuilder::<UserEvent>::with_user_event()
        .with_any_thread(true)
        .build();
    let proxy: EventLoopProxy<UserEvent> = event_loop.create_proxy();
    let mut logger = Logger::new();

    let mut builder = WindowBuilder::new()
        .with_title(cfg.title.clone())
        .with_inner_size(wry::application::dpi::LogicalSize::new(
            cfg.width as f64,
            cfg.height as f64,
        ))
        .with_decorations(!cfg.frameless)
        .with_transparent(cfg.transparent)
        .with_always_on_top(cfg.always_on_top)
        .with_resizable(cfg.resizable);

    if let (Some(w), Some(h)) = (cfg.min_width, cfg.min_height) {
        builder = builder.with_min_inner_size(wry::application::dpi::LogicalSize::new(w, h));
    }
    if let (Some(w), Some(h)) = (cfg.max_width, cfg.max_height) {
        builder = builder.with_max_inner_size(wry::application::dpi::LogicalSize::new(w, h));
    }

    let window = builder.build(&event_loop)?;

    let url = format!("http://localhost:{}", cfg.port);

    let init_script = r#"
        window.__taupyNativeEvents = [];
        window.taupyDrag = () => {
            if (window.ipc) {
                window.ipc.postMessage("drag");
            }
        };
        window.taupyNative = {
            send(cmd) {
                try { window.ipc?.postMessage(JSON.stringify(cmd)); } catch (e) { console.warn(e); }
            },
            onEvent(cb) {
                if (typeof cb === "function") window.__taupyNativeEvents.push(cb);
                return () => {
                    const idx = window.__taupyNativeEvents.indexOf(cb);
                    if (idx >= 0) window.__taupyNativeEvents.splice(idx, 1);
                };
            },

            minimize() { this.send({ type: "minimize" }); },
            maximize() { this.send({ type: "maximize" }); },
            toggleMaximize() { this.send({ type: "toggle_maximize" }); },
            restore() { this.send({ type: "restore" }); },
            close() { this.send({ type: "close_request" }); },
            center() { this.send({ type: "center" }); },
            toggleFullscreen() { this.send({ type: "toggle_fullscreen" }); },
            setSize(w, h) { this.send({ type: "set_size", width: w, height: h }); },
            setPosition(x, y) { this.send({ type: "set_position", x, y }); },
            setTitle(title) { this.send({ type: "set_title", title }); },
            focus() { this.send({ type: "focus" }); },
            alwaysOnTop(enabled=true) { this.send({ type: "always_on_top", enabled }); },
            resizable(enabled=true) { this.send({ type: "resizable", enabled }); },
            minSize(w, h) { this.send({ type: "min_size", width: w, height: h }); },
            maxSize(w, h) { this.send({ type: "max_size", width: w, height: h }); },
            showCursor(visible=true) { this.send({ type: "show_cursor", visible }); },
            grabCursor(grab=true) { this.send({ type: "grab_cursor", grab }); },
            startDrag() { this.send({ type: "start_drag" }); },
            }
        };
        window.__taupyNativeDispatch = (evt) => {
            for (const cb of window.__taupyNativeEvents) {
                try { cb(evt); } catch (e) { console.error(e); }
            }
        };
    "#;

    let webview = WebViewBuilder::new(window)?
        .with_url(&url)?
        .with_initialization_script(init_script)
        .with_devtools(cfg.open_devtools)
        .with_ipc_handler(move |win, req| {
            if req == "drag" {
                let _ = win.drag_window();
                return;
            }

            if let Ok(cmd) = serde_json::from_str::<WindowCommand>(&req) {
                handle_ipc_command(win, cmd);
                return;
            }
        })
        .build()?;

    if cfg.open_devtools {
        let _ = webview.open_devtools();
    }

    thread::spawn({
        let proxy = proxy.clone();
        move || {
            let stdin = std::io::stdin();
            let reader = BufReader::new(stdin.lock());
            for line in reader.lines() {
                if let Ok(line) = line {
                    if line.trim().is_empty() {
                        continue;
                    }
                    if let Ok(cmd) = serde_json::from_str::<WindowCommand>(&line) {
                        let _ = proxy.send_event(UserEvent::Ipc(cmd));
                    }
                }
            }
        }
    });

    logger.log(format!(
        "Launching TauPy window -> url=http://localhost:{}, external_http={}",
        cfg.port, cfg.external
    ));

    event_loop.run(move |event, _, control_flow| {
        let _ = &webview;

        *control_flow = ControlFlow::Wait;

        match event {
            Event::NewEvents(StartCause::Init) => {
                logger.log("EventLoop init");
                let _ = webview.evaluate_script(
                    &format!("window.__taupyNativeDispatch({});", json!({"type": "init"}))
                );
            },
            Event::WindowEvent { event: WindowEvent::CloseRequested, .. } => {
                logger.log("Close requested");
                let _ = webview.evaluate_script(
                    &format!("window.__taupyNativeDispatch({});", json!({"type": "close_request"}))
                );
                *control_flow = ControlFlow::Exit
            },
            Event::WindowEvent { event: WindowEvent::Focused(focused), .. } => {
                let _ = webview.evaluate_script(
                    &format!("window.__taupyNativeDispatch({});", json!({"type": "focus", "focused": focused}))
                );
            },
            Event::WindowEvent { event: WindowEvent::Resized(size), .. } => {
                let _ = webview.evaluate_script(
                    &format!("window.__taupyNativeDispatch({});", json!({"type": "resize", "width": size.width, "height": size.height}))
                );
            },
            Event::WindowEvent { event: WindowEvent::Moved(pos), .. } => {
                let _ = webview.evaluate_script(
                    &format!("window.__taupyNativeDispatch({});", json!({"type": "moved", "x": pos.x, "y": pos.y}))
                );
            },
            Event::UserEvent(UserEvent::Ipc(cmd)) => {
                let win = webview.window();
                handle_ipc_command(win, cmd);
            }
            _ => (),
        }
    });
}
