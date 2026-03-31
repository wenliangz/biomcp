use anyhow::Context;

#[derive(Debug, Clone)]
pub struct DiscoverArgs {
    pub query: String,
}

pub async fn run(args: DiscoverArgs, json: bool) -> anyhow::Result<String> {
    let result = crate::entities::discover::resolve_query(
        &args.query,
        crate::entities::discover::DiscoverMode::Command,
    )
    .await
    .context("discover requires OLS4")?;

    if json {
        Ok(crate::render::json::to_discover_json(&result)?)
    } else {
        Ok(crate::render::markdown::render_discover(&result)?)
    }
}
