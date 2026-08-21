use std::process::Command;

/// Run a JakeFSD CLI subcommand through the Python interpreter on PATH.
fn run_jakefsd_cli(args: &[&str]) -> Result<String, String> {
    let output = Command::new("python")
        .arg("-m")
        .arg("jakefsd.cli")
        .args(args)
        .output()
        .map_err(|e| format!("failed to spawn python: {e}"))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
        Err(stderr)
    }
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn python_runtime_version() -> String {
    match run_jakefsd_cli(&["--version"]) {
        Ok(version) => version,
        Err(err) => format!("Python runtime not available: {err}"),
    }
}

#[tauri::command]
fn plan_from_intent(intent: &str) -> Result<String, String> {
    run_jakefsd_cli(&["plan", intent])
}

#[tauri::command]
fn run_pipeline(manifest_path: &str) -> Result<String, String> {
    run_jakefsd_cli(&["run", manifest_path])
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            python_runtime_version,
            plan_from_intent,
            run_pipeline
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
