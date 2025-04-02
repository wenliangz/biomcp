# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial `CONTRIBUTING.md` guide.
- Initial `CHANGELOG.md`.
- New `docs/installation.md` guide.
- New `docs/getting_started.md` guide.
- New `docs/server_protocol.md` explaining the `biomcp run` server and MCP usage.
- New `docs/python_sdk.md` documenting library usage with examples.

### Changed
- Revamped `docs/index.md` with more project details, installation steps, and documentation overview.
- Synchronized `docs/cli/*.md` (articles, trials, variants) with source code options and arguments.
- Improved structure and clarity of `docs/cli/trials.md` options list.
- Clarified/Removed ambiguous `--related-*` flags documentation in `docs/cli/variants.md` and `docs/workflows.md` pending code implementation.
- Added Python SDK example to `docs/workflows.md`.
- Added introductory sentences clarifying audience/purpose to `docs/apis/*.md`.
- Updated `docs/apis/myvariant_info.md` regarding default fields returned by search vs get.

### Fixed
- Ensured consistent documentation of the `--json` flag across CLI docs.

## [0.1.0] - YYYY-MM-DD (Example - Replace with actual first release)

### Added
- Initial release of BioMCP CLI and server.
- Support for searching ClinicalTrials.gov (`biomcp trial search`).
- Support for retrieving trial details (`biomcp trial get`).
- Support for searching PubMed/PubTator3 (`biomcp article search`).
- Support for retrieving article details (`biomcp article get`).
- Support for searching MyVariant.info (`biomcp variant search`).
- Support for retrieving variant details (`biomcp variant get`).
- Basic HTTP caching for API requests.
- Initial documentation structure.
