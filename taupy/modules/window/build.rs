use std::{env, fs, path::PathBuf};

fn main() {
    println!("cargo:rerun-if-changed=build.rs");

    let out_dir = PathBuf::from(env::var("OUT_DIR").expect("OUT_DIR not set"));

    let profile_dir = out_dir
        .ancestors()
        .nth(3)
        .expect("Unexpected OUT_DIR layout – profile dir missing")
        .to_path_buf();

    let build_dir = out_dir
        .ancestors()
        .nth(2)
        .expect("Unexpected OUT_DIR layout – build dir missing");

    let target_arch = env::var("CARGO_CFG_TARGET_ARCH")
        .unwrap_or_else(|_| "x86_64".to_string());

    let arch_dir = match target_arch.as_str() {
        "x86_64" => "x64",
        "aarch64" => "arm64",
        "x86" => "x86",
        other => other,
    };

    let loader = fs::read_dir(build_dir)
        .expect("Failed to read build dir")
        .filter_map(|entry| entry.ok())
        .map(|entry| entry.path())
        .find_map(|path| {
            let name = path.file_name()?.to_string_lossy().to_string();
            if !name.starts_with("webview2-com-sys") {
                return None;
            }

            let candidate = path.join("out").join(arch_dir).join("WebView2Loader.dll");
            candidate.exists().then_some(candidate)
        })
        .or_else(|| {
            println!("cargo:warning=WebView2Loader.dll not found in build artifacts, trying prebuilt version.");
            let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
            let utils_dir = manifest_dir.join("..").join("..").join("utils");
            let preb = utils_dir.join("WebView2Loader.dll");
            preb.exists().then_some(preb)
        });

    if let Some(loader) = loader {
        let dest = profile_dir.join("WebView2Loader.dll");
        let _ = fs::copy(&loader, &dest);
    } else {
        println!("cargo:warning=WebView2Loader.dll not found; skipping copy.");
    }
}
