use clap::Subcommand;

use crate::error::BioMcpError;

#[derive(Subcommand, Debug, Clone, Copy, PartialEq, Eq)]
pub enum CacheCommand {
    /// Print the managed HTTP cache path as plain text (`--json` is ignored)
    #[command(long_about = "\
Print the managed HTTP cache path as plain text.

This command is read-only and prints `<resolved cache_root>/http`.
The global `--json` flag is ignored for this command and output stays plain text.
This command family is CLI-only because it reveals workstation-local filesystem paths.")]
    Path,
}

/// Render the managed HTTP cache path without creating or migrating cache directories.
///
/// # Errors
///
/// Returns an error if cache configuration resolution fails.
pub fn render_path() -> Result<String, BioMcpError> {
    let config = crate::cache::resolve_cache_config()?;
    Ok(config.cache_root.join("http").display().to_string())
}

#[cfg(test)]
mod tests {
    use std::path::{Path, PathBuf};
    use std::time::{SystemTime, UNIX_EPOCH};

    use tokio::sync::MutexGuard;

    use super::render_path;
    use crate::error::BioMcpError;

    fn env_lock() -> MutexGuard<'static, ()> {
        crate::test_support::env_lock().blocking_lock()
    }

    struct EnvVarGuard {
        name: &'static str,
        previous: Option<String>,
    }

    impl Drop for EnvVarGuard {
        fn drop(&mut self) {
            // Safety: tests serialize environment mutation with `env_lock()`.
            unsafe {
                match &self.previous {
                    Some(value) => std::env::set_var(self.name, value),
                    None => std::env::remove_var(self.name),
                }
            }
        }
    }

    fn set_env_var(name: &'static str, value: Option<&str>) -> EnvVarGuard {
        let previous = std::env::var(name).ok();
        // Safety: tests serialize environment mutation with `env_lock()`.
        unsafe {
            match value {
                Some(value) => std::env::set_var(name, value),
                None => std::env::remove_var(name),
            }
        }
        EnvVarGuard { name, previous }
    }

    struct TempDirGuard {
        path: PathBuf,
    }

    impl TempDirGuard {
        fn new(label: &str) -> Self {
            let suffix = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_nanos();
            let path = std::env::temp_dir().join(format!(
                "biomcp-cache-path-{label}-{}-{suffix}",
                std::process::id()
            ));
            std::fs::create_dir_all(&path).expect("create temp dir");
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

    #[test]
    fn default_path_uses_xdg_cache_home_http_subdir() {
        let _lock = env_lock();
        let root = TempDirGuard::new("default");
        let cache_home = root.path().join("cache-home");
        let config_home = root.path().join("config-home");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_home).expect("create config home");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var("XDG_CONFIG_HOME", Some(&config_home.to_string_lossy()));
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", None);
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let rendered = render_path().expect("default cache path should render");
        assert_eq!(
            rendered,
            cache_home.join("biomcp").join("http").display().to_string()
        );
    }

    #[test]
    fn env_override_uses_biomcp_cache_dir_http_subdir() {
        let _lock = env_lock();
        let root = TempDirGuard::new("env");
        let cache_home = root.path().join("cache-home");
        let config_home = root.path().join("config-home");
        let env_cache = root.path().join("env-cache");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_home).expect("create config home");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var("XDG_CONFIG_HOME", Some(&config_home.to_string_lossy()));
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", Some(&env_cache.to_string_lossy()));
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let rendered = render_path().expect("env cache path should render");
        assert_eq!(rendered, env_cache.join("http").display().to_string());
    }

    #[test]
    fn cache_toml_override_uses_configured_http_subdir() {
        let _lock = env_lock();
        let root = TempDirGuard::new("toml");
        let cache_home = root.path().join("cache-home");
        let config_dir = root.path().join("config-home").join("biomcp");
        let configured_root = root.path().join("configured-cache");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_dir).expect("create config dir");
        std::fs::write(
            config_dir.join("cache.toml"),
            format!("[cache]\ndir = \"{}\"\n", configured_root.display()),
        )
        .expect("write cache.toml");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var(
            "XDG_CONFIG_HOME",
            Some(&config_dir.parent().expect("config home").to_string_lossy()),
        );
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", None);
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let rendered = render_path().expect("config cache path should render");
        assert_eq!(rendered, configured_root.join("http").display().to_string());
    }

    #[test]
    fn relative_cache_toml_path_stays_relative() {
        let _lock = env_lock();
        let root = TempDirGuard::new("relative");
        let cache_home = root.path().join("cache-home");
        let config_dir = root.path().join("config-home").join("biomcp");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_dir).expect("create config dir");
        std::fs::write(
            config_dir.join("cache.toml"),
            "[cache]\ndir = \"relative-cache\"\n",
        )
        .expect("write cache.toml");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var(
            "XDG_CONFIG_HOME",
            Some(&config_dir.parent().expect("config home").to_string_lossy()),
        );
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", None);
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let rendered = render_path().expect("relative cache path should render");
        assert_eq!(
            rendered,
            PathBuf::from("relative-cache/http").display().to_string()
        );
    }

    #[test]
    fn malformed_cache_config_propagates_existing_error() {
        let _lock = env_lock();
        let root = TempDirGuard::new("invalid");
        let cache_home = root.path().join("cache-home");
        let config_dir = root.path().join("config-home").join("biomcp");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_dir).expect("create config dir");
        std::fs::write(config_dir.join("cache.toml"), "[cache\nmax_size = 1\n")
            .expect("write invalid cache.toml");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var(
            "XDG_CONFIG_HOME",
            Some(&config_dir.parent().expect("config home").to_string_lossy()),
        );
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", None);
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let err = render_path().expect_err("invalid cache config should fail");
        let message = err.to_string();
        assert!(matches!(err, BioMcpError::InvalidArgument(_)));
        assert!(message.contains("cache.toml"));
    }

    #[test]
    fn render_path_does_not_create_http_or_root_directories() {
        let _lock = env_lock();
        let root = TempDirGuard::new("no-create");
        let cache_home = root.path().join("cache-home");
        let config_home = root.path().join("config-home");
        let env_cache = root.path().join("env-cache");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_home).expect("create config home");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var("XDG_CONFIG_HOME", Some(&config_home.to_string_lossy()));
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", Some(&env_cache.to_string_lossy()));
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let rendered = render_path().expect("cache path should render");
        assert_eq!(rendered, env_cache.join("http").display().to_string());
        assert!(!env_cache.exists());
        assert!(!env_cache.join("http").exists());
    }

    #[test]
    fn render_path_does_not_migrate_legacy_http_cacache_directory() {
        let _lock = env_lock();
        let root = TempDirGuard::new("no-migrate");
        let cache_home = root.path().join("cache-home");
        let config_home = root.path().join("config-home");
        let env_cache = root.path().join("env-cache");
        let legacy = env_cache.join("http-cacache");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_home).expect("create config home");
        std::fs::create_dir_all(&legacy).expect("create legacy cache dir");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var("XDG_CONFIG_HOME", Some(&config_home.to_string_lossy()));
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", Some(&env_cache.to_string_lossy()));
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let rendered = render_path().expect("cache path should render");
        assert_eq!(rendered, env_cache.join("http").display().to_string());
        assert!(legacy.exists());
        assert!(!env_cache.join("http").exists());
    }
}
