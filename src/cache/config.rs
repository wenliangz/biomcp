use std::path::PathBuf;
use std::time::Duration;

use serde::Deserialize;

use crate::error::BioMcpError;

const DEFAULT_MAX_SIZE: u64 = 10_000_000_000;
const DEFAULT_MAX_AGE_SECS: u64 = 86_400;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum ConfigOrigin {
    Env,
    File,
    Default,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) struct CacheConfigOrigins {
    pub(crate) cache_root: ConfigOrigin,
    pub(crate) max_size: ConfigOrigin,
    pub(crate) max_age: ConfigOrigin,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) struct ResolvedCacheConfig {
    pub(crate) cache_root: PathBuf,
    pub(crate) max_size: u64,
    pub(crate) max_age: Duration,
    pub(crate) origins: CacheConfigOrigins,
}

pub(crate) type CacheConfig = ResolvedCacheConfig;

#[derive(Debug, Deserialize, Default)]
#[serde(deny_unknown_fields)]
struct CacheToml {
    #[serde(default)]
    cache: CacheTomlSection,
}

#[derive(Debug, Deserialize, Default)]
#[serde(deny_unknown_fields)]
struct CacheTomlSection {
    dir: Option<String>,
    max_size: Option<u64>,
    max_age_secs: Option<u64>,
}

pub(crate) fn resolve_cache_config() -> Result<CacheConfig, BioMcpError> {
    let env_dir = std::env::var("BIOMCP_CACHE_DIR").ok();
    let env_max_size = std::env::var("BIOMCP_CACHE_MAX_SIZE").ok();
    let default_cache_root = default_cache_root();
    let config_path = config_file_path();
    let toml_content = match config_path.as_deref() {
        Some(path) => read_cache_toml(path)?,
        None => None,
    };

    resolve_cache_config_with_source(
        env_dir.as_deref(),
        env_max_size.as_deref(),
        toml_content.as_deref(),
        default_cache_root,
        config_path.as_deref(),
    )
}

fn resolve_cache_config_from_parts(
    env_dir: Option<&str>,
    env_max_size: Option<&str>,
    toml_content: Option<&str>,
    default_cache_root: PathBuf,
) -> Result<CacheConfig, BioMcpError> {
    resolve_cache_config_with_source(
        env_dir,
        env_max_size,
        toml_content,
        default_cache_root,
        None,
    )
}

fn default_cache_root() -> PathBuf {
    dirs::cache_dir()
        .unwrap_or_else(std::env::temp_dir)
        .join("biomcp")
}

fn config_file_path() -> Option<PathBuf> {
    dirs::config_dir().map(|dir| dir.join("biomcp").join("cache.toml"))
}

fn resolve_cache_config_with_source(
    env_dir: Option<&str>,
    env_max_size: Option<&str>,
    toml_content: Option<&str>,
    default_cache_root: PathBuf,
    config_path: Option<&std::path::Path>,
) -> Result<CacheConfig, BioMcpError> {
    let CacheToml {
        cache:
            CacheTomlSection {
                dir: toml_dir,
                max_size: toml_max_size,
                max_age_secs: toml_max_age_secs,
            },
    } = parse_cache_toml(toml_content, config_path)?;

    let (cache_root, cache_root_origin) = if let Some(dir) = normalize_env_value(env_dir) {
        (PathBuf::from(dir), ConfigOrigin::Env)
    } else if let Some(dir) = parse_toml_dir(toml_dir.as_deref(), config_path)? {
        (dir, ConfigOrigin::File)
    } else {
        (default_cache_root, ConfigOrigin::Default)
    };

    let (max_size, max_size_origin) = if let Some(size) = parse_env_max_size(env_max_size)? {
        (size, ConfigOrigin::Env)
    } else if let Some(size) =
        parse_toml_positive_u64(toml_max_size, "[cache].max_size", config_path)?
    {
        (size, ConfigOrigin::File)
    } else {
        (DEFAULT_MAX_SIZE, ConfigOrigin::Default)
    };

    let (max_age_secs, max_age_origin) = if let Some(age_secs) =
        parse_toml_positive_u64(toml_max_age_secs, "[cache].max_age_secs", config_path)?
    {
        (age_secs, ConfigOrigin::File)
    } else {
        (DEFAULT_MAX_AGE_SECS, ConfigOrigin::Default)
    };

    Ok(ResolvedCacheConfig {
        cache_root,
        max_size,
        max_age: Duration::from_secs(max_age_secs),
        origins: CacheConfigOrigins {
            cache_root: cache_root_origin,
            max_size: max_size_origin,
            max_age: max_age_origin,
        },
    })
}

fn read_cache_toml(path: &std::path::Path) -> Result<Option<String>, BioMcpError> {
    match std::fs::read_to_string(path) {
        Ok(content) => Ok(Some(content)),
        Err(err) if err.kind() == std::io::ErrorKind::NotFound => Ok(None),
        Err(err) => Err(BioMcpError::Io(std::io::Error::new(
            err.kind(),
            format!("failed to read {}: {}", path.display(), err),
        ))),
    }
}

fn parse_cache_toml(
    toml_content: Option<&str>,
    config_path: Option<&std::path::Path>,
) -> Result<CacheToml, BioMcpError> {
    let Some(toml_content) = toml_content else {
        return Ok(CacheToml::default());
    };

    if toml_content.trim().is_empty() {
        return Ok(CacheToml::default());
    }

    toml::from_str::<CacheToml>(toml_content)
        .map_err(|err| invalid_config(config_path, format!("failed to parse cache config: {err}")))
}

fn normalize_env_value(value: Option<&str>) -> Option<&str> {
    value.map(str::trim).filter(|value| !value.is_empty())
}

fn parse_env_max_size(value: Option<&str>) -> Result<Option<u64>, BioMcpError> {
    let Some(value) = normalize_env_value(value) else {
        return Ok(None);
    };

    let parsed = value.parse::<u64>().map_err(|_| {
        BioMcpError::InvalidArgument(format!(
            "BIOMCP_CACHE_MAX_SIZE must be a positive integer number of bytes: got '{value}'"
        ))
    })?;

    if parsed == 0 {
        return Err(BioMcpError::InvalidArgument(
            "BIOMCP_CACHE_MAX_SIZE must be greater than 0".into(),
        ));
    }

    Ok(Some(parsed))
}

fn parse_toml_dir(
    value: Option<&str>,
    config_path: Option<&std::path::Path>,
) -> Result<Option<PathBuf>, BioMcpError> {
    let Some(value) = value else {
        return Ok(None);
    };

    let trimmed = value.trim();
    if trimmed.is_empty() {
        return Err(invalid_config(
            config_path,
            "[cache].dir must not be blank".into(),
        ));
    }

    Ok(Some(PathBuf::from(trimmed)))
}

fn parse_toml_positive_u64(
    value: Option<u64>,
    field_name: &str,
    config_path: Option<&std::path::Path>,
) -> Result<Option<u64>, BioMcpError> {
    match value {
        Some(0) => Err(invalid_config(
            config_path,
            format!("{field_name} must be greater than 0"),
        )),
        Some(value) => Ok(Some(value)),
        None => Ok(None),
    }
}

fn invalid_config(config_path: Option<&std::path::Path>, message: String) -> BioMcpError {
    BioMcpError::InvalidArgument(format!("{}: {message}", config_source_label(config_path)))
}

fn config_source_label(config_path: Option<&std::path::Path>) -> String {
    config_path
        .map(|path| path.display().to_string())
        .unwrap_or_else(|| "cache.toml".to_string())
}

#[cfg(test)]
mod tests {
    use super::{
        CacheConfig, CacheConfigOrigins, ConfigOrigin, DEFAULT_MAX_AGE_SECS, DEFAULT_MAX_SIZE,
        default_cache_root, resolve_cache_config, resolve_cache_config_from_parts,
    };
    use crate::error::BioMcpError;
    use std::path::{Path, PathBuf};
    use std::time::{Duration, SystemTime, UNIX_EPOCH};
    use tokio::sync::MutexGuard;

    fn env_lock() -> MutexGuard<'static, ()> {
        crate::test_support::env_lock().blocking_lock()
    }

    struct EnvVarGuard {
        name: &'static str,
        previous: Option<String>,
    }

    impl Drop for EnvVarGuard {
        fn drop(&mut self) {
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
                "biomcp-cache-config-{label}-{}-{suffix}",
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

    fn default_config_with_root(root: impl Into<PathBuf>) -> CacheConfig {
        CacheConfig {
            cache_root: root.into(),
            max_size: DEFAULT_MAX_SIZE,
            max_age: Duration::from_secs(DEFAULT_MAX_AGE_SECS),
            origins: CacheConfigOrigins {
                cache_root: ConfigOrigin::Default,
                max_size: ConfigOrigin::Default,
                max_age: ConfigOrigin::Default,
            },
        }
    }

    fn assert_invalid_argument_contains(err: BioMcpError, expected: &[&str]) {
        let message = err.to_string();
        assert!(matches!(err, BioMcpError::InvalidArgument(_)));
        for needle in expected {
            assert!(
                message.contains(needle),
                "expected error message to contain {needle:?}, got: {message}"
            );
        }
    }

    #[test]
    fn defaults_when_no_env_or_file_uses_default_cache_config() {
        let default_root = PathBuf::from("/tmp/default-cache");
        let config =
            resolve_cache_config_from_parts(None, None, None, default_root.clone()).expect("ok");
        assert_eq!(config, default_config_with_root(default_root));
    }

    #[test]
    fn env_cache_dir_overrides_file_and_default() {
        let default_root = PathBuf::from("/tmp/default-cache");
        let config = resolve_cache_config_from_parts(
            Some("  /env-cache  "),
            None,
            Some("[cache]\ndir = \"/file-cache\"\n"),
            default_root,
        )
        .expect("ok");
        assert_eq!(config.cache_root, PathBuf::from("/env-cache"));
        assert_eq!(config.origins.cache_root, ConfigOrigin::Env);
    }

    #[test]
    fn env_max_size_overrides_file_and_default() {
        let config = resolve_cache_config_from_parts(
            None,
            Some(" 5000 "),
            Some("[cache]\nmax_size = 42\n"),
            PathBuf::from("/tmp/default-cache"),
        )
        .expect("ok");
        assert_eq!(config.max_size, 5_000);
        assert_eq!(config.origins.max_size, ConfigOrigin::Env);
    }

    #[test]
    fn toml_dir_overrides_default() {
        let config = resolve_cache_config_from_parts(
            None,
            None,
            Some("[cache]\ndir = \"relative-cache\"\n"),
            PathBuf::from("/tmp/default-cache"),
        )
        .expect("ok");
        assert_eq!(config.cache_root, PathBuf::from("relative-cache"));
        assert_eq!(config.origins.cache_root, ConfigOrigin::File);
    }

    #[test]
    fn toml_max_size_overrides_default() {
        let config = resolve_cache_config_from_parts(
            None,
            None,
            Some("[cache]\nmax_size = 1234\n"),
            PathBuf::from("/tmp/default-cache"),
        )
        .expect("ok");
        assert_eq!(config.max_size, 1_234);
        assert_eq!(config.origins.max_size, ConfigOrigin::File);
    }

    #[test]
    fn toml_max_age_overrides_default() {
        let config = resolve_cache_config_from_parts(
            None,
            None,
            Some("[cache]\nmax_age_secs = 172800\n"),
            PathBuf::from("/tmp/default-cache"),
        )
        .expect("ok");
        assert_eq!(config.max_age, Duration::from_secs(172_800));
        assert_eq!(config.origins.max_age, ConfigOrigin::File);
    }

    #[test]
    fn origins_track_mixed_precedence_without_max_age_env_override() {
        let config = resolve_cache_config_from_parts(
            Some(" /env-cache "),
            None,
            Some("[cache]\nmax_size = 1234\nmax_age_secs = 7200\n"),
            PathBuf::from("/tmp/default-cache"),
        )
        .expect("ok");
        assert_eq!(
            config.origins,
            CacheConfigOrigins {
                cache_root: ConfigOrigin::Env,
                max_size: ConfigOrigin::File,
                max_age: ConfigOrigin::File,
            }
        );
    }

    #[test]
    fn default_origins_are_reported_when_values_fall_through() {
        let config = resolve_cache_config_from_parts(
            Some("   "),
            Some("   "),
            Some("# empty cache section\n"),
            PathBuf::from("/tmp/default-cache"),
        )
        .expect("ok");
        assert_eq!(
            config.origins,
            CacheConfigOrigins {
                cache_root: ConfigOrigin::Default,
                max_size: ConfigOrigin::Default,
                max_age: ConfigOrigin::Default,
            }
        );
    }

    #[test]
    fn invalid_env_size_returns_error() {
        let err =
            resolve_cache_config_from_parts(None, Some("foo"), None, PathBuf::from("/tmp/default"))
                .expect_err("invalid env size should fail");
        assert_invalid_argument_contains(err, &["BIOMCP_CACHE_MAX_SIZE", "foo"]);
    }

    #[test]
    fn zero_env_size_returns_error() {
        let err =
            resolve_cache_config_from_parts(None, Some("0"), None, PathBuf::from("/tmp/default"))
                .expect_err("zero env size should fail");
        assert_invalid_argument_contains(err, &["BIOMCP_CACHE_MAX_SIZE", "greater than 0"]);
    }

    #[test]
    fn invalid_toml_syntax_returns_error() {
        let err = resolve_cache_config_from_parts(
            None,
            None,
            Some("[cache\nmax_size = 1"),
            PathBuf::from("/tmp/default"),
        )
        .expect_err("invalid toml should fail");
        assert_invalid_argument_contains(err, &["cache"]);
    }

    #[test]
    fn unknown_toml_field_returns_error() {
        let err = resolve_cache_config_from_parts(
            None,
            None,
            Some("[cache]\nunknown = 1\n"),
            PathBuf::from("/tmp/default"),
        )
        .expect_err("unknown field should fail");
        assert_invalid_argument_contains(err, &["unknown"]);
    }

    #[test]
    fn toml_zero_max_size_returns_error() {
        let err = resolve_cache_config_from_parts(
            None,
            None,
            Some("[cache]\nmax_size = 0\n"),
            PathBuf::from("/tmp/default"),
        )
        .expect_err("zero max_size should fail");
        assert_invalid_argument_contains(err, &["max_size", "greater than 0"]);
    }

    #[test]
    fn toml_zero_max_age_returns_error() {
        let err = resolve_cache_config_from_parts(
            None,
            None,
            Some("[cache]\nmax_age_secs = 0\n"),
            PathBuf::from("/tmp/default"),
        )
        .expect_err("zero max_age should fail");
        assert_invalid_argument_contains(err, &["max_age_secs", "greater than 0"]);
    }

    #[test]
    fn blank_toml_dir_returns_error() {
        let err = resolve_cache_config_from_parts(
            None,
            None,
            Some("[cache]\ndir = \"   \"\n"),
            PathBuf::from("/tmp/default"),
        )
        .expect_err("blank dir should fail");
        assert_invalid_argument_contains(err, &["dir"]);
    }

    #[test]
    fn toml_without_cache_section_uses_defaults() {
        let default_root = PathBuf::from("/tmp/default-cache");
        let config = resolve_cache_config_from_parts(
            None,
            None,
            Some("# no [cache] section\n"),
            default_root.clone(),
        )
        .expect("missing [cache] should use defaults");
        assert_eq!(config, default_config_with_root(default_root));
    }

    #[test]
    fn blank_env_values_are_treated_as_unset() {
        let config = resolve_cache_config_from_parts(
            Some("   "),
            Some("   "),
            Some("[cache]\ndir = \"/file-cache\"\nmax_size = 42\n"),
            PathBuf::from("/tmp/default"),
        )
        .expect("blank env values should fall through");
        assert_eq!(config.cache_root, PathBuf::from("/file-cache"));
        assert_eq!(config.max_size, 42);
    }

    #[test]
    fn resolve_cache_config_uses_defaults_when_no_env_or_file() {
        let _lock = env_lock();
        let root = TempDirGuard::new("defaults");
        let cache_home = root.path().join("cache-home");
        let config_home = root.path().join("config-home");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_home).expect("create config home");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var("XDG_CONFIG_HOME", Some(&config_home.to_string_lossy()));
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", None);
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let config = resolve_cache_config().expect("defaults should resolve");
        assert_eq!(config, default_config_with_root(default_cache_root()));
    }

    #[test]
    fn resolve_cache_config_reads_cache_toml_from_xdg_config_home() {
        let _lock = env_lock();
        let root = TempDirGuard::new("toml");
        let cache_home = root.path().join("cache-home");
        let config_home = root.path().join("config-home");
        let config_dir = config_home.join("biomcp");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_dir).expect("create config dir");
        std::fs::write(
            config_dir.join("cache.toml"),
            format!(
                "[cache]\ndir = \"{}\"\nmax_size = 1234\nmax_age_secs = 7200\n",
                root.path().join("resolved-cache").display()
            ),
        )
        .expect("write cache.toml");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var("XDG_CONFIG_HOME", Some(&config_home.to_string_lossy()));
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", None);
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let config = resolve_cache_config().expect("toml should resolve");
        assert_eq!(config.cache_root, root.path().join("resolved-cache"));
        assert_eq!(config.max_size, 1_234);
        assert_eq!(config.max_age, Duration::from_secs(7_200));
        assert_eq!(
            config.origins,
            CacheConfigOrigins {
                cache_root: ConfigOrigin::File,
                max_size: ConfigOrigin::File,
                max_age: ConfigOrigin::File,
            }
        );
    }

    #[test]
    fn resolve_cache_config_env_overrides_file() {
        let _lock = env_lock();
        let root = TempDirGuard::new("env-overrides");
        let cache_home = root.path().join("cache-home");
        let config_home = root.path().join("config-home");
        let config_dir = config_home.join("biomcp");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_dir).expect("create config dir");
        std::fs::write(
            config_dir.join("cache.toml"),
            "[cache]\ndir = \"/file-cache\"\nmax_size = 1234\nmax_age_secs = 7200\n",
        )
        .expect("write cache.toml");
        let env_dir = root.path().join("env-cache");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var("XDG_CONFIG_HOME", Some(&config_home.to_string_lossy()));
        let _cache_dir = set_env_var(
            "BIOMCP_CACHE_DIR",
            Some(&format!("  {}  ", env_dir.display())),
        );
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", Some(" 5000 "));

        let config = resolve_cache_config().expect("env should override file");
        assert_eq!(config.cache_root, env_dir);
        assert_eq!(config.max_size, 5_000);
        assert_eq!(config.max_age, Duration::from_secs(7_200));
        assert_eq!(
            config.origins,
            CacheConfigOrigins {
                cache_root: ConfigOrigin::Env,
                max_size: ConfigOrigin::Env,
                max_age: ConfigOrigin::File,
            }
        );
    }

    #[test]
    fn resolve_cache_config_reports_path_on_failure() {
        let _lock = env_lock();
        let root = TempDirGuard::new("parse-error");
        let cache_home = root.path().join("cache-home");
        let config_home = root.path().join("config-home");
        let config_dir = config_home.join("biomcp");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_dir).expect("create config dir");
        let config_path = config_dir.join("cache.toml");
        std::fs::write(&config_path, "[cache\nmax_size = 1\n").expect("write invalid cache.toml");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var("XDG_CONFIG_HOME", Some(&config_home.to_string_lossy()));
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", None);
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let err = resolve_cache_config().expect_err("invalid file should fail");
        let message = err.to_string();
        assert!(
            message.contains(&*config_path.to_string_lossy()),
            "expected parse error to include config path, got: {message}"
        );
    }

    #[test]
    fn resolve_cache_config_reports_path_on_read_failure() {
        let _lock = env_lock();
        let root = TempDirGuard::new("read-error");
        let cache_home = root.path().join("cache-home");
        let config_home = root.path().join("config-home");
        let config_dir = config_home.join("biomcp");
        std::fs::create_dir_all(&cache_home).expect("create cache home");
        std::fs::create_dir_all(&config_dir).expect("create config dir");
        let config_path = config_dir.join("cache.toml");
        std::fs::create_dir_all(&config_path).expect("create directory at cache.toml path");
        let _cache_home = set_env_var("XDG_CACHE_HOME", Some(&cache_home.to_string_lossy()));
        let _config_home = set_env_var("XDG_CONFIG_HOME", Some(&config_home.to_string_lossy()));
        let _cache_dir = set_env_var("BIOMCP_CACHE_DIR", None);
        let _cache_size = set_env_var("BIOMCP_CACHE_MAX_SIZE", None);

        let err = resolve_cache_config().expect_err("directory at cache.toml path should fail");
        let message = err.to_string();
        assert!(matches!(err, BioMcpError::Io(_)));
        assert!(
            message.contains(&*config_path.to_string_lossy()),
            "expected read error to include config path, got: {message}"
        );
    }
}
