use clap::Parser;

#[derive(Parser, Debug)]
pub struct AppConfig {
    #[arg(long, default_value = "TauPy App")]
    pub title: String,

    #[arg(long, default_value_t = 8000)]
    pub port: u16,

    #[arg(long, default_value_t = 800)]
    pub width: u32,

    #[arg(long, default_value_t = 600)]
    pub height: u32,

    #[arg(long)]
    pub dist: Option<String>,

    #[arg(long, default_value_t = false)]
    pub external: bool,

    #[arg(long, default_value_t = false)]
    pub frameless: bool,

    #[arg(long, default_value_t = false)]
    pub transparent: bool,

    #[arg(long, default_value_t = false)]
    pub always_on_top: bool,

    #[arg(long, default_value_t = true, action = clap::ArgAction::Set)]
    pub resizable: bool,

    #[arg(long)]
    pub min_width: Option<u32>,

    #[arg(long)]
    pub min_height: Option<u32>,

    #[arg(long)]
    pub max_width: Option<u32>,

    #[arg(long)]
    pub max_height: Option<u32>,

    #[arg(long, default_value_t = false)]
    pub open_devtools: bool,
}

impl AppConfig {
    pub fn from_env() -> Self {
        use std::env;

        fn parse_u16(name: &str, default: u16) -> u16 {
            env::var(name)
                .ok()
                .and_then(|v| v.parse::<u16>().ok())
                .unwrap_or(default)
        }

        fn parse_u32(name: &str, default: u32) -> u32 {
            env::var(name)
                .ok()
                .and_then(|v| v.parse::<u32>().ok())
                .unwrap_or(default)
        }

        fn parse_bool(name: &str, default: bool) -> bool {
            env::var(name)
                .ok()
                .and_then(|v| {
                    let v_lower = v.to_ascii_lowercase();
                    match v_lower.as_str() {
                        "1" | "true" | "yes" | "on" => Some(true),
                        "0" | "false" | "no" | "off" => Some(false),
                        _ => None,
                    }
                })
                .unwrap_or(default)
        }

        fn parse_opt_u32(name: &str) -> Option<u32> {
            env::var(name).ok().and_then(|v| v.parse::<u32>().ok())
        }

        fn parse_opt_string(name: &str) -> Option<String> {
            match env::var(name) {
                Ok(v) if !v.is_empty() => Some(v),
                _ => None,
            }
        }

        AppConfig {
            title: env::var("TAUPY_WINDOW_TITLE")
                .unwrap_or_else(|_| "TauPy App".to_string()),
            port: parse_u16("TAUPY_WINDOW_PORT", 8000),
            width: parse_u32("TAUPY_WINDOW_WIDTH", 800),
            height: parse_u32("TAUPY_WINDOW_HEIGHT", 600),
            dist: parse_opt_string("TAUPY_WINDOW_DIST"),
            external: parse_bool("TAUPY_WINDOW_EXTERNAL", false),
            frameless: parse_bool("TAUPY_WINDOW_FRAMELESS", false),
            transparent: parse_bool("TAUPY_WINDOW_TRANSPARENT", false),
            always_on_top: parse_bool("TAUPY_WINDOW_ALWAYS_ON_TOP", false),
            resizable: parse_bool("TAUPY_WINDOW_RESIZABLE", true),
            min_width: parse_opt_u32("TAUPY_WINDOW_MIN_WIDTH"),
            min_height: parse_opt_u32("TAUPY_WINDOW_MIN_HEIGHT"),
            max_width: parse_opt_u32("TAUPY_WINDOW_MAX_WIDTH"),
            max_height: parse_opt_u32("TAUPY_WINDOW_MAX_HEIGHT"),
            open_devtools: parse_bool("TAUPY_WINDOW_OPEN_DEVTOOLS", false),
        }
    }
}
