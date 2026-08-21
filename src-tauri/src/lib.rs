use std::process::Command;

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn python_runtime_version() -> String {
    // Try to import the jakefsd package and report its version.
    let output = Command::new("python")
        .args(["-c", "import jakefsd; print(jakefsd.__version__)"])
        .output();

    match output {
        Ok(out) if out.status.success() => {
            let version = String::from_utf8_lossy(&out.stdout).trim().to_string();
            format!("JakeFSD Python runtime: {}", version)
        }
        _ => {
            // Fallback: report the Python interpreter version.
            let output = Command::new("python").args(["--version"]).output();
            match output {
                Ok(out) if out.status.success() => {
                    let version = String::from_utf8_lossy(&out.stdout)
                        .trim()
                        .to_string();
                    if version.is_empty() {
                        // python --version writes to stderr on some platforms.
                        let err = String::from_utf8_lossy(&out.stderr).trim().to_string();
                        format!("Python: {}", err)
                    } else {
                        format!("Python: {}", version)
                    }
                }
                _ => "Python runtime not found. Make sure Python is installed and on PATH.".to_string(),
            }
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet, python_runtime_version])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
