use wry::{
    application::{
        event::{Event, StartCause, WindowEvent},
        event_loop::{ControlFlow, EventLoop},
        window::WindowBuilder,
    },
    webview::WebViewBuilder,
};
use crate::config::AppConfig;

pub fn open_window(cfg: &AppConfig) -> wry::Result<()> {
    let event_loop = EventLoop::new();

    let window = WindowBuilder::new()
        .with_title(cfg.title.clone())
        .with_inner_size(wry::application::dpi::LogicalSize::new(
            cfg.width as f64,
            cfg.height as f64,
        ))
        .build(&event_loop)?;

    let url = format!("http://localhost:{}", cfg.port);

    let _webview = WebViewBuilder::new(window)?
        .with_url(&url)?
        .build()?;

    event_loop.run(move |event, _, control_flow| {
        *control_flow = ControlFlow::Wait;

        match event {
            Event::NewEvents(StartCause::Init) =>
                {},
            Event::WindowEvent { event: WindowEvent::CloseRequested, .. } =>
                *control_flow = ControlFlow::Exit,
            _ => (),
        }
    });
}
