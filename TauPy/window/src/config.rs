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
}
