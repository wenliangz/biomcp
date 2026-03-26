use std::borrow::Cow;

use clap::Subcommand;
use rust_embed::RustEmbed;

use crate::error::BioMcpError;

#[derive(RustEmbed)]
#[folder = "docs/charts/"]
struct EmbeddedCharts;

#[derive(Subcommand, Debug, Clone, Copy, PartialEq, Eq)]
pub enum ChartCommand {
    Bar,
    StackedBar,
    Pie,
    Heatmap,
    Histogram,
    Density,
    Box,
    Violin,
    Ridgeline,
    Survival,
}

fn embedded_text(path: &str) -> Result<String, BioMcpError> {
    let Some(asset) = EmbeddedCharts::get(path) else {
        return Err(BioMcpError::NotFound {
            entity: "chart".into(),
            id: path.to_string(),
            suggestion: "Try: biomcp chart".into(),
        });
    };
    let bytes: Cow<'static, [u8]> = asset.data;
    String::from_utf8(bytes.into_owned())
        .map_err(|_| BioMcpError::InvalidArgument("Embedded chart doc is not valid UTF-8".into()))
}

pub fn show(command: Option<&ChartCommand>) -> Result<String, BioMcpError> {
    let path = match command {
        None => "index.md",
        Some(ChartCommand::Bar) => "bar.md",
        Some(ChartCommand::StackedBar) => "stacked-bar.md",
        Some(ChartCommand::Pie) => "pie.md",
        Some(ChartCommand::Heatmap) => "heatmap.md",
        Some(ChartCommand::Histogram) => "histogram.md",
        Some(ChartCommand::Density) => "density.md",
        Some(ChartCommand::Box) => "box.md",
        Some(ChartCommand::Violin) => "violin.md",
        Some(ChartCommand::Ridgeline) => "ridgeline.md",
        Some(ChartCommand::Survival) => "survival.md",
    };
    embedded_text(path)
}

#[cfg(test)]
mod tests {
    use super::{ChartCommand, show};

    #[test]
    fn show_returns_heatmap_doc() {
        let doc = show(Some(&ChartCommand::Heatmap)).expect("heatmap doc should exist");
        assert!(doc.contains("# Heatmap"));
        assert!(doc.contains("study co-occurrence --chart heatmap"));
    }

    #[test]
    fn show_returns_stacked_bar_doc() {
        let doc = show(Some(&ChartCommand::StackedBar)).expect("stacked-bar doc should exist");
        assert!(doc.contains("# Stacked Bar Chart"));
        assert!(doc.contains("study compare --type mutations --chart stacked-bar"));
    }
}
