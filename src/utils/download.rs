use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use tokio::io::AsyncWriteExt;

use crate::error::BioMcpError;

pub fn biomcp_cache_dir() -> PathBuf {
    match dirs::cache_dir() {
        Some(dir) => dir.join("biomcp"),
        None => std::env::temp_dir().join("biomcp"),
    }
}

pub fn biomcp_downloads_dir() -> PathBuf {
    std::env::temp_dir().join("biomcp")
}

pub fn cache_key(id: &str) -> String {
    format!("{:x}", md5::compute(id.as_bytes()))
}

pub fn cache_path(id: &str) -> PathBuf {
    biomcp_downloads_dir().join(format!("{}.txt", cache_key(id)))
}

async fn create_unique_sibling_temp(
    path: &Path,
) -> Result<(tokio::fs::File, PathBuf), BioMcpError> {
    let Some(dir) = path.parent() else {
        return Err(BioMcpError::InvalidArgument(
            "Invalid cache path (no parent directory)".into(),
        ));
    };
    tokio::fs::create_dir_all(dir).await?;

    let stem = path
        .file_name()
        .and_then(|value| value.to_str())
        .unwrap_or("tmp");
    let seed = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or_default();
    for attempt in 0..32_u32 {
        let candidate = dir.join(format!(
            ".{stem}.{}.tmp",
            seed.saturating_add(attempt as u128)
        ));
        match tokio::fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&candidate)
            .await
        {
            Ok(file) => return Ok((file, candidate)),
            Err(err) if err.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(err) => return Err(err.into()),
        }
    }

    Err(BioMcpError::Io(std::io::Error::new(
        std::io::ErrorKind::AlreadyExists,
        "Unable to allocate secure temporary cache file",
    )))
}

async fn remove_temp_if_present(path: &Path) {
    let _ = tokio::fs::remove_file(path).await;
}

async fn existing_file_matches(path: &Path, content: &[u8]) -> bool {
    matches!(tokio::fs::read(path).await, Ok(existing) if existing == content)
}

async fn existing_regular_file(path: &Path) -> bool {
    matches!(tokio::fs::metadata(path).await, Ok(metadata) if metadata.is_file())
}

pub async fn write_atomic_bytes(path: &Path, content: &[u8]) -> Result<(), BioMcpError> {
    let (mut file, tmp_path) = create_unique_sibling_temp(path).await?;
    file.write_all(content).await?;
    file.flush().await?;
    file.sync_all().await?;
    drop(file);

    match tokio::fs::rename(&tmp_path, path).await {
        Ok(()) => Ok(()),
        Err(_err) if existing_file_matches(path, content).await => {
            remove_temp_if_present(&tmp_path).await;
            Ok(())
        }
        Err(err) => {
            if !existing_regular_file(path).await {
                remove_temp_if_present(&tmp_path).await;
                return Err(err.into());
            }

            match tokio::fs::remove_file(path).await {
                Ok(()) => {}
                Err(remove_err) if remove_err.kind() == std::io::ErrorKind::NotFound => {}
                Err(remove_err) => {
                    remove_temp_if_present(&tmp_path).await;
                    return Err(remove_err.into());
                }
            }

            match tokio::fs::rename(&tmp_path, path).await {
                Ok(()) => Ok(()),
                Err(_retry_err) if existing_file_matches(path, content).await => {
                    remove_temp_if_present(&tmp_path).await;
                    Ok(())
                }
                Err(retry_err) => {
                    remove_temp_if_present(&tmp_path).await;
                    Err(retry_err.into())
                }
            }
        }
    }
}

pub async fn save_atomic(id: &str, content: &str) -> Result<PathBuf, BioMcpError> {
    let path = cache_path(id);
    if tokio::fs::metadata(&path).await.is_ok() {
        return Ok(path);
    }

    write_atomic_bytes(&path, content.as_bytes()).await?;
    Ok(path)
}

#[cfg(test)]
mod tests {
    use std::path::{Path, PathBuf};
    use std::time::{SystemTime, UNIX_EPOCH};

    use super::write_atomic_bytes;

    struct TempDirGuard {
        path: PathBuf,
    }

    impl TempDirGuard {
        fn new(label: &str) -> Self {
            let stamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_nanos();
            let path = std::env::temp_dir().join(format!(
                "biomcp-download-test-{label}-{}-{stamp}",
                std::process::id()
            ));
            std::fs::create_dir_all(&path).expect("temp dir should be created");
            Self { path }
        }

        fn path(&self) -> &Path {
            &self.path
        }
    }

    impl Drop for TempDirGuard {
        fn drop(&mut self) {
            let _ = std::fs::remove_dir_all(&self.path);
        }
    }

    #[tokio::test]
    async fn write_atomic_bytes_replaces_existing_file_contents() {
        let root = TempDirGuard::new("replace-existing");
        let target = root.path().join("ema.json");
        std::fs::write(&target, b"old").expect("existing file should be writable");

        write_atomic_bytes(&target, b"new")
            .await
            .expect("atomic write should replace existing file");

        let updated = std::fs::read(&target).expect("updated file should be readable");
        assert_eq!(updated, b"new");
    }

    #[tokio::test]
    async fn write_atomic_bytes_errors_for_non_file_destination() {
        let root = TempDirGuard::new("destination-directory");
        let target = root.path().join("ema.json");
        std::fs::create_dir_all(&target).expect("target directory should be created");

        let err = write_atomic_bytes(&target, b"new")
            .await
            .expect_err("directory destination should fail");
        assert!(
            err.to_string().contains("Is a directory")
                || err.to_string().contains("directory")
                || err.to_string().contains("Access is denied"),
            "unexpected error: {err}"
        );
    }
}
