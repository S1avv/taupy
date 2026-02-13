use serde::Deserialize;
use wry::application::window::Window;

#[derive(Debug, Deserialize, Clone)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum WindowCommand {
    Minimize,
    Maximize,
    ToggleMaximize,
    Restore,
    Close,
    Center,
    ToggleFullscreen,
    SetSize { width: u32, height: u32 },
    SetPosition { x: i32, y: i32 },
    SetTitle { title: String },
    Focus,
    AlwaysOnTop { enabled: bool },
    Resizable { enabled: bool },
    MinSize { width: u32, height: u32 },
    MaxSize { width: u32, height: u32 },
    ShowCursor { visible: bool },
    StartDrag,
}

pub fn handle_ipc_command(window: &Window, cmd: WindowCommand) {
    match cmd {
        WindowCommand::Minimize => {
            let _ = window.set_minimized(true);
        }
        WindowCommand::Maximize => {
            let _ = window.set_maximized(true);
        }
        WindowCommand::ToggleMaximize => {
            let current = window.is_maximized();
            let _ = window.set_maximized(!current);
        }
        WindowCommand::Restore => {
            let _ = window.set_minimized(false);
            let _ = window.set_maximized(false);
        }
        WindowCommand::Close => {
            std::process::exit(0);
        }
        WindowCommand::Center => {
            if let Some(monitor) = window.current_monitor() {
                let size = window.outer_size();
                let pos = monitor.position();
                let area = monitor.size();
                let new_x = pos.x + (area.width as i32 - size.width as i32) / 2;
                let new_y = pos.y + (area.height as i32 - size.height as i32) / 2;
                let _ = window.set_outer_position(wry::application::dpi::PhysicalPosition::new(new_x, new_y));
            }
        }
        WindowCommand::ToggleFullscreen => {
            use wry::application::window::Fullscreen;
            if window.fullscreen().is_some() {
                let _ = window.set_fullscreen(None);
            } else if let Some(monitor) = window.current_monitor() {
                let _ = window.set_fullscreen(Some(Fullscreen::Borderless(Some(monitor))));
            }
        }
        WindowCommand::SetSize { width, height } => {
            let _ = window.set_resizable(true);
            let _ = window.set_inner_size(wry::application::dpi::LogicalSize::new(width, height));
            let _ = window.set_resizable(false);
        }
        WindowCommand::SetPosition { x, y } => {
            let _ = window.set_outer_position(wry::application::dpi::PhysicalPosition::new(x, y));
        }
        WindowCommand::SetTitle { title } => {
            window.set_title(&title);
        }
        WindowCommand::Focus => {
            let _ = window.set_focus();
        }
        WindowCommand::AlwaysOnTop { enabled } => {
            let _ = window.set_always_on_top(enabled);
        }
        WindowCommand::Resizable { enabled } => {
            let _ = window.set_resizable(enabled);
        }
        WindowCommand::MinSize { width, height } => {
            let _ = window.set_min_inner_size(Some(wry::application::dpi::LogicalSize::new(width, height)));
        }
        WindowCommand::MaxSize { width, height } => {
            let _ = window.set_max_inner_size(Some(wry::application::dpi::LogicalSize::new(width, height)));
        }
        WindowCommand::ShowCursor { visible } => {
            window.set_cursor_visible(visible);
        }
        WindowCommand::StartDrag => {
            let _ = window.drag_window();
        }
    }
}
