.PHONY: build test check run clean spec validate-skills test-contracts

build:
	cargo build --release

test:
	cargo test

test-contracts:
	uv sync --extra dev
	uv run pytest tests/ -v --mcp-cmd "biomcp serve"
	uv run mkdocs build --strict

check:
	cargo clippy -- -D warnings
	cargo fmt --check

run:
	cargo run --

clean:
	cargo clean

spec:
	XDG_CACHE_HOME="$(CURDIR)/.cache" PATH="$(CURDIR)/target/release:$(PATH)" \
		uv run --extra dev sh -c 'PATH="$(CURDIR)/target/release:$$PATH" pytest spec/ --mustmatch-lang bash --mustmatch-timeout 60 -v'

validate-skills:
	XDG_CACHE_HOME="$(CURDIR)/.cache" PATH="$(CURDIR)/target/release:$(PATH)" \
		uv run --extra dev sh -c 'PATH="$(CURDIR)/target/release:$$PATH" ./scripts/validate-skills.sh'
