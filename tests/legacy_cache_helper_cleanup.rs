use std::fs;
use std::path::Path;

fn download_module_source() -> String {
    let path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("src")
        .join("utils")
        .join("download.rs");
    fs::read_to_string(path).expect("download.rs should be readable")
}

#[test]
fn legacy_cache_helpers_are_removed() {
    let source = download_module_source();

    assert!(!source.contains("pub fn biomcp_cache_dir() -> PathBuf {"));
    assert!(!source.contains("pub fn biomcp_downloads_dir() -> PathBuf {"));
    assert!(!source.contains("pub fn cache_path(id: &str) -> PathBuf {"));
}
